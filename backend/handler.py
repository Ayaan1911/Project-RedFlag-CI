"""
handler.py — AWS Lambda Entry Point
Owner: Nikhil Virdi (NV)

Two modes:
  1. Lambda mode: Mangum wraps FastAPI for API Gateway events
  2. Direct mode: Raw Lambda handler for webhook-only invocations

Validates webhook signature, extracts PR metadata,
dispatches the scan pipeline, and tracks execution timing.
"""

import os
import json
import hmac
import hashlib
import logging
import asyncio
import time
from datetime import datetime, timezone

from mangum import Mangum
from backend.main import app

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ─── Mangum Adapter ───────────────────────────────────────
# This wraps the FastAPI app for API Gateway Lambda proxy integration.
# API Gateway routes (GET /api/scans/..., POST /webhook) all go through here.

mangum_handler = Mangum(app, lifespan="off")


def _verify_webhook_signature(payload_body: str, signature_header: str) -> bool:
    """
    Validate GitHub X-Hub-Signature-256 header against our webhook secret.
    Returns True if valid, False otherwise.
    """
    secret = os.getenv("WEBHOOK_SECRET", "")
    if not secret or not signature_header:
        logger.warning("Webhook secret or signature header missing — skipping verification in dev.")
        return True  # Allow in dev; enforce in production

    expected = "sha256=" + hmac.new(
        secret.encode("utf-8"),
        payload_body.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature_header)


def _build_pr_metadata(body: dict) -> dict | None:
    """Extract essential PR information from the webhook payload."""
    action = body.get("action", "")
    if action not in ("opened", "synchronize", "reopened"):
        logger.info("Ignoring PR action: %s", action)
        return None

    pr = body.get("pull_request", {})
    repo = body.get("repository", {})

    if not pr or not pr.get("number"):
        logger.warning("Webhook body missing pull_request data.")
        return None

    return {
        "action": action,
        "pr_number": pr.get("number"),
        "pr_title": pr.get("title", ""),
        "pr_url": pr.get("html_url", ""),
        "head_sha": pr.get("head", {}).get("sha", ""),
        "base_ref": pr.get("base", {}).get("ref", ""),
        "repo_full_name": repo.get("full_name", ""),
        "repo_id": str(repo.get("id", "")),
        "sender": body.get("sender", {}).get("login", ""),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    
    Routes:
      - If event has 'httpMethod' or 'requestContext' → API Gateway → use Mangum
      - If event has 'action' and 'pull_request' → Direct webhook invocation
    """
    start_time = time.time()
    logger.info("Lambda invoked at %s", datetime.now(timezone.utc).isoformat())

    # ─── Route 1: API Gateway proxy → Mangum handles it ───
    if "httpMethod" in event or "requestContext" in event:
        logger.info("Routing to Mangum (API Gateway proxy).")
        return mangum_handler(event, context)

    # ─── Route 2: Direct Lambda invocation (webhook payload) ─
    logger.info("Direct invocation — processing webhook event.")

    # 1. Extract raw body and signature
    raw_body = event.get("body", "")
    if isinstance(raw_body, dict):
        # Direct invocation: body is already a dict
        body = raw_body
        raw_body = json.dumps(raw_body)
    else:
        try:
            body = json.loads(raw_body)
        except json.JSONDecodeError:
            logger.error("Failed to parse webhook body as JSON.")
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid JSON body."}),
            }

    # 2. Validate webhook signature
    signature = ""
    headers = event.get("headers", {})
    if headers:
        signature = headers.get("x-hub-signature-256", headers.get("X-Hub-Signature-256", ""))

    if not _verify_webhook_signature(raw_body, signature):
        logger.error("Invalid webhook signature — rejecting request.")
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Invalid webhook signature."}),
        }

    # 3. Extract PR metadata
    pr_meta = _build_pr_metadata(body)
    if pr_meta is None:
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "ignored", "reason": "Non-PR or irrelevant action."}),
        }

    logger.info(
        "Processing PR #%d on %s (action=%s, sender=%s)",
        pr_meta["pr_number"],
        pr_meta["repo_full_name"],
        pr_meta["action"],
        pr_meta["sender"],
    )

    # 4. Run the scan pipeline
    try:
        from backend.orchestrator import ScanOrchestrator
        orchestrator = ScanOrchestrator()

        # Use existing event loop or create new one
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        scan_result = loop.run_until_complete(
            orchestrator.run_full_pipeline(pr_meta)
        )
    except Exception as e:
        logger.exception("Scan pipeline failed: %s", e)
        elapsed = time.time() - start_time
        logger.info("Pipeline failed after %.2f seconds.", elapsed)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Scan pipeline execution failed.",
                "detail": str(e),
                "elapsed_seconds": round(elapsed, 2),
            }),
        }

    # 5. Return success with timing
    elapsed = time.time() - start_time
    logger.info("Pipeline completed in %.2f seconds.", elapsed)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "status": "completed",
            "pr_number": pr_meta["pr_number"],
            "repo": pr_meta["repo_full_name"],
            "vibe_risk_score": scan_result.get("vibe_risk_score", 0),
            "findings_count": scan_result.get("total_findings", 0),
            "elapsed_seconds": round(elapsed, 2),
        }),
    }
