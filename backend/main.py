"""
main.py — FastAPI Application & API Endpoints v2
Owner: Nikhil Virdi (NV)

Frozen API endpoints with v2 response schema:
  GET /api/scans/{repo_id}
  GET /api/scans/{repo_id}/{pr_number}

v2 additions: multi-dimensional scores, compliance, cost, exploit, root cause
"""

import os
import json
import logging
import hmac
import hashlib
from datetime import datetime, timezone

import boto3
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from boto3.dynamodb.conditions import Key

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="RedFlag CI API",
    description="AI-powered CI/CD security pipeline for vibe-coded repos. 7 problem statements, 1 pipeline.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL", "http://localhost:5173"),
        "http://localhost:5173",
    ],
    allow_origin_regex=r"https://.*\.amplifyapp\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REGION = os.getenv("AWS_REGION", "ap-south-1")
TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "redflagci-scans")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "redflagci-reports-184574354000")


def _get_dynamodb_table():
    return boto3.resource("dynamodb", region_name=REGION).Table(TABLE_NAME)


def _get_s3_client():
    return boto3.client("s3", region_name=REGION)


def _verify_webhook_signature(payload_body: str, signature_header: str) -> bool:
    """
    Validate GitHub X-Hub-Signature-256 header against our webhook secret.
    Returns True if valid, False otherwise.
    """
    secret = os.getenv("WEBHOOK_SECRET", "")
    if not secret or not signature_header:
        logger.warning("Webhook secret or signature header missing — skipping verification in dev.")
        return True

    expected = "sha256=" + hmac.new(
        secret.encode("utf-8"),
        payload_body.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature_header)


# ─── Health Check ──────────────────────────────────────────

