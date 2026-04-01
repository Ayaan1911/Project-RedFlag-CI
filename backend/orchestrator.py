"""
orchestrator.py — Scan Pipeline Orchestrator
Owner: Nikhil Virdi (NV)

Coordinates the full RedFlag CI scan pipeline:
1. Fetch PR diff from GitHub
2. Run AI fingerprinting
3. Execute all scan engines in parallel via asyncio.gather
4. Score findings
5. Generate AI fixes via Bedrock
6. Post PR comment
7. Store results in DynamoDB + S3
8. Trigger SNS alerts if score > 80
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timezone

import boto3

from backend.github_client import get_pr_diff, post_pr_comment
from backend.fingerprint import AIFingerprinter
from backend.scorer import VibeRiskScorer
from backend.bedrock_client import BedrockClient
from backend.scanners.secret_scanner import SecretScanner
from backend.scanners.package_checker import PackageChecker
from backend.scanners.sql_scanner import SQLScanner
from backend.scanners.prompt_injection import PromptInjectionScanner
from backend.scanners.git_archaeology import GitArchaeologyScanner

logger = logging.getLogger(__name__)


class ScanOrchestrator:
    """
    Coordinates 7-layer scan execution using the Fork-Join pattern.
    asyncio.gather forks all scanners in parallel, then joins results.
    """

    def __init__(self):
        # Initialize all scan engines
        self.fingerprinter = AIFingerprinter()
        self.secret_scanner = SecretScanner()
        self.package_checker = PackageChecker()
        self.sql_scanner = SQLScanner()
        self.prompt_scanner = PromptInjectionScanner()
        self.git_scanner = GitArchaeologyScanner()
        self.bedrock = BedrockClient()

        # AWS services
        self.dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "ap-south-1"))
        self.s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION", "ap-south-1"))
        self.sns = boto3.client("sns", region_name=os.getenv("AWS_REGION", "ap-south-1"))

        self.table_name = os.getenv("DYNAMODB_TABLE_NAME", "redflagci-scans")
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "redflagci-reports")
        self.sns_topic_arn = os.getenv("SNS_TOPIC_ARN", "")

    async def run_full_pipeline(self, pr_meta: dict) -> dict:
        """
        Execute the complete scan pipeline for a PR event.
        
        Args:
            pr_meta: Dict with repo_full_name, pr_number, repo_id, head_sha, etc.
            
        Returns:
            Dict with vibe_risk_score, total_findings, findings, etc.
        """
        repo = pr_meta["repo_full_name"]
        pr_number = pr_meta["pr_number"]
        repo_id = pr_meta["repo_id"]

        logger.info("═══ Starting RedFlag CI scan for PR #%d on %s ═══", pr_number, repo)

        # ─── Step 1: Fetch PR diff from GitHub ─────────────
        logger.info("[1/7] Fetching PR diff...")
        files = await get_pr_diff(repo, pr_number)

        if not files:
            logger.info("No changed files in PR — nothing to scan.")
            await post_pr_comment(repo, pr_number, "✅ **RedFlag CI** — No changed files detected. Nothing to scan.")
            return {"vibe_risk_score": 0, "total_findings": 0, "findings": []}

        logger.info("Fetched %d files from PR #%d", len(files), pr_number)

        # ─── Step 2: AI Fingerprinting ─────────────────────
        logger.info("[2/7] Running AI code fingerprinting...")
        fingerprint_findings = self.fingerprinter.analyze_files(files)
        ai_file_count = sum(1 for f in files if f.get("is_ai_generated"))
        logger.info("Fingerprinting: %d/%d files classified as AI-generated.", ai_file_count, len(files))

        # ─── Step 3: Parallel scan execution ───────────────
        logger.info("[3/7] Launching parallel scan engines...")
        scan_results = await asyncio.gather(
            self.secret_scanner.run(files),
            self.package_checker.run(files),
            self.sql_scanner.run(files),
            self.prompt_scanner.run(files),
            self.git_scanner.run(files),
            return_exceptions=True,
        )

        # Flatten results, handle errors
        all_findings = list(fingerprint_findings)  # Start with fingerprint findings
        scanner_names = ["SecretScanner", "PackageChecker", "SQLScanner", "PromptInjection", "GitArchaeology"]

        for i, result in enumerate(scan_results):
            if isinstance(result, Exception):
                logger.error("%s failed: %s", scanner_names[i], result)
            elif isinstance(result, list):
                all_findings.extend(result)
                logger.info("%s returned %d findings.", scanner_names[i], len(result))

        logger.info("[4/7] Total findings after parallel scan: %d", len(all_findings))

        # ─── Step 4: Calculate Vibe Risk Score ─────────────
        logger.info("[5/7] Calculating Vibe Risk Score...")
        score = VibeRiskScorer.calculate_score(all_findings)
        risk_level = VibeRiskScorer.get_risk_level(score)
        severity_summary = VibeRiskScorer.get_severity_summary(all_findings)

        # ─── Step 5: Generate AI fixes for Critical/High ───
        logger.info("[6/7] Generating AI fixes via Bedrock...")
        critical_high = [f for f in all_findings if f.get("severity") in ("CRITICAL", "HIGH")]
        for finding in critical_high[:10]:  # Limit to 10 to control Bedrock costs
            try:
                # Find the file content for context
                file_content = ""
                for f in files:
                    if f.get("filename") == finding.get("file"):
                        file_content = f.get("content", "")
                        break

                ai_fix = await self.bedrock.generate_fix(finding, file_content)
                if ai_fix and "Manual review" not in ai_fix:
                    finding["fix_code"] = ai_fix
            except Exception as e:
                logger.warning("Bedrock fix generation skipped for %s: %s", finding.get("file"), e)

        # ─── Step 6: Post PR Comment ──────────────────────
        comment_body = self._build_pr_comment(pr_number, all_findings, score, risk_level, severity_summary)
        await post_pr_comment(repo, pr_number, comment_body)

        # ─── Step 7: Store results ────────────────────────
        scan_record = VibeRiskScorer.build_scan_record(repo_id, pr_number, all_findings)
        await self._store_results(scan_record)

        # ─── Step 8: Alert if critical ────────────────────
        if score > 80:
            await self._send_alert(repo, pr_number, score, severity_summary)

        logger.info("═══ RedFlag CI scan complete. Score: %d (%s) ═══", score, risk_level)

        return {
            "vibe_risk_score": score,
            "risk_level": risk_level,
            "total_findings": len(all_findings),
            "findings_summary": severity_summary,
            "findings": all_findings,
        }

    def _build_pr_comment(
        self,
        pr_number: int,
        findings: list[dict],
        score: int,
        risk_level: str,
        summary: dict,
    ) -> str:
        """Build a structured PR comment with findings grouped by severity."""
        badge = VibeRiskScorer.build_risk_badge(score)

        comment = f"""## 🚩 RedFlag CI — Security Scan Report

