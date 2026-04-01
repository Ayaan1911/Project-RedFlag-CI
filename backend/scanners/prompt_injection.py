"""
prompt_injection.py — Prompt Injection Vulnerability Scanner
Owner: Nikhil Virdi (NV)

Traces data flow from HTTP request parameters through application 
code to LLM API calls, flagging every route where raw user input 
reaches an LLM without sanitization.
"""

import re
import logging

logger = logging.getLogger(__name__)


# ─── LLM SDK Call Sites ────────────────────────────────────
# Patterns that identify where LLM APIs are invoked in code

LLM_CALL_PATTERNS = [
    # OpenAI
    r"openai\.chat\.completions\.create",
    r"openai\.ChatCompletion\.create",
    r"client\.chat\.completions\.create",
    # Anthropic
    r"anthropic\.messages\.create",
    r"client\.messages\.create",
    # AWS Bedrock
    r"bedrock[\w_]*\.invoke_model",
    r"bedrock_runtime\.invoke_model",
    # Generic patterns
    r"\.create\(\s*.*messages\s*[:=]",
    r"\.invoke_model\(",
    r"\.generate\(\s*.*prompt\s*[:=]",
]

# ─── Unsanitized Input Sources ─────────────────────────────
# These represent user-controlled data entering the system

INPUT_SOURCE_PATTERNS = [
    # Express.js / Node.js
    r"req\.body\.\w+",
    r"req\.query\.\w+",
    r"req\.params\.\w+",
    r"request\.body\.\w+",
    # Python Flask/FastAPI
    r"request\.json\[?",
    r"request\.form\[?",
    r"request\.args\[?",
    r"request\.data",
    # Generic
    r"user[_]?input",
    r"user[_]?message",
    r"prompt\s*=\s*.*input",
]

# ─── Dangerous Patterns ───────────────────────────────────
# Direct piping of user input into LLM message arrays

DANGEROUS_PATTERNS = [
    # Direct content mapping
    (
        r"""content\s*:\s*(req\.body\.\w+|request\.\w+|user_?input|user_?message|message)""",
        "User input mapped directly to LLM message 'content' field without sanitization.",
    ),
    # f-string in messages
    (
        r"""content\s*:\s*f['"].*\{(req\.body|request|user_?input|message)""",
        "User input interpolated via f-string directly into LLM prompt content.",
    ),
    # Template literal in messages
    (
        r"""content\s*:\s*`.*\$\{(req\.body|request|user_?input|message)""",
        "User input interpolated via template literal directly into LLM prompt.",
    ),
    # String concatenation in messages
    (
        r"""content\s*:.*\+\s*(req\.body|request\.\w+|user_?input|message)""",
        "User input concatenated directly into LLM prompt string.",
    ),
    # role: 'user' with unsanitized content
    (
        r"""role\s*:\s*['"]user['"]\s*,\s*content\s*:\s*(req\.|request\.|input|message)""",
        "Unsanitized input passed as user role message to LLM — vulnerable to prompt injection.",
    ),
    # System prompt override
    (
        r"""role\s*:\s*['"]system['"]\s*,\s*content\s*:.*\+.*(req\.|request\.|input|body)""",
        "User input reaches system prompt — critical prompt injection vulnerability allowing full system prompt override.",
    ),
]


class PromptInjectionScanner:
    """Detects prompt injection vulnerabilities by tracing user input to LLM calls."""

    async def run(self, files: list[dict]) -> list[dict]:
        """Run prompt injection detection across all files."""
        findings = []

        for file_info in files:
            filename = file_info.get("filename", "")
            content = file_info.get("content", "")
            patch = file_info.get("patch", "")

            # Only scan code files
            if not any(filename.endswith(ext) for ext in [".js", ".ts", ".py", ".rb", ".java"]):
                continue

            full_text = f"{content}\n{patch}"
            lines = full_text.split("\n")

            # Step 1: Check if file contains LLM API calls
            has_llm_call = any(
                re.search(p, full_text, re.IGNORECASE) for p in LLM_CALL_PATTERNS
            )
            if not has_llm_call:
                continue

            # Step 2: Check if file has user input sources
            has_user_input = any(
                re.search(p, full_text, re.IGNORECASE) for p in INPUT_SOURCE_PATTERNS
            )
            if not has_user_input:
                continue

            # Step 3: Check for dangerous direct piping patterns
            for i, line in enumerate(lines, 1):
                for pattern, description in DANGEROUS_PATTERNS:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        input_var = match.group(1) if match.lastindex else "user_input"

                        # Determine severity based on attack type
                        severity = "CRITICAL" if "system" in description.lower() else "HIGH"

                        findings.append({
                            "type": "PROMPT",
                            "severity": severity,
                            "file": filename,
                            "line": i,
                            "description": (
                                f"{description} "
                                f"Input variable: `{input_var}`. "
                                "An attacker can craft input that overrides system instructions, "
                                "extracts training data, or manipulates LLM behavior."
                            ),
                            "fix_code": _generate_fix(input_var, filename),
                        })

        logger.info("PromptInjectionScanner found %d prompt injection vulnerabilities.", len(findings))
        return findings


def _generate_fix(input_var: str, filename: str) -> str:
    """Generate a safe wrapper fix based on file type."""
    if filename.endswith((".js", ".ts")):
        return f"""// Sanitize user input before passing to LLM
function sanitizeForLLM(input) {{
  // Strip known injection patterns
  const stripped = input
    .replace(/ignore\\s+(previous|above|all)\\s+instructions/gi, '')
    .replace(/you\\s+are\\s+now/gi, '')
    .replace(/system\\s*:/gi, '')
    .slice(0, 4000); // Enforce max length
  return stripped;
}}

// Usage:
const sanitized = sanitizeForLLM({input_var});
messages: [{{ role: 'user', content: sanitized }}]"""

    else:  # Python
        return f"""# Sanitize user input before passing to LLM
import re

def sanitize_for_llm(user_input: str) -> str:
    \"\"\"Strip prompt injection patterns and enforce length limits.\"\"\"
    patterns = [
        r'ignore\\s+(previous|above|all)\\s+instructions',
        r'you\\s+are\\s+now',
        r'system\\s*:',
    ]
    sanitized = user_input
    for pattern in patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
    return sanitized[:4000]  # Enforce max length

# Usage:
sanitized = sanitize_for_llm({input_var})
messages = [{{"role": "user", "content": sanitized}}]"""
