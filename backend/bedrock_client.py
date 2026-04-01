"""
bedrock_client.py — Amazon Bedrock AI Integration (v2 — with Router)
Owner: Nikhil Virdi (NV)

Now integrates with router.py for intelligent model selection:
  - Simple tasks → Claude Haiku (10x cheaper, 3x faster)
  - Complex tasks → Claude Sonnet 4 (higher accuracy)

Tracks per-invocation costs via CostTracker.
"""

import os
import json
import logging
import boto3

from backend.router import PromptRouter

logger = logging.getLogger(__name__)


class BedrockClient:
    """Wrapper around Amazon Bedrock with intelligent routing."""

    def __init__(self, router: PromptRouter | None = None):
        self.region = os.getenv("AWS_REGION", "ap-south-1")
        self.default_model_id = os.getenv("BEDROCK_MODEL_ID", "claude-sonnet-4-20250514")
        self.router = router or PromptRouter()
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=self.region,
        )

    async def generate_fix(self, finding: dict, file_content: str = "", scan_type: str = "fix_generation") -> str:
        """Generate a fix patch for a specific finding using Claude."""
        prompt = self._build_fix_prompt(finding, file_content)

        try:
            model_id = self.router.get_model(scan_type)
            response = self._invoke_model(prompt, model_id=model_id, scan_type=scan_type)
            return response.strip()
        except Exception as e:
            logger.error("Bedrock fix generation failed for %s: %s", finding.get("type"), e)
            return finding.get("fix_code", "// Fix generation failed. Manual review required.")

    async def analyze_antipatterns(self, file_content: str, filename: str) -> list[dict]:
        """Analyze a file for LLM anti-patterns using Bedrock."""
        prompt = f"""You are an expert security engineer. Analyze the following AI-generated code file for common LLM anti-patterns and security issues.

File: {filename}

```
{file_content[:8000]}
```

Check for these specific anti-patterns that LLMs consistently generate:
1. CORS wildcard configuration (Access-Control-Allow-Origin: *)
2. Missing authentication middleware on API routes
3. Missing rate limiting on public endpoints
4. Exposed debug/development routes in production
5. Unvalidated file upload handlers
6. Missing input validation on request bodies
7. Overly permissive error messages exposing internals

For each issue found, return a JSON array with objects containing:
- "type": "LLM_ANTIPATTERN"
- "severity": "HIGH" or "MEDIUM"
- "line": approximate line number
- "description": clear explanation
- "fix_code": corrected code snippet

Return ONLY the JSON array. If no issues found, return [].
"""

        try:
            model_id = self.router.get_model("llm_antipattern")
            response = self._invoke_model(prompt, model_id=model_id, scan_type="llm_antipattern")
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = "\n".join(cleaned.split("\n")[1:-1])

            findings = json.loads(cleaned)
            for f in findings:
                f["file"] = filename
            return findings
        except (json.JSONDecodeError, Exception) as e:
            logger.error("Bedrock anti-pattern analysis failed for %s: %s", filename, e)
            return []

    def _build_fix_prompt(self, finding: dict, file_content: str) -> str:
        """Build a specialized fix generation prompt based on finding type."""
        finding_type = finding.get("type", "")
        description = finding.get("description", "")
        filename = finding.get("file", "")
        line = finding.get("line", 0)

        base_prompt = f"""You are an expert security engineer. Fix the following vulnerability.

Vulnerability Type: {finding_type}
Severity: {finding.get('severity', 'HIGH')}
File: {filename}
Line: {line}
Description: {description}
"""

        if file_content:
            lines = file_content.split("\n")
            start = max(0, line - 10)
            end = min(len(lines), line + 10)
            context = "\n".join(f"{i+start+1}: {l}" for i, l in enumerate(lines[start:end]))
            base_prompt += f"\nCode context:\n```\n{context}\n```\n"

        type_specific = {
            "SECRET": "Replace the hardcoded credential with an environment variable lookup.",
            "PACKAGE": "Remove the hallucinated package and suggest the correct real package.",
            "SQL": "Convert to a parameterized/prepared statement. Preserve query logic.",
            "PROMPT": "Add input sanitization before user input reaches the LLM.",
            "IAC": "Apply least-privilege. Replace wildcard permissions with specific actions.",
            "GIT": "Provide git filter-repo command to purge from history + rotation steps.",
            "LLM_ANTIPATTERN": "Fix the anti-pattern: add auth, restrict CORS, add rate limiting.",
            "PIPELINE": "Pin actions to SHAs, restrict permissions, add timeout-minutes.",
        }

        base_prompt += f"\nSpecific instruction: {type_specific.get(finding_type, 'Generate a secure fix.')}\n"
        base_prompt += "\nReturn ONLY the corrected code. No explanations, no markdown."

        return base_prompt

    def _invoke_model(self, prompt: str, model_id: str | None = None, scan_type: str = "unknown") -> str:
        """Invoke the Bedrock model and return the response text. Tracks costs via router."""
        target_model = model_id or self.default_model_id

        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "temperature": 0.1,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}],
                }
            ],
        }

        response = self.client.invoke_model(
            modelId=target_model,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload),
        )

        response_body = json.loads(response["body"].read())
        text = response_body.get("content", [{}])[0].get("text", "")

        # Track cost via router
        usage = response_body.get("usage", {})
        input_tokens = usage.get("input_tokens", len(prompt) // 4)
        output_tokens = usage.get("output_tokens", len(text) // 4)
        self.router.track_cost(scan_type, input_tokens, output_tokens)

        return text
