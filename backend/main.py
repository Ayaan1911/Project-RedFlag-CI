"""
main.py — FastAPI Application & API Endpoints
Owner: Nikhil Virdi (NV)

Exposes the frozen API endpoints:
  GET /api/scans/{repo_id}
  GET /api/scans/{repo_id}/{pr_number}

Also handles the webhook POST endpoint for local testing.
In production, Lambda + API Gateway handles the webhook.
"""

import os
import json
import logging
import asyncio
from typing import Optional
from datetime import datetime, timezone

import boto3
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ─── App Init ──────────────────────────────────────────────

app = FastAPI(
    title="RedFlag CI API",
    description="AI-powered CI/CD security pipeline for vibe-coded repos.",
    version="1.0.0",
)

# CORS — allow frontend dashboard to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL", "http://localhost:5173"),
        "https://*.amplifyapp.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AWS clients
REGION = os.getenv("AWS_REGION", "ap-south-1")
TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "redflagci-scans")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "redflagci-reports")


def _get_dynamodb_table():
    """Get DynamoDB table resource."""
    dynamodb = boto3.resource("dynamodb", region_name=REGION)
    return dynamodb.Table(TABLE_NAME)


def _get_s3_client():
    """Get S3 client."""
    return boto3.client("s3", region_name=REGION)


# ─── Health Check ──────────────────────────────────────────

@app.get("/")
def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "RedFlag CI API",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ─── FROZEN API ENDPOINTS ─────────────────────────────────
# These are frozen at Hour 15. Do NOT change paths or response shapes.
# ES (Eshan Shukla) consumes these in /frontend/src/api/client.js


@app.get("/api/scans/{repo_id}")
async def get_repo_scans(repo_id: str):
    """
    Get all scans for a repository.
    
    Response: [
        {
            pr_number: int,
            vibe_risk_score: int,          // 0-100
            timestamp: str,                // ISO 8601
            findings_summary: {
                critical: int,
                high: int,
                medium: int,
                low: int
            },
            s3_report_key: str
        }
    ]
    """
    try:
        table = _get_dynamodb_table()

        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key("repo_id").eq(repo_id),
            ScanIndexForward=False,  # Most recent first
            Limit=50,
        )

        items = response.get("Items", [])

        scans = []
        for item in items:
            scans.append({
                "pr_number": int(item.get("pr_number", 0)),
                "vibe_risk_score": int(item.get("vibe_risk_score", 0)),
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
    
    Response: {
        pr_number: int,
        vibe_risk_score: int,
        timestamp: str,
        findings: [
            {
                type: str,       // 'SECRET' | 'PACKAGE' | 'SQL' | 'PROMPT' | 'IAC' | 'GIT'
                severity: str,   // 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'
                file: str,
                line: int,
                description: str,
                fix_code: str
            }
        ],
        auto_fix_pr_url: str | null
    }
    """
    try:
        # Fetch the full report from S3
        s3 = _get_s3_client()

        # List objects with the prefix to find the latest scan for this PR
        prefix = f"reports/{repo_id}/{pr_number}/"
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)

        if "Contents" not in response or not response["Contents"]:
            raise HTTPException(status_code=404, detail=f"No scan found for PR #{pr_number}")

        # Get the most recent report
        latest_key = sorted(response["Contents"], key=lambda x: x["LastModified"], reverse=True)[0]["Key"]

        obj = s3.get_object(Bucket=BUCKET_NAME, Key=latest_key)
        report = json.loads(obj["Body"].read().decode("utf-8"))

        # Return in the frozen schema format
        return {
            "pr_number": report.get("pr_number", pr_number),
            "vibe_risk_score": report.get("vibe_risk_score", 0),
            "timestamp": report.get("timestamp", ""),
            "findings": [
                {
                    "type": f.get("type", "UNKNOWN"),
                    "severity": f.get("severity", "LOW"),
                    "file": f.get("file", ""),
                    "line": f.get("line", 0),
                    "description": f.get("description", ""),
                    "fix_code": f.get("fix_code", ""),
                }
                for f in report.get("findings", [])
            ],
            "auto_fix_pr_url": report.get("auto_fix_pr_url"),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to fetch scan detail for PR #%d: %s", pr_number, e)
        raise HTTPException(status_code=500, detail=f"Failed to fetch scan detail: {str(e)}")


# ─── Webhook Endpoint (for local development) ─────────────

@app.post("/webhook")
async def receive_webhook(request: Request):
    """
    Receive GitHub webhook events for local development.
    In production, API Gateway invokes Lambda directly.
    """
    body = await request.json()

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

    # Run the scan pipeline asynchronously
    from backend.orchestrator import ScanOrchestrator
    orchestrator = ScanOrchestrator()
    result = await orchestrator.run_full_pipeline(pr_meta)

    return {
        "status": "completed",
        "vibe_risk_score": result.get("vibe_risk_score", 0),
        "total_findings": result.get("total_findings", 0),
    }


# ─── Local Development Entry Point ────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
