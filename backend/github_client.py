"""
github_client.py — PUBLIC INTERFACE (frozen at Hour 6, do not change signatures)
Owner: Nikhil Virdi (NV)
Consumer: Mohammad Ayaan (MDA) — auto_fix_pr.py

Full implementation of GitHub API operations using httpx.
Authenticates as a GitHub App using JWT + installation token.
"""

import os
import time
import json
import logging
import jwt
import httpx

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"


def _generate_jwt() -> str:
    """Generate a JWT for GitHub App authentication."""
    app_id = os.getenv("GITHUB_APP_ID")
    private_key_path = os.getenv("GITHUB_PRIVATE_KEY_PATH", "")

    # Attempt to read key from file path or directly from env var
    private_key = ""
    if private_key_path and os.path.exists(private_key_path):
        with open(private_key_path, "r") as f:
            private_key = f.read()
    else:
        private_key = os.getenv("GITHUB_PRIVATE_KEY", "")

    if not app_id or not private_key:
        raise ValueError("GITHUB_APP_ID and GITHUB_PRIVATE_KEY must be set.")

    now = int(time.time())
    payload = {
        "iat": now - 60,
        "exp": now + (10 * 60),
        "iss": app_id,
    }
    return jwt.encode(payload, private_key, algorithm="RS256")


async def _get_installation_token(repo_full_name: str) -> str:
    """Fetch an installation access token for the given repository."""
    jwt_token = _generate_jwt()
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    async with httpx.AsyncClient() as client:
        # Get installation ID for this repo
        resp = await client.get(
            f"{GITHUB_API_BASE}/repos/{repo_full_name}/installation",
            headers=headers,
        )
        resp.raise_for_status()
        installation_id = resp.json()["id"]

        # Create installation access token
        resp = await client.post(
            f"{GITHUB_API_BASE}/app/installations/{installation_id}/access_tokens",
            headers=headers,
        )
        resp.raise_for_status()
        return resp.json()["token"]


async def _get_headers(repo_full_name: str) -> dict:
    """Build authenticated headers for GitHub API calls."""
    token = await _get_installation_token(repo_full_name)
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


async def extract_code_snippet(file_content: str, line: int, context: int = 5) -> str:
    lines = file_content.split('\n')
    start = max(0, line - context - 1)
    end = min(len(lines), line + context)
    return '\n'.join(lines[start:end])

LANG_MAP = {
    ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".tf": "hcl", ".yml": "yaml", ".yaml": "yaml",
    ".java": "java", ".go": "go", ".rs": "rust"
}


# ─────────────────────────────────────────────
#  FROZEN PUBLIC INTERFACE — Do NOT change signatures
# ─────────────────────────────────────────────


async def get_pr_diff(repo_full_name: str, pr_number: int) -> list[dict]:
    """
    Fetch the files changed in a PR.
    Returns: [{'filename': str, 'content': str, 'patch': str}]
    """
    headers = await _get_headers(repo_full_name)

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Get list of files changed in the PR
        resp = await client.get(
            f"{GITHUB_API_BASE}/repos/{repo_full_name}/pulls/{pr_number}/files",
            headers=headers,
        )
        resp.raise_for_status()
        pr_files = resp.json()

        result = []
        for f in pr_files:
            filename = f.get("filename", "")
            patch = f.get("patch", "")
            raw_url = f.get("raw_url", "")

            # 2. Fetch full file content
            content = ""
            if raw_url:
                try:
                    content_resp = await client.get(raw_url, headers=headers)
                    if content_resp.status_code == 200:
                        content = content_resp.text
                except Exception as e:
                    logger.warning("Could not fetch content for %s: %s", filename, e)

            result.append({
                "filename": filename,
                "content": content,
                "patch": patch,
            })

        logger.info("Fetched %d files from PR #%d on %s", len(result), pr_number, repo_full_name)
        return result


async def post_pr_comment(repo_full_name: str, pr_number: int, body: str) -> bool:
    """
    Post a comment on a pull request.
    Returns: True if posted successfully.
    """
    headers = await _get_headers(repo_full_name)

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            f"{GITHUB_API_BASE}/repos/{repo_full_name}/issues/{pr_number}/comments",
            headers=headers,
            json={"body": body},
        )

        if resp.status_code in (200, 201):
            logger.info("Posted comment on PR #%d of %s", pr_number, repo_full_name)
            return True
        else:
            logger.error("Failed to post comment: %d %s", resp.status_code, resp.text)
            return False


async def create_branch(repo_full_name: str, branch_name: str, base_sha: str) -> str:
    """
    Create a new branch from a base SHA.
    Returns: new branch ref SHA.
    """
    headers = await _get_headers(repo_full_name)

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            f"{GITHUB_API_BASE}/repos/{repo_full_name}/git/refs",
            headers=headers,
            json={
                "ref": f"refs/heads/{branch_name}",
                "sha": base_sha,
            },
        )
        resp.raise_for_status()
        sha = resp.json()["object"]["sha"]
        logger.info("Created branch '%s' at SHA %s on %s", branch_name, sha, repo_full_name)
        return sha


async def commit_file(
    repo_full_name: str,
    branch: str,
    filepath: str,
    content: str,
    message: str,
) -> bool:
    """
    Create or update a file on a branch.
    Returns: True if committed successfully.
    """
    headers = await _get_headers(repo_full_name)

    async with httpx.AsyncClient(timeout=15.0) as client:
        # Check if file already exists to get its SHA (needed for update)
        existing_sha = None
        check_resp = await client.get(
            f"{GITHUB_API_BASE}/repos/{repo_full_name}/contents/{filepath}",
            headers=headers,
            params={"ref": branch},
        )
        if check_resp.status_code == 200:
            existing_sha = check_resp.json().get("sha")

        import base64
        encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

        payload = {
            "message": message,
            "content": encoded_content,
            "branch": branch,
        }
        if existing_sha:
            payload["sha"] = existing_sha

        resp = await client.put(
            f"{GITHUB_API_BASE}/repos/{repo_full_name}/contents/{filepath}",
            headers=headers,
            json=payload,
        )

        if resp.status_code in (200, 201):
            logger.info("Committed file '%s' to branch '%s'", filepath, branch)
            return True
        else:
            logger.error("Failed to commit file: %d %s", resp.status_code, resp.text)
            return False


async def create_pull_request(
    repo_full_name: str,
    title: str,
    body: str,
    head: str,
    base: str,
) -> str:
    """
    Open a new pull request.
    Returns: created PR URL string.
    """
    headers = await _get_headers(repo_full_name)

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            f"{GITHUB_API_BASE}/repos/{repo_full_name}/pulls",
            headers=headers,
            json={
                "title": title,
                "body": body,
                "head": head,
                "base": base,
            },
        )
        resp.raise_for_status()
        pr_url = resp.json()["html_url"]
        logger.info("Created PR: %s", pr_url)
        return pr_url
