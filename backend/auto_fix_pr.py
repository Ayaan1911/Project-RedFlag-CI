import logging

logger = logging.getLogger(__name__)

async def create_auto_fix_pr(repo_full_name: str, pr_number: int, findings: list, github_client) -> str | None:
    try:
        # 1. Filter findings where severity is "critical" or "high" (case insensitive)
        target_findings = [
            f for f in findings 
            if isinstance(f, dict) and f.get("severity", "").lower() in ("critical", "high") and f.get("fix_code")
        ]
        
        # 2. If no critical/high findings, return None
        if not target_findings:
            return None
            
        # 3. Call github_client.get_pr_diff(repo_full_name, pr_number) to get the current files
        files = await github_client.get_pr_diff(repo_full_name, pr_number)
        
        # 4. Create branch name
        branch_name = f"redflag/fix-{pr_number}"
        
        # 5. Get the base SHA from the first file's data
        if files:
            base_sha = files[0].get("sha", "main")
        else:
            base_sha = "main"
            
        # 6. Call create_branch
        await github_client.create_branch(repo_full_name, branch_name, base_sha)
        
        # 7. For each critical/high finding, call commit_file
        for finding in target_findings:
            filepath = finding.get("file")
            content = finding.get("fix_code")
            message = f"RedFlag CI: Fix {finding.get('severity')} - {finding.get('description', '')[:50]}"
            
            await github_client.commit_file(
                repo_full_name=repo_full_name,
                branch=branch_name,
                filepath=filepath,
                content=content,
                message=message
            )
            
        # 8. Call create_pull_request
        title = f"🚨 RedFlag CI — Auto Fix for PR #{pr_number}"
        
        body_lines = ["This is an automated pull request bringing critical security patches from RedFlag CI.\n"]
        body_lines.append("### Applied Fixes:")
        for f in target_findings:
            body_lines.append(f"- **[{f.get('severity', '').upper()}]** `{f.get('file')}:{f.get('line')}` - {f.get('description')}")
            
        body = "\n".join(body_lines)
        
        pr_url = await github_client.create_pull_request(
            repo_full_name=repo_full_name,
            title=title,
            body=body,
            head=branch_name,
            base="main"
        )
        
        # 9. Return the created PR URL
        return pr_url
        
    except Exception as e:
        # 10. Wrap everything in try/except — if anything fails, log the error and return None
        logger.error(f"RedFlag CI Auto-Fix failed for PR #{pr_number}: {e}")
        return None
