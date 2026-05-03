"""
root_cause.py — Root Cause Explainer (Problem 1.5 + 1.6 extension)
Owner: Nikhil Virdi (NV)

For every finding, explains WHY the LLM generated insecure code —
the behavioral reason, not just the technical description.

Converts RedFlag CI from a detection tool into a learning system.
"""

import json
import logging
import asyncio

logger = logging.getLogger(__name__)

# ─── Root Cause Prompt Template ──────────────────────────

ROOT_CAUSE_PROMPT = """You are an AI behavioral researcher specializing in LLM code generation patterns.

A security vulnerability was found in AI-generated code:

Vulnerability Type: {finding_type}
Severity: {severity}
File: {file}
Description: {description}

Vulnerable Code:
```
{vulnerable_code}
```

Explain WHY the LLM generated this insecure code — the behavioral reason, not just the technical description.

Return ONLY valid JSON with these fields:
{{
  "why_llm_generated_this": "1-2 sentence explanation of the LLM behavioral pattern that caused this",
  "llm_behavioral_pattern": "name of the pattern (e.g., 'Shortest-path optimization bias')",
  "developer_mistake": "what the developer should have caught",
  "how_to_avoid": "specific actionable advice (e.g., 'Add to .cursorrules: never use string concat for SQL')"
}}

Return ONLY JSON, no explanations, no markdown.
"""

# ─── Fallback Root Cause Templates ───────────────────────
# Used when Bedrock is unavailable or times out

FALLBACK_ROOT_CAUSES = {
    "SECRET": {
        "why_llm_generated_this": "LLMs reproduce patterns from training data where API keys are hardcoded in example code. They optimize for 'working code' not 'secure code' — env vars add complexity the model avoids.",
        "llm_behavioral_pattern": "Training data reproduction bias",
        "developer_mistake": "Accepted AI-generated code containing hardcoded credentials without security review",
        "how_to_avoid": "Add to .cursorrules: 'Never hardcode API keys. Always use environment variables via os.getenv() or process.env.'"
    },
    "SQL": {
        "why_llm_generated_this": "LLMs choose string concatenation because it satisfies the immediate requirement with the fewest tokens. Parameterized queries require importing libraries and restructuring the query — the model takes the shortest path.",
        "llm_behavioral_pattern": "Shortest-path optimization bias",
        "developer_mistake": "Trusted LLM output for database queries without verifying parameterization",
        "how_to_avoid": "Add to .cursorrules: 'All SQL queries MUST use parameterized statements. Never use string concatenation, f-strings, or template literals for SQL.'"
    },
    "PROMPT": {
        "why_llm_generated_this": "LLMs generate the most direct integration path — passing request.body directly to the messages array. Input sanitization is an 'extra step' that doesn't affect functionality, so the model omits it.",
        "llm_behavioral_pattern": "Functionality-first generation bias",
        "developer_mistake": "Did not add an input sanitization layer between user input and LLM API calls",
        "how_to_avoid": "Add to .cursorrules: 'All user input reaching LLM APIs must pass through a sanitize_for_llm() function that strips injection patterns and enforces length limits.'"
    },
    "PACKAGE": {
        "why_llm_generated_this": "LLMs hallucinate package names by combining real package name fragments into plausible-sounding but non-existent packages. The model generates 'openai-stream-helper' because both 'openai' and 'stream' exist in its training data.",
        "llm_behavioral_pattern": "Name hallucination via fragment recombination",
        "developer_mistake": "Did not verify that all dependencies exist in the package registry before installing",
        "how_to_avoid": "Run 'npm view <package>' or 'pip show <package>' for every AI-suggested dependency before adding to package.json or requirements.txt."
    },
    "GIT": {
        "why_llm_generated_this": "LLMs don't understand git history persistence. When asked to 'remove' a secret, they delete the line — but the secret remains in previous commits. The model treats files as current-state-only.",
        "llm_behavioral_pattern": "Stateless context assumption",
        "developer_mistake": "Assumed deleting a line removes the secret permanently. Git stores full history of every committed change.",
        "how_to_avoid": "After removing any secret: 1) Rotate the credential immediately 2) Use git-filter-repo to purge from history 3) Force-push all branches."
    },
    "IAC": {
        "why_llm_generated_this": "LLMs generate IaC that 'works' by using permissive defaults — public buckets, wildcard IAM, open security groups. Restrictive configurations require understanding the specific application architecture.",
        "llm_behavioral_pattern": "Permissive default bias",
        "developer_mistake": "Deployed AI-generated Terraform/CloudFormation without reviewing security posture",
        "how_to_avoid": "Add to .cursorrules: 'All S3 buckets must have BlockPublicAccess enabled. All IAM policies must specify exact actions — never use Effect:Allow, Action:*'"
    },
    "PIPELINE": {
        "why_llm_generated_this": "LLMs generate CI/CD workflows using `permissions: write-all` and unpinned action versions because these are the most common patterns in public repository examples.",
        "llm_behavioral_pattern": "Common-pattern replication bias",
        "developer_mistake": "Deployed AI-generated GitHub Actions workflow without reviewing permissions and action pinning",
        "how_to_avoid": "Pin all third-party actions to commit SHAs. Use least-privilege permissions. Add timeout-minutes to every job."
    },
}


class RootCauseExplainer:
    """Explains why LLMs generate insecure code — behavioral analysis."""

    async def explain(
        self,
        finding: dict,
        file_content: str = "",
        bedrock_client=None,
    ) -> dict:
        """
        Generate root cause explanation for a finding.
        
        Returns dict with: why_llm_generated_this, llm_behavioral_pattern,
        developer_mistake, how_to_avoid
        """
        finding_type = finding.get("type", "UNKNOWN")

        # Try Bedrock for specific analysis
        if bedrock_client and file_content:
            try:
                result = await self._explain_via_bedrock(finding, file_content, bedrock_client)
                if result:
                    return result
            except Exception as e:
                logger.warning("Bedrock root cause analysis failed: %s. Using fallback.", e)

        # Fallback to templates
        fallback = FALLBACK_ROOT_CAUSES.get(finding_type)
        if fallback:
            return dict(fallback)

        # Generic fallback
        return {
            "why_llm_generated_this": "LLMs optimize for working code over secure code, often omitting security best practices that don't affect core functionality.",
            "llm_behavioral_pattern": "Security-as-afterthought bias",
            "developer_mistake": "Accepted AI-generated code without security review",
            "how_to_avoid": "Always review AI-generated code for security issues before committing. Use RedFlag CI to automate this review."
        }

    async def _explain_via_bedrock(
        self,
        finding: dict,
        file_content: str,
        bedrock_client,
    ) -> dict | None:
        """Generate root cause via Bedrock AI."""
        line = finding.get("line", 0)
        lines = file_content.split("\n")
        start = max(0, line - 5)
        end = min(len(lines), line + 10)
        vulnerable_code = "\n".join(lines[start:end])

        prompt = ROOT_CAUSE_PROMPT.format(
            finding_type=finding.get("type", ""),
            severity=finding.get("severity", ""),
            file=finding.get("file", ""),
            description=finding.get("description", ""),
            vulnerable_code=vulnerable_code[:3000],
        )

        response = await asyncio.to_thread(bedrock_client._invoke_model, prompt)

        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = "\n".join(cleaned.split("\n")[1:-1])

        result = json.loads(cleaned)

        required = ["why_llm_generated_this", "llm_behavioral_pattern", "developer_mistake", "how_to_avoid"]
        if all(k in result for k in required):
            return result

        return None
