"""
git_archaeology.py — Git History Archaeology Scanner
Owner: Nikhil Virdi (NV)

Scans the full git commit history of changed files for secrets 
that were introduced in a past commit and subsequently 'deleted' 
from the latest version. The secret is still accessible in history.
"""

import re
import logging
import tempfile
import os

logger = logging.getLogger(__name__)

# Reuse the same secret patterns from secret_scanner
HISTORY_SECRET_PATTERNS = [
    ("OpenAI Key", r"(sk-proj-[a-zA-Z0-9_-]{20,})"),
    ("OpenAI Legacy Key", r"(sk-[a-zA-Z0-9]{32,})"),
    ("Anthropic Key", r"(sk-ant-[a-zA-Z0-9_-]{20,})"),
    ("Stripe Secret Key", r"(sk_live_[a-zA-Z0-9]{24,})"),
    ("Stripe Test Key", r"(sk_test_[a-zA-Z0-9]{24,})"),
    ("AWS Access Key", r"(AKIA[0-9A-Z]{16})"),
    ("GitHub Token", r"(ghp_[a-zA-Z0-9]{36})"),
    ("Private Key Header", r"(-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----)"),
    ("Database URL", r"((?:postgres|mysql|mongodb|redis)://[^\s'\"]+:[^\s'\"]+@[^\s'\"]+)"),
    ("Generic Secret", r"""(?i)((?:api[_-]?key|secret[_-]?key|auth[_-]?token)\s*[:=]\s*['"][a-zA-Z0-9_/+=\-]{20,}['"])"""),
]


class GitArchaeologyScanner:
    """
    Scans git commit history for deleted secrets.
    Uses GitPython to traverse the full log of changed files.
    """

    async def run(self, files: list[dict], repo_path: str = None) -> list[dict]:
        """
        Run git history scanning.
        
        If repo_path is provided and is a valid git repo, performs real history analysis.
        Otherwise, uses static analysis on the file patches to detect 
        deletion patterns (lines starting with '-' containing secrets).
        """
        findings = []

        # Strategy 1: Real git history analysis (when running against a cloned repo)
        if repo_path and os.path.isdir(os.path.join(repo_path, ".git")):
            findings = await self._scan_real_history(repo_path, files)
        
        # Strategy 2: Patch-based analysis (always available)
        patch_findings = self._scan_patches_for_removed_secrets(files)
        findings.extend(patch_findings)

        logger.info("GitArchaeologyScanner found %d historical secret exposures.", len(findings))
        return findings

    async def _scan_real_history(self, repo_path: str, files: list[dict]) -> list[dict]:
        """Scan actual git history using GitPython."""
        findings = []
        try:
            import git
            repo = git.Repo(repo_path)

            # Get the filenames we care about
            target_files = {f.get("filename", "") for f in files}

            # Walk through commits (limit to last 50 for performance)
            for commit in list(repo.iter_commits(max_count=50)):
                for blob in commit.tree.traverse():
                    if blob.path not in target_files:
                        continue

                    try:
                        content = blob.data_stream.read().decode("utf-8", errors="ignore")
                    except Exception:
                        continue

                    for secret_name, pattern in HISTORY_SECRET_PATTERNS:
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            # Check if this secret exists in the latest version
                            latest_file = next(
                                (f for f in files if f.get("filename") == blob.path), None
                            )
                            latest_content = latest_file.get("content", "") if latest_file else ""

                            if match.group(0) not in latest_content:
                                # Secret was in history but removed from latest — archaeology finding!
                                masked = match.group(0)[:12] + "..."

                                findings.append({
                                    "type": "GIT",
                                    "severity": "CRITICAL",
                                    "file": blob.path,
                                    "line": 0,
                                    "description": (
                                        f"{secret_name} found in commit {commit.hexsha[:8]} "
                                        f"(author: {commit.author.name}, date: {commit.committed_datetime.isoformat()}) "
                                        f"but deleted from the latest version. "
                                        f"The secret `{masked}` is still permanently accessible in git history. "
                                        "Anyone with read access to this repo can recover it."
                                    ),
                                    "fix_code": (
                                        f"# IMMEDIATELY rotate this credential!\n"
                                        f"# Then purge from git history:\n"
                                        f"git filter-repo --replace-text <(echo '{masked}==>***REDACTED***') --force\n"
                                        f"# Or use BFG Repo Cleaner:\n"
                                        f"bfg --replace-text passwords.txt\n"
                                        f"git reflog expire --expire=now --all && git gc --prune=now"
                                    ),
                                })

        except ImportError:
            logger.warning("GitPython not installed — skipping real history analysis.")
        except Exception as e:
            logger.error("Git history scan failed: %s", e)

        return findings

    def _scan_patches_for_removed_secrets(self, files: list[dict]) -> list[dict]:
        """
        Analyze PR patches for removed lines containing secrets.
        Lines starting with '-' in a patch indicate deleted content.
        If a secret appears in a deleted line, it was in a previous commit.
        """
        findings = []

        for file_info in files:
            filename = file_info.get("filename", "")
            patch = file_info.get("patch", "")

            if not patch:
                continue

            for line in patch.split("\n"):
                # Only look at removed lines (git diff format)
                if not line.startswith("-") or line.startswith("---"):
                    continue

                removed_content = line[1:]  # Strip the leading '-'

                for secret_name, pattern in HISTORY_SECRET_PATTERNS:
                    match = re.search(pattern, removed_content)
                    if match:
                        masked = match.group(0)[:12] + "..."

                        # Verify it's not in the added lines (still present)
                        added_lines = [
                            l[1:] for l in patch.split("\n")
                            if l.startswith("+") and not l.startswith("+++")
                        ]
                        still_present = any(match.group(0) in al for al in added_lines)

                        if not still_present:
                            findings.append({
                                "type": "GIT",
                                "severity": "CRITICAL",
                                "file": filename,
                                "line": 0,
                                "description": (
                                    f"{secret_name} (`{masked}`) was removed in this PR but exists in previous commits. "
                                    "Deleting a secret from the latest commit does NOT remove it from git history. "
                                    "The credential is permanently accessible to anyone with repo read access."
                                ),
                                "fix_code": (
                                    "# 1. IMMEDIATELY rotate this credential with the service provider!\n"
                                    "# 2. Purge from git history:\n"
                                    "pip install git-filter-repo\n"
                                    f"git filter-repo --replace-text <(echo '{masked}==>***REDACTED***') --force\n"
                                    "# 3. Force push all branches:\n"
                                    "git push --force --all"
                                ),
                            })

        return findings
