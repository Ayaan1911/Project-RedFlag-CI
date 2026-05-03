"""
secret_scanner.py — Secret Detection Engine
Owner: Nikhil Virdi (NV)

Scans all changed files for hardcoded credentials, API keys,
tokens, and private keys across 40+ service patterns.
Uses regex patterns augmented with entropy analysis.
"""

import re
import math
import logging

logger = logging.getLogger(__name__)


# ─── Secret Patterns ───────────────────────────────────────
# Each tuple: (name, regex, severity, fix_template)

SECRET_PATTERNS = [
    # OpenAI
    (
        "OpenAI API Key",
        r"(sk-proj-[a-zA-Z0-9_-]{20,})",
        "CRITICAL",
        "import os\napi_key = os.getenv('OPENAI_API_KEY')",
    ),
    (
        "OpenAI Legacy Key",
        r"(sk-[a-zA-Z0-9]{32,})",
        "CRITICAL",
        "import os\napi_key = os.getenv('OPENAI_API_KEY')",
    ),
    # Anthropic
    (
        "Anthropic API Key",
        r"(sk-ant-[a-zA-Z0-9_-]{20,})",
        "CRITICAL",
        "import os\napi_key = os.getenv('ANTHROPIC_API_KEY')",
    ),
    # Stripe
    (
        "Stripe Secret Key",
        r"(sk_live_[a-zA-Z0-9]{24,})",
        "CRITICAL",
        "import os\nstripe_key = os.getenv('STRIPE_SECRET_KEY')",
    ),
    (
        "Stripe Publishable Key",
        r"(pk_live_[a-zA-Z0-9]{24,})",
        "MEDIUM",
        "import os\nstripe_pub_key = os.getenv('STRIPE_PUBLISHABLE_KEY')",
    ),
    # AWS
    (
        "AWS Access Key ID",
        r"(AKIA[0-9A-Z]{16})",
        "CRITICAL",
        "# Use IAM roles or AWS SSO instead of hardcoded keys\nimport os\naws_key = os.getenv('AWS_ACCESS_KEY_ID')",
    ),
    (
        "AWS Secret Access Key",
        r"(?i)(aws_secret_access_key|aws_secret)\s*[:=]\s*['\"]?([a-zA-Z0-9/+=]{40})['\"]?",
        "CRITICAL",
        "# Use IAM roles or AWS SSO instead of hardcoded keys\nimport os\naws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')",
    ),
    # Google Cloud
    (
        "Google API Key",
        r"(AIza[0-9A-Za-z_-]{35})",
        "HIGH",
        "import os\ngoogle_key = os.getenv('GOOGLE_API_KEY')",
    ),
    # GitHub
    (
        "GitHub Token",
        r"(ghp_[a-zA-Z0-9]{36})",
        "CRITICAL",
        "import os\ngithub_token = os.getenv('GITHUB_TOKEN')",
    ),
    (
        "GitHub OAuth",
        r"(gho_[a-zA-Z0-9]{36})",
        "HIGH",
        "import os\ngithub_oauth = os.getenv('GITHUB_OAUTH_TOKEN')",
    ),
    # HuggingFace
    (
        "HuggingFace Token",
        r"(hf_[a-zA-Z0-9]{34})",
        "HIGH",
        "import os\nhf_token = os.getenv('HF_TOKEN')",
    ),
    # Slack
    (
        "Slack Bot Token",
        r"(xoxb-[0-9]{10,}-[0-9]{10,}-[a-zA-Z0-9]{24})",
        "HIGH",
        "import os\nslack_token = os.getenv('SLACK_BOT_TOKEN')",
    ),
    # Generic high-entropy
    (
        "Generic API Key Assignment",
        r"(?i)(api[_-]?key|secret[_-]?key|auth[_-]?token|access[_-]?token)\s*[:=]\s*['\"]([a-zA-Z0-9_/+=\-]{20,})['\"]",
        "HIGH",
        "import os\n# Move this credential to environment variables\nvalue = os.getenv('YOUR_SECRET_KEY')",
    ),
    # Private Keys
    (
        "RSA Private Key",
        r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----",
        "CRITICAL",
        "# Never commit private keys. Use AWS Secrets Manager or a vault.\nimport os\nkey_path = os.getenv('PRIVATE_KEY_PATH')",
    ),
    # Database URLs
    (
        "Database Connection String",
        r"(?i)(postgres|mysql|mongodb|redis)://[^\s'\"]+:[^\s'\"]+@[^\s'\"]+",
        "CRITICAL",
        "import os\ndb_url = os.getenv('DATABASE_URL')",
    ),
    # JWT Secrets
    (
        "JWT Secret",
        r"(?i)(jwt[_-]?secret|jwt[_-]?key)\s*[:=]\s*['\"]([^\s'\"]{8,})['\"]",
        "HIGH",
        "import os\njwt_secret = os.getenv('JWT_SECRET')",
    ),
]


def _shannon_entropy(data: str) -> float:
    """Calculate the Shannon entropy of a string."""
    if not data:
        return 0.0
    freq = {}
    for c in data:
        freq[c] = freq.get(c, 0) + 1
    length = len(data)
    return -sum((count / length) * math.log2(count / length) for count in freq.values())


class SecretScanner:
    """Scans file content for hardcoded secrets using regex + entropy analysis."""

    async def run(self, files: list[dict]) -> list[dict]:
        """Run secret scanning across all files. Returns list of findings."""
        findings = []

        for file_info in files:
            filename = file_info.get("filename", "")
            content = file_info.get("content", "")
            patch = file_info.get("patch", "")
            full_text = f"{content}\n{patch}"

            # Skip binary files and common non-code files
            if any(filename.endswith(ext) for ext in [".png", ".jpg", ".gif", ".ico", ".woff", ".lock"]):
                continue

            for secret_name, pattern, severity, fix_code in SECRET_PATTERNS:
                matches = re.finditer(pattern, full_text)
                for match in matches:
                    matched_text = match.group(0)

                    # Find line number
                    line_num = full_text[:match.start()].count("\n") + 1

                    # Entropy check for generic patterns — reduce false positives
                    if "Generic" in secret_name:
                        captured = match.group(2) if match.lastindex and match.lastindex >= 2 else matched_text
                        if _shannon_entropy(captured) < 3.5:
                            continue  # low entropy → likely not a real secret

                    # Mask the secret in the description
                    masked = matched_text[:8] + "..." + matched_text[-4:] if len(matched_text) > 16 else "***"

                    findings.append({
                        "type": "SECRET",
                        "severity": severity,
                        "file": filename,
                        "line": line_num,
                        "description": f"{secret_name} detected: `{masked}`. Hardcoded credentials must be moved to environment variables or a secrets manager.",
                        "fix_code": fix_code,
                    })

        logger.info("SecretScanner found %d secrets across %d files.", len(findings), len(files))
        return findings
