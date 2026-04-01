"""
handler.py — AWS Lambda Entry Point
Owner: Nikhil Virdi (NV)

Receives GitHub webhook POST events via API Gateway,
validates the signature, extracts PR metadata, and
dispatches the scan pipeline.
"""

import os
import json
import hmac
import hashlib
import logging
import asyncio
from datetime import datetime, timezone

logger = logging.getLogger()
logger.setLevel(logging.INFO)


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
    Called by API Gateway on every GitHub webhook delivery.
    """
    logger.info("Lambda invoked — processing webhook event.")

    # 1. Extract raw body and signature
    raw_body = event.get("body", "")
    if isinstance(raw_body, dict):
        raw_body = json.dumps(raw_body)

    signature = ""
    headers = event.get("headers", {})
    if headers:
        # API Gateway v2 lowercases headers
        signature = headers.get("x-hub-signature-256", headers.get("X-Hub-Signature-256", ""))

    # 2. Validate webhook signature
    if not _verify_webhook_signature(raw_body, signature):
        logger.error("Invalid webhook signature — rejecting request.")
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Invalid webhook signature."}),
        }

    # 3. Parse body
    try:
        body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
    except json.JSONDecodeError:
        logger.error("Failed to parse webhook body as JSON.")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON body."}),
        }

    # 4. Extract PR metadata
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

    # 5. Run the scan pipeline
    try:
        from backend.orchestrator import ScanOrchestrator
        orchestrator = ScanOrchestrator()
        scan_result = asyncio.get_event_loop().run_until_complete(
            orchestrator.run_full_pipeline(pr_meta)
        )
    except Exception as e:
        logger.exception("Scan pipeline failed: %s", e)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Scan pipeline execution failed.", "detail": str(e)}),
        }

    # 6. Return success
    return {
        "statusCode": 200,
        "body": json.dumps({
            "status": "completed",
            "pr_number": pr_meta["pr_number"],
            "repo": pr_meta["repo_full_name"],
            "vibe_risk_score": scan_result.get("vibe_risk_score", 0),
            "findings_count": scan_result.get("total_findings", 0),
        }),
    }
