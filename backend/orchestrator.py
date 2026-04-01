"""
orchestrator.py — Scan Pipeline Orchestrator
Owner: Nikhil Virdi (NV)

Coordinates the full RedFlag CI scan pipeline:
1. Fetch PR diff from GitHub
2. Run AI fingerprinting
3. Execute all scan engines in parallel via asyncio.gather
4. Score findings
5. Generate AI fixes via Bedrock (with timeout)
6. Post PR comment
7. Store results in DynamoDB + S3
8. Trigger SNS alerts if score > 80

Performance: Tracks per-engine scan times and total pipeline duration.
Edge cases: Empty diffs, no findings, Bedrock timeouts, scanner failures.
"""

import os
import json
import asyncio
import logging
import time
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

# Bedrock fix generation timeout (per finding)
BEDROCK_FIX_TIMEOUT = 15  # seconds
# Total Bedrock budget for all fixes
BEDROCK_TOTAL_TIMEOUT = 60  # seconds
# Max findings to generate fixes for
MAX_BEDROCK_FIXES = 10


class ScanOrchestrator:
    """
    Coordinates 7-layer scan execution using the Fork-Join pattern.
    asyncio.gather forks all scanners in parallel, then joins results.
    Total scan time target: under 90 seconds.
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
        region = os.getenv("AWS_REGION", "ap-south-1")
        self.dynamodb = boto3.resource("dynamodb", region_name=region)
        self.s3 = boto3.client("s3", region_name=region)
        self.sns = boto3.client("sns", region_name=region)

        self.table_name = os.getenv("DYNAMODB_TABLE_NAME", "redflagci-scans")
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "redflagci-reports")
        self.sns_topic_arn = os.getenv("SNS_TOPIC_ARN", "")

        # Performance metrics
        self.metrics = {}

    async def run_full_pipeline(self, pr_meta: dict) -> dict:
        """
        Execute the complete scan pipeline for a PR event.

        Args:
            pr_meta: Dict with repo_full_name, pr_number, repo_id, head_sha, etc.

        Returns:
            Dict with vibe_risk_score, total_findings, findings, metrics, etc.
        """
        pipeline_start = time.time()
        repo = pr_meta["repo_full_name"]
        pr_number = pr_meta["pr_number"]
        repo_id = pr_meta["repo_id"]

        logger.info("═══════════════════════════════════════════════════")
        logger.info("  RedFlag CI — Starting scan for PR #%d on %s", pr_number, repo)
        logger.info("═══════════════════════════════════════════════════")

        # ─── Step 1: Fetch PR diff from GitHub ─────────────
        step_start = time.time()
        logger.info("[1/8] Fetching PR diff...")
        try:
            files = await get_pr_diff(repo, pr_number)
        except Exception as e:
            logger.error("Failed to fetch PR diff: %s", e)
            await self._post_error_comment(repo, pr_number, "Failed to fetch PR diff", str(e))
            return {"vibe_risk_score": 0, "total_findings": 0, "findings": [], "error": str(e)}

        self.metrics["fetch_diff_ms"] = round((time.time() - step_start) * 1000)

        # Edge case: Empty diff
        if not files:
            logger.info("No changed files in PR — nothing to scan.")
            await post_pr_comment(
                repo, pr_number,
                "✅ **RedFlag CI** — No changed files detected in this PR. Nothing to scan.\n\n"
                "<sub>Score: 0/100 | 0 findings</sub>"
            )
            return {"vibe_risk_score": 0, "total_findings": 0, "findings": []}

        logger.info("Fetched %d files from PR #%d", len(files), pr_number)

        # ─── Step 2: AI Fingerprinting ─────────────────────
        step_start = time.time()
        logger.info("[2/8] Running AI code fingerprinting...")
        fingerprint_findings = self.fingerprinter.analyze_files(files)
        ai_file_count = sum(1 for f in files if f.get("is_ai_generated"))
        self.metrics["fingerprint_ms"] = round((time.time() - step_start) * 1000)
        logger.info("  → %d/%d files classified as AI-generated (%dms)",
                     ai_file_count, len(files), self.metrics["fingerprint_ms"])

        # ─── Step 3: Parallel scan execution (Fork-Join) ──
        step_start = time.time()
        logger.info("[3/8] Launching 5 parallel scan engines...")

        scan_results = await asyncio.gather(
            self._timed_scan("secret_scanner", self.secret_scanner.run(files)),
            self._timed_scan("package_checker", self.package_checker.run(files)),
            self._timed_scan("sql_scanner", self.sql_scanner.run(files)),
            self._timed_scan("prompt_injection", self.prompt_scanner.run(files)),
            self._timed_scan("git_archaeology", self.git_scanner.run(files)),
            return_exceptions=True,
        )

        self.metrics["parallel_scan_ms"] = round((time.time() - step_start) * 1000)

        # Flatten results, handle scanner errors gracefully
        all_findings = list(fingerprint_findings)
        scanner_names = ["SecretScanner", "PackageChecker", "SQLScanner", "PromptInjection", "GitArchaeology"]
        scanner_errors = []

        for i, result in enumerate(scan_results):
            if isinstance(result, Exception):
                logger.error("  ✗ %s FAILED: %s", scanner_names[i], result)
                scanner_errors.append(f"{scanner_names[i]}: {result}")
            elif isinstance(result, list):
                all_findings.extend(result)
                logger.info("  ✓ %s → %d findings", scanner_names[i], len(result))

        logger.info("[4/8] Total findings after parallel scan: %d (in %dms)",
                     len(all_findings), self.metrics["parallel_scan_ms"])

        # ─── Step 4: Calculate Vibe Risk Score ─────────────
        logger.info("[5/8] Calculating Vibe Risk Score...")
        score = VibeRiskScorer.calculate_score(all_findings)
        risk_level = VibeRiskScorer.get_risk_level(score)
        severity_summary = VibeRiskScorer.get_severity_summary(all_findings)

        # Edge case: No vulnerabilities found (only fingerprint findings)
        real_findings = [f for f in all_findings if f.get("type") != "AI_FINGERPRINT"]
        if not real_findings:
            logger.info("No security vulnerabilities found — posting clean report.")
            await post_pr_comment(
                repo, pr_number,
                "## 🚩 RedFlag CI — Security Scan Report\n\n"
                "✅ **SAFE** — Score: 0/100\n\n"
                f"Scanned **{len(files)}** changed files across 5 security engines. "
                "No vulnerabilities detected.\n\n"
                f"{'🤖 ' + str(ai_file_count) + ' file(s) classified as AI-generated.' if ai_file_count else ''}\n\n"
                "---\n\n"
                "<sub>🤖 Powered by **RedFlag CI** — Your AI wrote the code. We check if it's safe to ship.</sub>"
            )
            # Still store the clean result
            scan_record = VibeRiskScorer.build_scan_record(repo_id, pr_number, all_findings)
            await self._store_results(scan_record)
            return {
                "vibe_risk_score": score,
                "risk_level": risk_level,
                "total_findings": len(all_findings),
                "findings_summary": severity_summary,
                "findings": all_findings,
            }

        # ─── Step 5: Generate AI fixes for Critical/High ───
        step_start = time.time()
        logger.info("[6/8] Generating AI fixes via Bedrock...")
        critical_high = [f for f in all_findings if f.get("severity") in ("CRITICAL", "HIGH")]
        bedrock_fix_count = 0
        bedrock_skip_count = 0

        for finding in critical_high[:MAX_BEDROCK_FIXES]:
            # Check total Bedrock time budget
            elapsed_bedrock = time.time() - step_start
            if elapsed_bedrock > BEDROCK_TOTAL_TIMEOUT:
                remaining = len(critical_high[:MAX_BEDROCK_FIXES]) - bedrock_fix_count - bedrock_skip_count
                logger.warning("Bedrock budget exhausted (%.1fs). Skipping %d remaining fixes.", elapsed_bedrock, remaining)
                break

            try:
                # Find file content for context
                file_content = ""
                for f in files:
                    if f.get("filename") == finding.get("file"):
                        file_content = f.get("content", "")
                        break

                # Timeout per individual fix
                ai_fix = await asyncio.wait_for(
                    self.bedrock.generate_fix(finding, file_content),
                    timeout=BEDROCK_FIX_TIMEOUT,
                )
                if ai_fix and "Manual review" not in ai_fix and len(ai_fix) > 10:
                    finding["fix_code"] = ai_fix
                    bedrock_fix_count += 1
                else:
                    bedrock_skip_count += 1
            except asyncio.TimeoutError:
                logger.warning("Bedrock timed out for %s (line %d). Using default fix.",
                             finding.get("file"), finding.get("line", 0))
                bedrock_skip_count += 1
            except Exception as e:
                logger.warning("Bedrock fix generation failed for %s: %s", finding.get("file"), e)
                bedrock_skip_count += 1

        self.metrics["bedrock_ms"] = round((time.time() - step_start) * 1000)
        logger.info("  → %d AI fixes generated, %d skipped (%dms)",
                     bedrock_fix_count, bedrock_skip_count, self.metrics["bedrock_ms"])

        # ─── Step 6: Post PR Comment ──────────────────────
        step_start = time.time()
        logger.info("[7/8] Posting PR comment...")
        comment_body = self._build_pr_comment(
            pr_number, all_findings, score, risk_level, severity_summary,
            ai_file_count, len(files), scanner_errors,
        )
        await post_pr_comment(repo, pr_number, comment_body)
        self.metrics["comment_ms"] = round((time.time() - step_start) * 1000)

        # ─── Step 7: Store results ────────────────────────
        step_start = time.time()
        logger.info("[8/8] Storing results in DynamoDB + S3...")
        scan_record = VibeRiskScorer.build_scan_record(repo_id, pr_number, all_findings)
        scan_record["metrics"] = self.metrics
        await self._store_results(scan_record)
        self.metrics["storage_ms"] = round((time.time() - step_start) * 1000)

        # ─── Step 8: Alert if critical ────────────────────
        if score > 80:
            await self._send_alert(repo, pr_number, score, severity_summary)

        # ─── Pipeline complete ────────────────────────────
        total_ms = round((time.time() - pipeline_start) * 1000)
        self.metrics["total_pipeline_ms"] = total_ms
        logger.info("═══════════════════════════════════════════════════")
        logger.info("  RedFlag CI scan complete!")
        logger.info("  Score: %d/100 (%s) | Findings: %d | Time: %dms", score, risk_level, len(all_findings), total_ms)
        logger.info("═══════════════════════════════════════════════════")

        return {
            "vibe_risk_score": score,
            "risk_level": risk_level,
            "total_findings": len(all_findings),
            "findings_summary": severity_summary,
            "findings": all_findings,
            "metrics": self.metrics,
        }

    async def _timed_scan(self, name: str, coro) -> list[dict]:
        """Wrapper to time individual scanner execution."""
        start = time.time()
        result = await coro
        elapsed = round((time.time() - start) * 1000)
        self.metrics[f"{name}_ms"] = elapsed
        return result

    def _build_pr_comment(
        self,
        pr_number: int,
        findings: list[dict],
        score: int,
        risk_level: str,
        summary: dict,
        ai_file_count: int,
        total_file_count: int,
        scanner_errors: list[str],
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

**Total Findings:** {len(findings)} | **Files Scanned:** {total_file_count} | **AI-Generated:** {ai_file_count}

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
                ftype = f.get("type", "UNKNOWN")
                fname = f.get("file", "unknown")
                fline = f.get("line", 0)

                comment += f"**[{ftype}]** `{fname}`"
                if fline:
                    comment += f" (line {fline})"
                comment += "\n"
                comment += f"> {f.get('description', '')}\n"

                if f.get("fix_code"):
                    comment += f"\n<details><summary>💡 Suggested Fix</summary>\n\n```\n{f['fix_code']}\n```\n</details>\n"

                comment += "\n"

        # Scanner error warnings
        if scanner_errors:
            comment += "### ⚠️ Scanner Warnings\n\n"
            for err in scanner_errors:
                comment += f"- {err}\n"
            comment += "\n"

        # Performance metrics
        comment += "<details><summary>📊 Scan Performance</summary>\n\n"
        comment += "| Engine | Time |\n|--------|------|\n"
        for key, value in self.metrics.items():
            if key.endswith("_ms"):
                name = key.replace("_ms", "").replace("_", " ").title()
                comment += f"| {name} | {value}ms |\n"
        comment += "\n</details>\n\n"

        comment += """---

