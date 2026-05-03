import logging
import re
import time

logger = logging.getLogger(__name__)


def _sanitize_branch_suffix(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-").lower() or "fix"


def _apply_fix_to_content(content: str, finding: dict) -> str:
    """
    Apply the generated fix to the target file without replacing the whole file.
    For now we replace the vulnerable line with the generated fix snippet.
    """
    line_number = int(finding.get("line") or 1)
    fix_code = finding.get("fix_code", "").rstrip()
    if not fix_code:
        return content

    lines = content.splitlines()
    if not lines:
        return fix_code + "\n"

    target_index = max(0, min(len(lines) - 1, line_number - 1))
    replacement_lines = fix_code.splitlines()
    updated_lines = lines[:target_index] + replacement_lines + lines[target_index + 1 :]
    trailing_newline = "\n" if content.endswith("\n") else ""
    return "\n".join(updated_lines) + trailing_newline


async def create_fix_pr(
    repo_full_name: str,
    pr_number: int,
    finding: dict,
    files: list[dict],
    github_client,
) -> str | None:
    try:
        filepath = finding.get("file")
        if not filepath or not finding.get("fix_code"):
            return None

        file_entry = next((f for f in files if f.get("filename") == filepath), None)
        if not file_entry or not file_entry.get("sha"):
            logger.warning("Auto-fix skipped for %s: missing file sha from PR diff.", filepath)
            return None

        default_branch = await github_client.get_repo_default_branch(repo_full_name)
        base_sha = await github_client.get_branch_head_sha(repo_full_name, default_branch)

        finding_id = finding.get("id") or f"{filepath}-{finding.get('line', 0)}-{int(time.time())}"
        branch_name = f"redflag-fix/{pr_number}-{_sanitize_branch_suffix(str(finding_id))}"
        await github_client.create_branch(repo_full_name, branch_name, base_sha)

        current_file = await github_client.get_file_contents(repo_full_name, filepath, ref=default_branch)
        if not current_file or not current_file.get("sha"):
            logger.warning("Auto-fix skipped for %s: could not fetch current file contents.", filepath)
            return None

        if current_file["sha"] != file_entry["sha"]:
            logger.warning(
                "File sha changed for %s between PR diff and contents fetch (%s -> %s). Applying fix to latest branch content.",
                filepath,
                file_entry["sha"],
                current_file["sha"],
            )

        updated_content = _apply_fix_to_content(current_file.get("content", ""), finding)
        if updated_content == current_file.get("content", ""):
            logger.warning("Auto-fix made no changes for %s; skipping PR creation.", filepath)
            return None

        commit_message = f"RedFlag CI: fix {finding.get('severity', 'issue').lower()} in {filepath}"
        committed = await github_client.commit_file(
            repo_full_name=repo_full_name,
            branch=branch_name,
            filepath=filepath,
            content=updated_content,
            message=commit_message,
        )
        if not committed:
            return None

        title = f"RedFlag CI auto-fix for PR #{pr_number}: {filepath}"
        body = "\n".join([
            "This automated PR applies a RedFlag CI suggested fix.",
            "",
            f"- Severity: **{finding.get('severity', 'UNKNOWN')}**",
            f"- File: `{filepath}`",
            f"- Line: `{finding.get('line', 0)}`",
            f"- Description: {finding.get('description', '')}",
        ])

        return await github_client.create_pull_request(
            repo_full_name=repo_full_name,
            title=title,
            body=body,
            head=branch_name,
            base=default_branch,
        )

    except Exception as e:
        logger.error("RedFlag CI auto-fix failed for PR #%s: %s", pr_number, e)
        return None


async def create_auto_fix_pr(repo_full_name: str, pr_number: int, findings: list, github_client) -> str | None:
    """Backward-compatible wrapper for older callers."""
    target_finding = next(
        (
            f for f in findings
            if isinstance(f, dict)
            and f.get("severity", "").lower() in ("critical", "high")
            and f.get("fix_code")
        ),
        None,
    )
    if not target_finding:
        return None

    files = await github_client.get_pr_diff(repo_full_name, pr_number)
    return await create_fix_pr(repo_full_name, pr_number, target_finding, files, github_client)
