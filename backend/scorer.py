"""
scorer.py — Vibe Risk Score Calculator
Owner: Nikhil Virdi (NV)

Aggregates all scan findings into a single 0-100 score
representing the security risk introduced by the pull request.
Score is stored in DynamoDB per PR and surfaced on the dashboard.
"""

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


# ─── Severity Weights ─────────────────────────────────────
# From the blueprint: Critical=25, High=15, Medium=8, Low=3

SEVERITY_WEIGHTS = {
    "CRITICAL": 25,
    "HIGH": 15,
    "MEDIUM": 8,
    "LOW": 3,
}

# Thresholds for risk classification
RISK_LEVELS = {
    "SAFE": (0, 10),
    "LOW_RISK": (11, 30),
    "MODERATE": (31, 60),
    "HIGH_RISK": (61, 80),
    "CRITICAL_RISK": (81, 100),
}


class VibeRiskScorer:
    """Calculates and classifies the Vibe Risk Score."""

    @staticmethod
    def calculate_score(findings: list[dict]) -> int:
        """
        Score = min(100, sum(severity_weight for each finding))
        """
        total = sum(
            SEVERITY_WEIGHTS.get(f.get("severity", "LOW").upper(), 0)
            for f in findings
        )
        score = min(100, total)
        logger.info("Vibe Risk Score: %d (from %d findings)", score, len(findings))
        return score

    @staticmethod
    def get_risk_level(score: int) -> str:
        """Return a human-readable risk classification."""
        for level, (low, high) in RISK_LEVELS.items():
            if low <= score <= high:
                return level
        return "CRITICAL_RISK"

    @staticmethod
    def get_severity_summary(findings: list[dict]) -> dict:
        """
        Build a summary breakdown by severity.
        Returns: {"critical": int, "high": int, "medium": int, "low": int}
        """
        summary = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for f in findings:
            sev = f.get("severity", "LOW").lower()
            if sev in summary:
                summary[sev] += 1
        return summary

    @staticmethod
    def get_type_summary(findings: list[dict]) -> dict:
        """Build a summary breakdown by finding type."""
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
        auto_fix_pr_url: str | None = None,
    ) -> dict:
        """
        Build a complete scan result record for DynamoDB storage.
        Matches the frozen API schema exactly.
        """
        score = VibeRiskScorer.calculate_score(findings)
        severity_summary = VibeRiskScorer.get_severity_summary(findings)

        return {
            "repo_id": repo_id,
            "pr_number": pr_number,
            "vibe_risk_score": score,
            "risk_level": VibeRiskScorer.get_risk_level(score),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "findings_summary": severity_summary,
            "findings": findings,
            "total_findings": len(findings),
            "type_summary": VibeRiskScorer.get_type_summary(findings),
            "auto_fix_pr_url": auto_fix_pr_url,
        }

    @staticmethod
    def build_risk_badge(score: int) -> str:
        """Generate a markdown badge/emoji string for the PR comment."""
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