<sub>🤖 Powered by **RedFlag CI** — Your AI wrote the code. We check if it's safe to ship.</sub>
"""
        return comment

    async def _post_error_comment(self, repo: str, pr_number: int, error_title: str, error_detail: str) -> None:
        """Post an error comment on the PR when the pipeline fails."""
        try:
            comment = (
                "## 🚩 RedFlag CI — Scan Error\n\n"
                f"⚠️ **{error_title}**\n\n"
                f"> {error_detail}\n\n"
                "The scan could not complete. Please check CloudWatch logs for details.\n\n"
                "---\n\n"
                "<sub>🤖 Powered by **RedFlag CI**</sub>"
            )
            await post_pr_comment(repo, pr_number, comment)
        except Exception as e:
            logger.error("Failed to post error comment: %s", e)

    async def _store_results(self, scan_record: dict) -> None:
        """Store scan results in DynamoDB and full report in S3."""
        try:
            table = self.dynamodb.Table(self.table_name)
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
            logger.error("DynamoDB storage failed (non-fatal): %s", e)

        try:
            s3_key = f"reports/{scan_record['repo_id']}/{scan_record['pr_number']}/{scan_record['timestamp']}.json"
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json.dumps(scan_record, default=str),
                ContentType="application/json",
            )
            logger.info("Stored full report in S3: %s", s3_key)
        except Exception as e:
            logger.error("S3 storage failed (non-fatal): %s", e)

    async def _send_alert(self, repo: str, pr_number: int, score: int, summary: dict) -> None:
        """Send SNS alert for critical risk scores (> 80)."""
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
                f"Immediate review required.\n"
                f"Time: {datetime.now(timezone.utc).isoformat()}"
            )
            self.sns.publish(
                TopicArn=self.sns_topic_arn,
                Subject=f"🚩 RedFlag CI Alert: Score {score}/100 on {repo}",
                Message=message,
            )
            logger.info("SNS critical alert sent for PR #%d", pr_number)
        except Exception as e:
            logger.error("SNS alert failed (non-fatal): %s", e)
