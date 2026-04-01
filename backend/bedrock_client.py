"""
bedrock_client.py — Amazon Bedrock AI Integration
Owner: Nikhil Virdi (NV)

Wraps Amazon Bedrock (Claude Sonnet 4) for:
1. Fix code generation per finding type
2. LLM anti-pattern analysis (used by MDA's llm_antipattern.py)
3. Natural language finding descriptions
"""

import os
import json
import logging
import boto3

logger = logging.getLogger(__name__)


class BedrockClient:
    """Wrapper around Amazon Bedrock for AI-powered security analysis."""

    def __init__(self):
        self.region = os.getenv("AWS_REGION", "ap-south-1")
        self.model_id = os.getenv(
            "BEDROCK_MODEL_ID",
            "anthropic.claude-sonnet-4-20250514"
        )
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=self.region,
        )

    async def generate_fix(self, finding: dict, file_content: str = "") -> str:
        """
        Generate a fix patch for a specific finding using Claude.
        
        Args:
            finding: Dict with type, severity, file, line, description
            file_content: Full content of the vulnerable file (for context)
            
        Returns:
            String containing the fixed code snippet.
        """
        finding_type = finding.get("type", "UNKNOWN")
        prompt = self._build_fix_prompt(finding, file_content)

        try:
            response = self._invoke_model(prompt)
            return response.strip()
        except Exception as e:
            logger.error("Bedrock fix generation failed for %s: %s", finding_type, e)
            return finding.get("fix_code", "// Fix generation failed. Manual review required.")

    async def analyze_antipatterns(self, file_content: str, filename: str) -> list[dict]:
        """
        Analyze a file for LLM anti-patterns using Bedrock.
        Called by MDA's llm_antipattern.py scanner.
        
        Returns list of finding dicts.
        """
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
6. Hardcoded CORS origins that should be environment variables
7. Missing input validation on request bodies
8. Overly permissive error messages exposing internals

For each issue found, return a JSON array with objects containing:
- "type": "LLM_ANTIPATTERN"
- "severity": "HIGH" or "MEDIUM"
- "line": approximate line number
- "description": clear explanation of the vulnerability
- "fix_code": the corrected code snippet

Return ONLY the JSON array. If no issues found, return [].
"""

        try:
            response = self._invoke_model(prompt)
            # Parse Bedrock's response as JSON
            # Strip any markdown code fences
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = "\n".join(cleaned.split("\n")[1:-1])
            
            findings = json.loads(cleaned)
            # Add filename to each finding
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
            # Include surrounding context (limit to avoid token overflow)
            lines = file_content.split("\n")
            start = max(0, line - 10)
            end = min(len(lines), line + 10)
            context = "\n".join(f"{i+start+1}: {l}" for i, l in enumerate(lines[start:end]))
            base_prompt += f"\nCode context:\n```\n{context}\n```\n"

        type_specific = {
            "SECRET": "Replace the hardcoded credential with an environment variable lookup. Use os.getenv() for Python or process.env for JavaScript.",
            "PACKAGE": "Remove the hallucinated package and suggest the correct real package name if one exists.",
            "SQL": "Convert the string-concatenated query to a parameterized/prepared statement. Preserve the query logic.",
            "PROMPT": "Add input sanitization before the user input reaches the LLM. Create a sanitize_for_llm() wrapper function.",
            "IAC": "Apply least-privilege principles. Replace wildcard permissions with specific required actions. Make S3 buckets private.",
            "GIT": "Provide the git filter-repo command to purge the secret from history, and instructions to rotate the credential.",
            "LLM_ANTIPATTERN": "Fix the anti-pattern by applying security best practices: add auth middleware, restrict CORS, add rate limiting.",
        }

        base_prompt += f"\nSpecific instruction: {type_specific.get(finding_type, 'Generate a secure fix.')}\n"
        base_prompt += "\nReturn ONLY the corrected code. No explanations, no markdown."

        return base_prompt

    def _invoke_model(self, prompt: str) -> str:
        """Invoke the Bedrock model and return the response text."""
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "temperature": 0.1,  # Low temperature for deterministic fixes
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}],
                }
            ],
        }

        response = self.client.invoke_model(
            modelId=self.model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload),
        )

        response_body = json.loads(response["body"].read())
        return response_body.get("content", [{}])[0].get("text", "")