@app.get("/")
def health_check():
    return {
        "status": "ok",
        "service": "RedFlag CI API",
        "version": "2.0.0",
        "problems_covered": 7,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ─── FROZEN API ENDPOINTS (v2 schema) ─────────────────────

@app.get("/api/scans/{repo_id}")
async def get_repo_scans(repo_id: str):
    """
    Get all scans for a repository.
    v2: includes ai_confidence_score and code_reliability_score
    """
    try:
        table = _get_dynamodb_table()
        response = table.query(
            KeyConditionExpression=Key("repo_id").eq(repo_id),
            ScanIndexForward=False,
            Limit=50,
        )
        items = response.get("Items", [])

        scans = []
        for item in items:
            scans.append({
                "repo_id": repo_id,
                "repo_full_name": item.get("repo_full_name", repo_id),
                "pr_number": int(item.get("pr_number", 0)),
                "vibe_risk_score": int(item.get("vibe_risk_score", 0)),
                "ai_confidence_score": int(item.get("ai_confidence_score", 0)),
                "code_reliability_score": item.get("code_reliability_score", "LOW"),
                "timestamp": item.get("timestamp", ""),
                "findings_summary": {
                    "critical": int(item.get("findings_summary", {}).get("critical", 0)),
                    "high": int(item.get("findings_summary", {}).get("high", 0)),
                    "medium": int(item.get("findings_summary", {}).get("medium", 0)),
                    "low": int(item.get("findings_summary", {}).get("low", 0)),
                },
                "s3_report_key": f"reports/{repo_id}/{item.get('pr_number', 0)}/{item.get('timestamp', '')}.json",
            })

        return scans

    except Exception as e:
        logger.error("Failed to fetch scans for repo %s: %s", repo_id, e)
        raise HTTPException(status_code=500, detail=f"Failed to fetch scans: {str(e)}")


@app.get("/api/scans/{repo_id}/{pr_number}")
async def get_scan_detail(repo_id: str, pr_number: int):
    """
    Get detailed scan results for a specific PR.
    v2 schema: includes exploit_payload, root_cause, compliance, reputation, cost
    """
    try:
        s3 = _get_s3_client()
        prefix = f"reports/{repo_id}/{pr_number}/"
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)

        if "Contents" not in response or not response["Contents"]:
            raise HTTPException(status_code=404, detail=f"No scan found for PR #{pr_number}")

        latest_key = sorted(response["Contents"], key=lambda x: x["LastModified"], reverse=True)[0]["Key"]
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=latest_key)
        report = json.loads(obj["Body"].read().decode("utf-8"))

        # Build v2 response
        return {
            "repo_id": repo_id,
            "repo_full_name": report.get("repo_full_name", repo_id),
            "pr_number": report.get("pr_number", pr_number),
            "vibe_risk_score": report.get("vibe_risk_score", 0),
            "ai_confidence_score": report.get("ai_confidence_score", 0),
            "code_reliability_score": report.get("code_reliability_score", "LOW"),
            "timestamp": report.get("timestamp", ""),

            # Cost routing
            "bedrock_cost_usd": report.get("cost_summary", {}).get("bedrock_cost_usd", 0),
            "bedrock_cost_without_routing_usd": report.get("cost_summary", {}).get("bedrock_cost_without_routing_usd", 0),
            "cost_savings_pct": report.get("cost_summary", {}).get("cost_savings_pct", 0),

            # Findings with v2 fields
            "findings": [
                {
                    "type": f.get("type", "UNKNOWN"),
                    "severity": f.get("severity", "LOW"),
                    "file": f.get("file", ""),
                    "line": f.get("line", 0),
                    "description": f.get("description", ""),
                    "fix_code": f.get("fix_code", ""),

                    # v2: Exploit payload (CRITICAL only)
                    "exploit_payload": f.get("exploit_payload"),

                    # v2: Root cause
                    "root_cause": f.get("root_cause"),

                    # v2: Compliance
                    "compliance_violations": f.get("compliance_violations", []),
                    "audit_impact": f.get("audit_impact", ""),

                    # v2: Reputation (PACKAGE only)
                    "reputation": f.get("reputation"),

                    # v2: WAF + cost (IAC only, from MDA)
                    "waf_pillar": f.get("waf_pillar"),
                    "cost_impact": f.get("cost_impact"),
                }
                for f in report.get("findings", [])
            ],

            # Pipeline findings (separate array, from MDA)
            "pipeline_findings": report.get("pipeline_findings", []),

            "auto_fix_pr_url": report.get("auto_fix_pr_url"),

            # v2: Compliance summary
            "compliance_summary": report.get("compliance_summary", {
                "owasp_violations": [],
                "soc2_violations": [],
                "cis_violations": [],
                "audit_ready": True,
            }),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to fetch scan detail for PR #%d: %s", pr_number, e)
        raise HTTPException(status_code=500, detail=f"Failed to fetch scan detail: {str(e)}")


# ─── Webhook (local dev) ──────────────────────────────────

@app.post("/webhook")
async def receive_webhook(request: Request):
    raw_body = await request.body()
    signature = request.headers.get("x-hub-signature-256", request.headers.get("X-Hub-Signature-256", ""))

    if not _verify_webhook_signature(raw_body.decode("utf-8"), signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature.")

    body = json.loads(raw_body.decode("utf-8"))
    action = body.get("action", "")
    if action not in ("opened", "synchronize", "reopened"):
        return {"status": "ignored", "reason": f"Unsupported action: {action}"}

    pr = body.get("pull_request", {})
    repo = body.get("repository", {})

    pr_meta = {
        "action": action,
        "pr_number": pr.get("number"),
        "pr_title": pr.get("title", ""),
        "head_sha": pr.get("head", {}).get("sha", ""),
        "base_ref": pr.get("base", {}).get("ref", ""),
        "repo_full_name": repo.get("full_name", ""),
        "repo_id": str(repo.get("id", "")),
        "sender": body.get("sender", {}).get("login", ""),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    from backend.orchestrator import ScanOrchestrator
    orchestrator = ScanOrchestrator()
    result = await orchestrator.run_full_pipeline(pr_meta)

    return {
        "status": "completed",
        "vibe_risk_score": result.get("vibe_risk_score", 0),
        "total_findings": result.get("total_findings", 0),
        "cost_savings_pct": result.get("cost_savings_pct", 0),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
