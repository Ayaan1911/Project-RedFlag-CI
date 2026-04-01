"""
scorer.py — Multi-Dimensional Vibe Score Calculator
Owner: Nikhil Virdi (NV)

Three scores computed per PR:
  1. security_risk_score (Vibe Risk Score) — 0-100 severity-weighted
  2. ai_confidence_score — 0-100 how sure we are it's AI-generated
  3. code_reliability_score — HIGH | MEDIUM | LOW
"""

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# ─── Severity Weights ─────────────────────────────────────

SEVERITY_WEIGHTS = {
    "CRITICAL": 25,
    "HIGH": 15,
    "MEDIUM": 8,
    "LOW": 3,
}

RISK_LEVELS = {
    "SAFE": (0, 10),
    "LOW_RISK": (11, 30),
    "MODERATE": (31, 60),
    "HIGH_RISK": (61, 80),
    "CRITICAL_RISK": (81, 100),
}


class VibeRiskScorer:
    """Calculates multi-dimensional Vibe scores."""

    # ─── Dimension 1: Security Risk Score ─────────────────

    @staticmethod
    def calculate_score(findings: list[dict]) -> int:
        """score = min(100, sum(severity_weight per finding))"""
        total = sum(
            SEVERITY_WEIGHTS.get(f.get("severity", "LOW").upper(), 0)
            for f in findings
        )
        score = min(100, total)
        logger.info("Vibe Risk Score: %d (from %d findings)", score, len(findings))
        return score

    @staticmethod
    def get_risk_level(score: int) -> str:
        for level, (low, high) in RISK_LEVELS.items():
            if low <= score <= high:
                return level
        return "CRITICAL_RISK"

    # ─── Dimension 2: AI Confidence Score ─────────────────

    @staticmethod
    def calculate_ai_confidence(files: list[dict]) -> int:
        """
        Returns 0-100 representing how confident we are that
        the code is AI-generated.
        
        Based on fingerprint.py results stored in file dicts.
        """
        if not files:
            return 0

        ai_count = sum(1 for f in files if f.get("is_ai_generated"))
        total = len(files)

        if total == 0:
            return 0

        return round((ai_count / total) * 100)

    # ─── Dimension 3: Code Reliability Score ──────────────

    @staticmethod
    def calculate_reliability(findings: list[dict], files: list[dict]) -> str:
        """
        Returns 'HIGH' | 'MEDIUM' | 'LOW' based on:
        - Number of critical findings
        - Test file presence
        - Complexity of issues
        """
        critical_count = sum(
            1 for f in findings if f.get("severity") == "CRITICAL"
        )
        high_count = sum(
            1 for f in findings if f.get("severity") == "HIGH"
        )

        # Check if tests exist in PR
        has_tests = any(
            "test" in f.get("filename", "").lower() or
            "spec" in f.get("filename", "").lower()
            for f in files
        )

        # Scoring logic
        score = 100
        score -= critical_count * 20
        score -= high_count * 10
        if not has_tests:
            score -= 15

        if score >= 70:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        else:
            return "LOW"

    # ─── Summary Builders ─────────────────────────────────

    @staticmethod
    def get_severity_summary(findings: list[dict]) -> dict:
        summary = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for f in findings:
            sev = f.get("severity", "LOW").lower()
            if sev in summary:
                summary[sev] += 1
        return summary

    @staticmethod
    def get_type_summary(findings: list[dict]) -> dict:
        summary = {}
        for f in findings:
            ftype = f.get("type", "UNKNOWN")
            summary[ftype] = summary.get(ftype, 0) + 1
        return summary

    @staticmethod
    def build_scan_record(
        repo_id: str,
        pr_number: int,
        findings: list[dict],
        files: list[dict] | None = None,
        auto_fix_pr_url: str | None = None,
        cost_summary: dict | None = None,
        compliance_summary: dict | None = None,
    ) -> dict:
        """Build a complete scan result record for DynamoDB."""
        score = VibeRiskScorer.calculate_score(findings)
        severity_summary = VibeRiskScorer.get_severity_summary(findings)
        ai_confidence = VibeRiskScorer.calculate_ai_confidence(files or [])
        reliability = VibeRiskScorer.calculate_reliability(findings, files or [])

        return {
            "repo_id": repo_id,
            "pr_number": pr_number,
            "vibe_risk_score": score,
            "risk_level": VibeRiskScorer.get_risk_level(score),
            "ai_confidence_score": ai_confidence,
            "code_reliability_score": reliability,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "findings_summary": severity_summary,
            "findings": findings,
            "total_findings": len(findings),
            "type_summary": VibeRiskScorer.get_type_summary(findings),
            "auto_fix_pr_url": auto_fix_pr_url,
            "cost_summary": cost_summary,
            "compliance_summary": compliance_summary,
        }

    @staticmethod
    def build_risk_badge(score: int) -> str:
        if score >= 81:
            return f"🔴 **CRITICAL RISK** — Score: {score}/100"
        elif score >= 61:
            return f"🟠 **HIGH RISK** — Score: {score}/100"
        elif score >= 31:
            return f"🟡 **MODERATE RISK** — Score: {score}/100"
        elif score >= 11:
            return f"🟢 **LOW RISK** — Score: {score}/100"
        else:
            return f"✅ **SAFE** — Score: {score}/100"
