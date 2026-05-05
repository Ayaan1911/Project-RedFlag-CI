"""
storage_client.py — Supabase Storage Client (replaces S3)
Owner: Nikhil Virdi (NV)

Single unified interface for report storage in RedFlag CI.
Uses Supabase Storage — free tier available, no AWS required.
"""

import os
import json
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
BUCKET_NAME = "scan-reports"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def upload_report(repo_id: str, pr_number: int, report: dict) -> str:
    """
    Upload scan report JSON to Supabase Storage.
    Returns the public URL or empty string on failure.
    """
    try:
        path = f"{repo_id}/{pr_number}/report.json"
        data = json.dumps(report, default=str).encode("utf-8")
        supabase.storage.from_(BUCKET_NAME).upload(
            path, data, {"content-type": "application/json", "upsert": "true"}
        )
        url = supabase.storage.from_(BUCKET_NAME).get_public_url(path)
        return url
    except Exception as e:
        print(f"[STORAGE ERROR] upload_report: {e}")
        return ""


def download_report(repo_id: str, pr_number: int) -> dict:
    """
    Download and return scan report JSON from Supabase Storage.
    Returns empty dict on failure.
    """
    try:
        path = f"{repo_id}/{pr_number}/report.json"
        data = supabase.storage.from_(BUCKET_NAME).download(path)
        return json.loads(data)
    except Exception as e:
        print(f"[STORAGE ERROR] download_report: {e}")
        return {}
