"""
orchestrator.py — Scan Pipeline Orchestrator v2
Owner: Nikhil Virdi (NV)

Coordinates the full RedFlag CI v2 scan pipeline:
1. Fetch PR diff from GitHub
2. Run AI fingerprinting
3. Execute all scan engines in parallel via asyncio.gather
4. Enrich findings: exploit sim + root cause + compliance mapping
5. Score findings (multi-dimensional)
6. Generate AI fixes via Bedrock (routed)
7. Post PR comment
8. Store results in DynamoDB + S3
9. Trigger SNS alerts if score > 80

v2 additions: exploit simulation, root cause, compliance, reputation, router cost tracking
"""

import os
import json
import asyncio
import logging
import time
from datetime import datetime, timezone

import boto3

import backend.github_client as github_client
from backend.auto_fix_pr import create_fix_pr
from backend.github_client import get_pr_diff, post_pr_comment
from backend.fingerprint import AIFingerprinter
from backend.scorer import VibeRiskScorer
from backend.router import PromptRouter
from backend.bedrock_client import BedrockClient
from backend.compliance_mapper import ComplianceMapper
from backend.scanners.secret_scanner import SecretScanner
from backend.scanners.package_checker import PackageChecker
from backend.scanners.sql_scanner import SQLScanner
from backend.scanners.prompt_injection import PromptInjectionScanner
from backend.scanners.git_archaeology import GitArchaeologyScanner
from backend.scanners.iac_auditor import IACAuditor
from backend.scanners.llm_antipattern import LLMAntiPatternScanner
from backend.scanners.exploit_simulation import ExploitSimulator
from backend.scanners.root_cause import RootCauseExplainer
from backend.scanners.reputation_scorer import ReputationScorer

logger = logging.getLogger(__name__)

BEDROCK_FIX_TIMEOUT = 15
BEDROCK_TOTAL_TIMEOUT = 60
MAX_BEDROCK_FIXES = 10