{badge}

| Severity | Count |
|----------|-------|
| 🔴 Critical | {summary['critical']} |
| 🟠 High | {summary['high']} |
| 🟡 Medium | {summary['medium']} |
| 🟢 Low | {summary['low']} |

**Total Findings:** {len(findings)} | **AI-Generated Files Detected:** {sum(1 for f in findings if f.get('type') == 'AI_FINGERPRINT')}

---

"""
        # Group findings by severity
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            sev_findings = [f for f in findings if f.get("severity") == severity]
            if not sev_findings:
                continue

            emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}[severity]
            comment += f"### {emoji} {severity} Findings\n\n"

            for f in sev_findings:
                comment += f"**[{f.get('type', 'UNKNOWN')}]** `{f.get('file', 'unknown')}`"
                if f.get("line"):
                    comment += f" (line {f['line']})"
                comment += "\n"
                comment += f"> {f.get('description', '')}\n"

                if f.get("fix_code"):
                    comment += f"\n<details><summary>💡 Suggested Fix</summary>\n\n```\n{f['fix_code']}\n```\n</details>\n"

                comment += "\n"

        comment += """---

<sub>🤖 Powered by **RedFlag CI** — Your AI wrote the code. We check if it's safe to ship.</sub>
"""
        return comment

    async def _store_results(self, scan_record: dict) -> None:
        """Store scan results in DynamoDB and full report in S3."""
        try:
            # Store summary in DynamoDB
            table = self.dynamodb.Table(self.table_name)
            # DynamoDB doesn't accept float, convert score
            dynamo_item = {
                "repo_id": scan_record["repo_id"],
                "sort_key": f"{scan_record['pr_number']}#{scan_record['timestamp']}",
                "pr_number": scan_record["pr_number"],
                "vibe_risk_score": scan_record["vibe_risk_score"],
                "risk_level": scan_record["risk_level"],
                "timestamp": scan_record["timestamp"],
                "findings_summary": scan_record["findings_summary"],
                "total_findings": scan_record["total_findings"],
            }
            table.put_item(Item=dynamo_item)
            logger.info("Stored scan summary in DynamoDB.")
        except Exception as e:
            logger.error("DynamoDB storage failed: %s", e)

        try:
            # Store full report in S3
            s3_key = f"reports/{scan_record['repo_id']}/{scan_record['pr_number']}/{scan_record['timestamp']}.json"
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json.dumps(scan_record, default=str),
                ContentType="application/json",
            )
            logger.info("Stored full report in S3: %s", s3_key)
        except Exception as e:
            logger.error("S3 storage failed: %s", e)

    async def _send_alert(self, repo: str, pr_number: int, score: int, summary: dict) -> None:
        """Send SNS alert for critical risk scores."""
        if not self.sns_topic_arn:
            logger.warning("SNS_TOPIC_ARN not set — skipping alert.")
            return

        try:
            message = (
                f"🚨 RedFlag CI Critical Alert\n\n"
                f"Repository: {repo}\n"
                f"PR: #{pr_number}\n"
                f"Vibe Risk Score: {score}/100\n"
                f"Critical: {summary['critical']}, High: {summary['high']}, "
                f"Medium: {summary['medium']}, Low: {summary['low']}\n\n"
                f"Immediate review required."
            )
            self.sns.publish(
                TopicArn=self.sns_topic_arn,
                Subject=f"🚩 RedFlag CI Alert: Score {score}/100 on {repo}",
                Message=message,
            )
            logger.info("SNS critical alert sent for PR #%d", pr_number)
        except Exception as e:
            logger.error("SNS alert failed: %s", e)
