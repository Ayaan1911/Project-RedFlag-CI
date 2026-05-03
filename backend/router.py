"""
router.py — Intelligent Prompt Router (Problem 1.4)
Owner: Nikhil Virdi (NV)

Routes each Bedrock call to the optimal model:
  - Simple pattern-matching → Claude Haiku (10x cheaper, 3x faster)
  - Complex reasoning → Claude Sonnet 4 (higher accuracy)

Tracks cost per invocation for dashboard display.
"""

import os
import logging
import time
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# ─── Model Definitions ───────────────────────────────────

HAIKU_MODEL_ID = os.getenv("BEDROCK_HAIKU_MODEL_ID", "anthropic.claude-3-5-haiku-20241022")
SONNET_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "claude-sonnet-4-20250514")

# ─── Pricing (per 1K tokens, USD) ────────────────────────
# Source: AWS Bedrock pricing page

MODEL_PRICING = {
    HAIKU_MODEL_ID: {"input": 0.001, "output": 0.005},
    SONNET_MODEL_ID: {"input": 0.003, "output": 0.015},
}

# ─── Routing Map ─────────────────────────────────────────
# Simple tasks → Haiku | Complex reasoning → Sonnet

ROUTING_MAP = {
    # Pattern matching only — Haiku handles these fine
    "secret_scanner": HAIKU_MODEL_ID,
    "package_checker": HAIKU_MODEL_ID,
    "sql_scanner": HAIKU_MODEL_ID,
    "git_archaeology": HAIKU_MODEL_ID,
    "compliance_map": HAIKU_MODEL_ID,

    # Needs deep reasoning — Sonnet required
    "llm_antipattern": SONNET_MODEL_ID,
    "prompt_injection": SONNET_MODEL_ID,
    "iac_auditor": SONNET_MODEL_ID,
    "fix_generation": SONNET_MODEL_ID,
    "exploit_sim": SONNET_MODEL_ID,
    "root_cause": SONNET_MODEL_ID,
}


@dataclass
class CostTracker:
    """Tracks Bedrock invocation costs across a scan pipeline run."""
    total_cost_usd: float = 0.0
    total_cost_without_routing_usd: float = 0.0
    call_count: int = 0
    haiku_calls: int = 0
    sonnet_calls: int = 0
    call_log: list = field(default_factory=list)

    @property
    def cost_savings_pct(self) -> int:
        if self.total_cost_without_routing_usd == 0:
            return 0
        savings = 1 - (self.total_cost_usd / self.total_cost_without_routing_usd)
        return max(0, round(savings * 100))

    def to_dict(self) -> dict:
        return {
            "bedrock_cost_usd": round(self.total_cost_usd, 6),
            "bedrock_cost_without_routing_usd": round(self.total_cost_without_routing_usd, 6),
            "cost_savings_pct": self.cost_savings_pct,
            "total_calls": self.call_count,
            "haiku_calls": self.haiku_calls,
            "sonnet_calls": self.sonnet_calls,
        }


class PromptRouter:
    """Routes Bedrock calls to optimal model and tracks costs."""

    def __init__(self):
        self.cost_tracker = CostTracker()

    def get_model(self, scan_type: str) -> str:
        """Get the optimal model ID for a given scan type."""
        model = ROUTING_MAP.get(scan_type, SONNET_MODEL_ID)
        logger.debug("Router: %s → %s", scan_type, "Haiku" if model == HAIKU_MODEL_ID else "Sonnet")
        return model

    def track_cost(self, scan_type: str, input_tokens: int, output_tokens: int) -> float:
        """
        Track the cost of a Bedrock invocation.
        Returns the actual cost in USD.
        """
        actual_model = self.get_model(scan_type)
        actual_pricing = MODEL_PRICING.get(actual_model, MODEL_PRICING[SONNET_MODEL_ID])
        sonnet_pricing = MODEL_PRICING[SONNET_MODEL_ID]

        # Actual cost with routing
        actual_cost = (input_tokens / 1000 * actual_pricing["input"]) + \
                      (output_tokens / 1000 * actual_pricing["output"])

        # What it would cost if everything used Sonnet
        sonnet_cost = (input_tokens / 1000 * sonnet_pricing["input"]) + \
                      (output_tokens / 1000 * sonnet_pricing["output"])

        self.cost_tracker.total_cost_usd += actual_cost
        self.cost_tracker.total_cost_without_routing_usd += sonnet_cost
        self.cost_tracker.call_count += 1

        if actual_model == HAIKU_MODEL_ID:
            self.cost_tracker.haiku_calls += 1
        else:
            self.cost_tracker.sonnet_calls += 1

        self.cost_tracker.call_log.append({
            "scan_type": scan_type,
            "model": actual_model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": round(actual_cost, 6),
        })

        return actual_cost

    def get_cost_summary(self) -> dict:
        """Get the full cost tracking summary for API response."""
        return self.cost_tracker.to_dict()

    def reset(self):
        """Reset cost tracker for a new scan run."""
        self.cost_tracker = CostTracker()