class ScanOrchestrator:
    """
    Coordinates 9-layer scan execution using the Fork-Join pattern.
    v2: Adds exploit simulation, root cause, compliance, reputation, cost routing.
    """

    def __init__(self):
        # Core engines
        self.fingerprinter = AIFingerprinter()
        self.secret_scanner = SecretScanner()
        self.package_checker = PackageChecker()
        self.sql_scanner = SQLScanner()
        self.prompt_scanner = PromptInjectionScanner()
        self.git_scanner = GitArchaeologyScanner()
        self.iac_scanner = IACAuditor()
        self.llm_antipattern_scanner = LLMAntiPatternScanner()

        # v2 engines
        self.exploit_simulator = ExploitSimulator()
        self.root_cause_explainer = RootCauseExplainer()
        self.compliance_mapper = ComplianceMapper()
        self.reputation_scorer = ReputationScorer()

        # Bedrock + Router
        self.router = PromptRouter()
        self.bedrock = BedrockClient(router=self.router)

        # AWS services
        region = os.getenv("AWS_REGION", "ap-south-1")
        self.dynamodb = boto3.resource("dynamodb", region_name=region)
        self.s3 = boto3.client("s3", region_name=region)
        self.sns = boto3.client("sns", region_name=region)

        self.table_name = os.getenv("DYNAMODB_TABLE_NAME", "redflagci-scans")
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "redflagci-reports-184574354000")
        self.sns_topic_arn = os.getenv("SNS_TOPIC_ARN", "")

        self.metrics = {}

    async def run_full_pipeline(self, pr_meta: dict) -> dict:
        """Execute the complete v2 scan pipeline."""
        pipeline_start = time.time()
        self.router.reset()

        repo = pr_meta["repo_full_name"]
        pr_number = pr_meta["pr_number"]
        repo_id = pr_meta["repo_id"]

        logger.info("═══════════════════════════════════════════════════")
        logger.info("  RedFlag CI v2 — Starting scan for PR #%d on %s", pr_number, repo)
        logger.info("═══════════════════════════════════════════════════")

        # ─── Step 1: Fetch PR diff ─────────────────────────
        step_start = time.time()
        logger.info("[1/9] Fetching PR diff...")
        try:
            files = await get_pr_diff(repo, pr_number)
        except Exception as e:
            logger.error("Failed to fetch PR diff: %s", e)
            await self._post_error_comment(repo, pr_number, "Failed to fetch PR diff", str(e))
            return {"vibe_risk_score": 0, "total_findings": 0, "findings": [], "error": str(e)}

        self.metrics["fetch_diff_ms"] = round((time.time() - step_start) * 1000)

        if not files:
            logger.info("No changed files — nothing to scan.")
            await post_pr_comment(repo, pr_number,
                "✅ **RedFlag CI** — No changed files detected. Score: 0/100 | 0 findings")
            return {"vibe_risk_score": 0, "total_findings": 0, "findings": []}

        logger.info("Fetched %d files from PR #%d", len(files), pr_number)

        # ─── Step 2: AI Fingerprinting ─────────────────────
        step_start = time.time()
        logger.info("[2/9] Running AI fingerprinting...")
        fingerprint_findings = self.fingerprinter.analyze_files(files)
        ai_file_count = sum(1 for f in files if f.get("is_ai_generated"))
        self.metrics["fingerprint_ms"] = round((time.time() - step_start) * 1000)

        # ─── Step 3: Parallel scan execution ───────────────
        step_start = time.time()
        logger.info("[3/9] Launching 7 parallel scan engines...")

        scan_results = await asyncio.gather(
            self._timed_scan("secret_scanner", self.secret_scanner.run(files)),
            self._timed_scan("package_checker", self.package_checker.run(files)),
            self._timed_scan("sql_scanner", self.sql_scanner.run(files)),
            self._timed_scan("prompt_injection", self.prompt_scanner.run(files)),
            self._timed_scan("git_archaeology", self.git_scanner.run(files)),
            self._timed_scan("iac_auditor", self.iac_scanner.run(files)),
            self._timed_scan("llm_antipattern", self.llm_antipattern_scanner.run(files)),
            return_exceptions=True,
        )

        self.metrics["parallel_scan_ms"] = round((time.time() - step_start) * 1000)

        all_findings = list(fingerprint_findings)
        scanner_names = [
            "SecretScanner",
            "PackageChecker",
            "SQLScanner",
            "PromptInjection",
            "GitArchaeology",
            "IACAuditor",
            "LLMAntiPatternScanner",
        ]
        scanner_errors = []
        iac_findings = []
        llm_antipattern_findings = []

        for i, result in enumerate(scan_results):
            if isinstance(result, Exception):
                logger.error("  ✗ %s FAILED: %s", scanner_names[i], result)
                scanner_errors.append(f"{scanner_names[i]}: {result}")
            elif isinstance(result, list):
                all_findings.extend(result)
                if scanner_names[i] == "IACAuditor":
                    iac_findings = result
                elif scanner_names[i] == "LLMAntiPatternScanner":
                    llm_antipattern_findings = result
                logger.info("  ✓ %s → %d findings", scanner_names[i], len(result))

        # ─── Step 4: Compliance mapping (zero latency) ─────
        pipeline_findings = self._build_pipeline_findings(files)

        step_start = time.time()
        logger.info("[4/9] Mapping compliance controls...")
        for finding in all_findings:
            compliance = self.compliance_mapper.map_finding(finding)
            finding["compliance_violations"] = compliance["compliance_violations"]
            finding["audit_impact"] = compliance["audit_impact"]

        compliance_summary = self.compliance_mapper.build_compliance_summary(all_findings)
        self.metrics["compliance_ms"] = round((time.time() - step_start) * 1000)

        # ─── Step 5: Exploit simulation (CRITICAL only) ────
        step_start = time.time()
        logger.info("[5/9] Generating exploit payloads for CRITICAL findings...")
        critical_findings = [f for f in all_findings if f.get("severity") == "CRITICAL"]

        for finding in critical_findings[:5]:
            try:
                file_content = self._get_file_content(files, finding.get("file"))
                exploit = await asyncio.wait_for(
                    self.exploit_simulator.generate_exploit(finding, file_content, self.bedrock),
                    timeout=BEDROCK_FIX_TIMEOUT,
                )
                if exploit:
                    finding["exploit_payload"] = exploit
            except asyncio.TimeoutError:
                logger.warning("Exploit sim timed out for %s", finding.get("file"))
            except Exception as e:
                logger.warning("Exploit sim failed for %s: %s", finding.get("file"), e)

        self.metrics["exploit_sim_ms"] = round((time.time() - step_start) * 1000)

        # ─── Step 6: Root cause analysis (ALL findings) ────
        step_start = time.time()
        logger.info("[6/9] Generating root cause explanations...")
        for finding in all_findings:
            if finding.get("type") == "AI_FINGERPRINT":
                continue
            try:
                file_content = self._get_file_content(files, finding.get("file"))
                root_cause = await self.root_cause_explainer.explain(finding, file_content, self.bedrock)
                finding["root_cause"] = root_cause
            except Exception as e:
                logger.warning("Root cause failed for %s: %s", finding.get("file"), e)

        self.metrics["root_cause_ms"] = round((time.time() - step_start) * 1000)

        # ─── Step 7: Reputation scoring (packages) ────────
        step_start = time.time()
        logger.info("[7/9] Scoring package reputations...")
        package_findings = [f for f in all_findings if f.get("type") == "PACKAGE"]
        for finding in package_findings:
            pkg_name = self._extract_package_name(finding)
            if pkg_name:
                try:
                    rep = await self.reputation_scorer.score_npm_package(pkg_name)
                    finding["reputation"] = {
                        "trust_level": rep.get("trust_level", "UNKNOWN"),
                        "weekly_downloads": rep.get("weekly_downloads", 0),
                        "package_age_days": rep.get("package_age_days", 0),
                        "has_repository": rep.get("has_repository", False),
                    }
                except Exception as e:
                    logger.warning("Reputation scoring failed for %s: %s", pkg_name, e)

        self.metrics["reputation_ms"] = round((time.time() - step_start) * 1000)

        # ─── Step 8: Calculate scores (multi-dimensional) ──
        logger.info("[8/9] Calculating multi-dimensional scores...")
        score = VibeRiskScorer.calculate_score(all_findings)
        risk_level = VibeRiskScorer.get_risk_level(score)
        severity_summary = VibeRiskScorer.get_severity_summary(all_findings)
        ai_confidence = VibeRiskScorer.calculate_ai_confidence(files)
        reliability = VibeRiskScorer.calculate_reliability(all_findings, files)

        # ─── Step 9: Generate AI fixes (routed) ────────────
        step_start = time.time()
        logger.info("[9/9] Generating AI fixes via Bedrock (routed)...")
        critical_high = [f for f in all_findings if f.get("severity") in ("CRITICAL", "HIGH")]
        fix_count = 0

        for finding in critical_high[:MAX_BEDROCK_FIXES]:
            elapsed = time.time() - step_start
            if elapsed > BEDROCK_TOTAL_TIMEOUT:
                break
            try:
                file_content = self._get_file_content(files, finding.get("file"))
                ai_fix = await asyncio.wait_for(
                    self.bedrock.generate_fix(finding, file_content),
                    timeout=BEDROCK_FIX_TIMEOUT,
                )
                if ai_fix and "Manual review" not in ai_fix and len(ai_fix) > 10:
                    finding["fix_code"] = ai_fix
                    fix_count += 1
            except (asyncio.TimeoutError, Exception) as e:
                logger.warning("Fix gen skipped for %s: %s", finding.get("file"), e)

        self.metrics["bedrock_fixes_ms"] = round((time.time() - step_start) * 1000)

        # ─── Post PR Comment ──────────────────────────────
        auto_fix_pr_url = None
        fixable_finding = next((f for f in critical_high if f.get("fix_code")), None)
        if fixable_finding:
            auto_fix_pr_url = await create_fix_pr(repo, pr_number, fixable_finding, files, github_client)

        cost_summary = self.router.get_cost_summary()
        comment_body = self._build_pr_comment(
            pr_number, all_findings, score, risk_level, severity_summary,
            ai_file_count, len(files), scanner_errors,
            ai_confidence, reliability, cost_summary, compliance_summary,
        )
        await post_pr_comment(repo, pr_number, comment_body)

        # ─── Store results ────────────────────────────────
        scan_record = VibeRiskScorer.build_scan_record(
            repo_id, pr_number, all_findings, files,
            auto_fix_pr_url=auto_fix_pr_url,
            cost_summary=cost_summary,
            compliance_summary=compliance_summary,
        )
        scan_record["repo_full_name"] = repo
        scan_record["pipeline_findings"] = pipeline_findings
        scan_record["iac_findings"] = iac_findings
        scan_record["llm_antipattern_findings"] = llm_antipattern_findings
        scan_record["metrics"] = self.metrics
        await self._store_results(scan_record)

        # ─── Alert if critical ────────────────────────────
        if score > 80:
            await self._send_alert(repo, pr_number, score, severity_summary)

        total_ms = round((time.time() - pipeline_start) * 1000)
        self.metrics["total_pipeline_ms"] = total_ms
        logger.info("═══════════════════════════════════════════════════")
        logger.info("  Score: %d/100 (%s) | AI Confidence: %d%% | Reliability: %s",
                     score, risk_level, ai_confidence, reliability)
        logger.info("  Findings: %d | Cost: $%.4f (saved %d%%)",
                     len(all_findings), cost_summary.get("bedrock_cost_usd", 0),
                     cost_summary.get("cost_savings_pct", 0))
        logger.info("  Total time: %dms", total_ms)
        logger.info("═══════════════════════════════════════════════════")

        return {
            "vibe_risk_score": score,
            "risk_level": risk_level,
            "ai_confidence_score": ai_confidence,
            "code_reliability_score": reliability,
            "total_findings": len(all_findings),
            "findings_summary": severity_summary,
            "findings": all_findings,
            "pipeline_findings": pipeline_findings,
            "auto_fix_pr_url": auto_fix_pr_url,
            "repo_full_name": repo,
            "iac_findings": iac_findings,
            "llm_antipattern_findings": llm_antipattern_findings,
            "metrics": self.metrics,
            "bedrock_cost_usd": cost_summary.get("bedrock_cost_usd", 0),
            "bedrock_cost_without_routing_usd": cost_summary.get("bedrock_cost_without_routing_usd", 0),
            "cost_savings_pct": cost_summary.get("cost_savings_pct", 0),
            "compliance_summary": compliance_summary,
        }

    # ─── Helpers ──────────────────────────────────────────

    async def _timed_scan(self, name: str, coro) -> list[dict]:
        start = time.time()
        result = await coro
        self.metrics[f"{name}_ms"] = round((time.time() - start) * 1000)
        return result

    def _get_file_content(self, files: list[dict], filename: str) -> str:
        for f in files:
            if f.get("filename") == filename:
                return f.get("content", "")
        return ""

    def _extract_package_name(self, finding: dict) -> str | None:
        desc = finding.get("description", "")
        # Extract package name from description patterns like "Package `xyz` does not exist"
        if "`" in desc:
            parts = desc.split("`")
            if len(parts) >= 2:
                return parts[1]
        return None

    def _build_pipeline_findings(self, files: list[dict]) -> list[dict]:
        pipeline_paths = {
            ".gitlab-ci.yml": "GitLab CI pipeline config detected",
            "docker-compose.yml": "Docker Compose file detected",
            "jenkinsfile": "Jenkins pipeline file detected",
            "dockerfile": "Docker build file detected",
            ".circleci/config.yml": "CircleCI config detected",
        }

        findings = []
        for file_info in files:
            filename = file_info.get("filename", "")
            normalized = filename.lower()

            message = None
            if normalized.startswith(".github/workflows/") and normalized.endswith((".yml", ".yaml")):
                message = "GitHub Actions workflow detected"
            elif normalized in pipeline_paths:
                message = pipeline_paths[normalized]

            if message:
                findings.append({
                    "file": filename,
                    "issue_type": "pipeline_config_detected",
                    "severity": "info",
                    "message": message,
                })

        return findings

    def _build_pr_comment(
        self, pr_number, findings, score, risk_level, summary,
        ai_file_count, total_file_count, scanner_errors,
        ai_confidence, reliability, cost_summary, compliance_summary,
    ) -> str:
        badge = VibeRiskScorer.build_risk_badge(score)

        comment = f"""## 🚩 RedFlag CI v2 — Security Scan Report

{badge}

| Metric | Value |
|--------|-------|
| 🔐 Security Risk | **{score}/100** |
| 🤖 AI Confidence | **{ai_confidence}%** |
| 📊 Code Reliability | **{reliability}** |
| 💰 Scan Cost | **${cost_summary.get('bedrock_cost_usd', 0):.4f}** (saved {cost_summary.get('cost_savings_pct', 0)}% via routing) |

| Severity | Count |
|----------|-------|
| 🔴 Critical | {summary['critical']} |
| 🟠 High | {summary['high']} |
| 🟡 Medium | {summary['medium']} |
| 🟢 Low | {summary['low']} |

**Files Scanned:** {total_file_count} | **AI-Generated:** {ai_file_count} | **Total Findings:** {len(findings)}

"""
        # Compliance summary
        if compliance_summary and compliance_summary.get("total_controls_violated", 0) > 0:
            comment += f"""### 🛡️ Compliance Impact

| Framework | Violations |
|-----------|-----------|
| OWASP Top 10 | {', '.join(compliance_summary.get('owasp_violations', [])) or 'None'} |
| SOC 2 Type II | {', '.join(compliance_summary.get('soc2_violations', [])) or 'None'} |
| CIS Benchmarks | {', '.join(compliance_summary.get('cis_violations', [])) or 'None'} |
| OWASP LLM Top 10 | {', '.join(compliance_summary.get('llm_owasp_violations', [])) or 'None'} |

**Audit Ready:** {'✅ Yes' if compliance_summary.get('audit_ready') else '❌ No — ' + str(compliance_summary.get('total_controls_violated', 0)) + ' controls violated'}

---

"""

        # Findings grouped by severity
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

                # Compliance badges
                violations = f.get("compliance_violations", [])
                if violations:
                    badges = " ".join(f"`{v}`" for v in violations[:3])
                    comment += f" — {badges}"

                comment += "\n"
                comment += f"> {f.get('description', '')}\n"

                # Exploit payload (CRITICAL only)
                exploit = f.get("exploit_payload")
                if exploit:
                    comment += f"\n<details><summary>⚔️ Exploit Proof-of-Concept</summary>\n\n"
                    comment += f"**Payload:** `{exploit.get('payload', '')}`\n\n"
                    comment += f"**Impact:** {exploit.get('impact', '')}\n\n"
                    comment += f"```bash\n{exploit.get('curl_example', '')}\n```\n</details>\n"

                # Root cause
                root = f.get("root_cause")
                if root:
                    comment += f"\n<details><summary>🧠 Why AI Generated This</summary>\n\n"
                    comment += f"**Pattern:** {root.get('llm_behavioral_pattern', '')}\n\n"
                    comment += f"{root.get('why_llm_generated_this', '')}\n\n"
                    comment += f"**How to avoid:** {root.get('how_to_avoid', '')}\n</details>\n"

                # Fix code
                if f.get("fix_code"):
                    comment += f"\n<details><summary>💡 Suggested Fix</summary>\n\n```\n{f['fix_code']}\n```\n</details>\n"

                comment += "\n"

        # Scanner errors
        if scanner_errors:
            comment += "### ⚠️ Scanner Warnings\n\n"
            for err in scanner_errors:
                comment += f"- {err}\n"
            comment += "\n"

        # Performance
        comment += "<details><summary>📊 Scan Performance & Cost</summary>\n\n"
        comment += "| Engine | Time |\n|--------|------|\n"
        for key, value in self.metrics.items():
            if key.endswith("_ms"):
                name = key.replace("_ms", "").replace("_", " ").title()
                comment += f"| {name} | {value}ms |\n"
        comment += f"\n| Bedrock Calls | {cost_summary.get('total_calls', 0)} ({cost_summary.get('haiku_calls', 0)} Haiku + {cost_summary.get('sonnet_calls', 0)} Sonnet) |\n"
        comment += f"| Actual Cost | ${cost_summary.get('bedrock_cost_usd', 0):.4f} |\n"
        comment += f"| Without Routing | ${cost_summary.get('bedrock_cost_without_routing_usd', 0):.4f} |\n"
        comment += f"| Savings | {cost_summary.get('cost_savings_pct', 0)}% |\n"
        comment += "\n</details>\n\n"

        comment += """---

<sub>🤖 Powered by **RedFlag CI v2** — 7 problem statements. 1 pipeline. Your AI wrote the code. We check if it's safe to ship.</sub>
"""
        return comment

    async def _post_error_comment(self, repo, pr_number, title, detail):
        try:
            comment = (
                "## 🚩 RedFlag CI — Scan Error\n\n"
                f"⚠️ **{title}**\n\n> {detail}\n\n"
                "---\n<sub>🤖 Powered by **RedFlag CI**</sub>"
            )
            await post_pr_comment(repo, pr_number, comment)
        except Exception as e:
            logger.error("Failed to post error comment: %s", e)

    async def _store_results(self, scan_record):
        try:
            table = self.dynamodb.Table(self.table_name)
            dynamo_item = {
                "repo_id": scan_record["repo_id"],
                "sort_key": f"{scan_record['pr_number']}#{scan_record['timestamp']}",
                "pr_number": scan_record["pr_number"],
                "vibe_risk_score": scan_record["vibe_risk_score"],
                "risk_level": scan_record["risk_level"],
                "ai_confidence_score": scan_record.get("ai_confidence_score", 0),
                "code_reliability_score": scan_record.get("code_reliability_score", "LOW"),
                "repo_full_name": scan_record.get("repo_full_name", ""),
                "timestamp": scan_record["timestamp"],
                "findings_summary": scan_record["findings_summary"],
                "total_findings": scan_record["total_findings"],
            }
            table.put_item(Item=dynamo_item)
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
        except Exception as e:
            logger.error("S3 storage failed (non-fatal): %s", e)

    async def _send_alert(self, repo, pr_number, score, summary):
        if not self.sns_topic_arn:
            return
        try:
            message = (
                f"🚨 RedFlag CI Critical Alert\n\n"
                f"Repository: {repo}\nPR: #{pr_number}\n"
                f"Vibe Risk Score: {score}/100\n"
                f"Critical: {summary['critical']}, High: {summary['high']}\n"
                f"Time: {datetime.now(timezone.utc).isoformat()}"
            )
            self.sns.publish(
                TopicArn=self.sns_topic_arn,
                Subject=f"🚩 RedFlag CI: Score {score}/100 on {repo}",
                Message=message,
            )
        except Exception as e:
            logger.error("SNS alert failed (non-fatal): %s", e)
