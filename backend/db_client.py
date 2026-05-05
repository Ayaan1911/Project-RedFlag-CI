"""
db_client.py — Supabase Database Client (replaces DynamoDB)
Owner: Nikhil Virdi (NV)

Single unified interface for all database operations in RedFlag CI.
Uses Supabase PostgreSQL — free tier available, no AWS required.
"""

import os
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def save_scan(scan_record: dict) -> dict:
    """Save a scan record to Supabase. Returns the inserted record."""
    try:
        result = supabase.table("scans").insert(scan_record).execute()
        return result.data[0] if result.data else {}
    except Exception as e:
        print(f"[DB ERROR] save_scan: {e}")
        return {}


def get_scans_by_repo(repo_id: str) -> list:
    """Get all scans for a repo, ordered by created_at desc."""
    try:
        result = (
            supabase.table("scans")
            .select("*")
            .eq("repo_id", repo_id)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or []
    except Exception as e:
        print(f"[DB ERROR] get_scans_by_repo: {e}")
        return []


def get_scan_by_pr(repo_id: str, pr_number: int) -> dict:
    """Get a specific scan by repo_id and pr_number."""
    try:
        result = (
            supabase.table("scans")
            .select("*")
            .eq("repo_id", repo_id)
            .eq("pr_number", pr_number)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else {}
    except Exception as e:
        print(f"[DB ERROR] get_scan_by_pr: {e}")
        return {}


def get_all_scans(limit: int = 50) -> list:
    """Get recent scans across all repos."""
    try:
        result = (
            supabase.table("scans")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []
    except Exception as e:
        print(f"[DB ERROR] get_all_scans: {e}")
        return []
