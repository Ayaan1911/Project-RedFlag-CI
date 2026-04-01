"""
sql_scanner.py — SQL Injection Scanner
Owner: Nikhil Virdi (NV)

Detects SQL injection vulnerabilities from AI-generated code,
specifically string concatenation and template literal patterns
that LLMs consistently produce.
"""

import re
import logging

logger = logging.getLogger(__name__)


# ─── Detection Rules ───────────────────────────────────────
# Each rule: (name, pattern, severity, description_template, fix_template)

SQL_INJECTION_RULES = [
    # JavaScript/Node.js string concatenation
    (
        "JS String Concat SQL",
        r"""(?:"|')?(SELECT|INSERT|UPDATE|DELETE)\s+.*?\s+(FROM|INTO|SET)\s+.*?['"]\s*\+\s*(?:req\.|params\.|query\.|body\.|args\.|user)""",
        "CRITICAL",
        "SQL injection via string concatenation: user-controlled input '{input_var}' is concatenated directly into a SQL query.",
        "// Use parameterized queries:\nconst q = '{safe_query}';\ndb.query(q, [{param}]);",
    ),
    # Python f-string SQL
    (
        "Python f-string SQL",
        r"""f['"](SELECT|INSERT|UPDATE|DELETE)\s+.*?\{.*?\}""",
        "CRITICAL",
        "SQL injection via Python f-string: variable interpolated directly into SQL query string.",
        "# Use parameterized queries:\ncursor.execute('{safe_query}', ({param},))",
    ),
    # Python format() SQL
    (
        "Python format() SQL",
        r"""['"](SELECT|INSERT|UPDATE|DELETE).*?['"]\.format\(""",
        "CRITICAL",
        "SQL injection via str.format(): variable interpolated directly into SQL query.",
        "# Use parameterized queries:\ncursor.execute('{safe_query}', ({param},))",
    ),
    # Python % formatting SQL
    (
        "Python % format SQL",
        r"""['"](SELECT|INSERT|UPDATE|DELETE).*?['"]\s*%\s*\(""",
        "CRITICAL",
        "SQL injection via % string formatting in SQL query.",
        "# Use parameterized queries:\ncursor.execute('{safe_query}', ({param},))",
    ),
    # JavaScript template literal SQL
    (
        "JS Template Literal SQL",
        r"""`(SELECT|INSERT|UPDATE|DELETE)\s+.*?\$\{.*?\}.*?`""",
        "CRITICAL",
        "SQL injection via JavaScript template literal: ${variable} interpolated into SQL query.",
        "// Use parameterized queries:\nconst q = '{safe_query}';\ndb.query(q, [{param}]);",
    ),
    # Raw ORM queries
    (
        "Raw ORM Query",
        r"""(?:raw|execute|query)\s*\(\s*[f'"]?(SELECT|INSERT|UPDATE|DELETE)""",
        "HIGH",
        "Potentially unsafe raw SQL query detected in ORM call. Verify that inputs are parameterized.",
        "# Use the ORM's built-in parameterization:\nModel.objects.raw('{safe_query}', [{param}])",
    ),
]


class SQLScanner:
    """Scans source files for SQL injection vulnerabilities."""

    async def run(self, files: list[dict]) -> list[dict]:
        """Run SQL injection detection across all files."""
        findings = []

        for file_info in files:
            filename = file_info.get("filename", "")
            content = file_info.get("content", "")
            patch = file_info.get("patch", "")

            # Only scan code files
            if not any(filename.endswith(ext) for ext in [".js", ".ts", ".py", ".rb", ".java", ".go", ".php"]):
                continue

            full_text = f"{content}\n{patch}"
            lines = full_text.split("\n")

            for rule_name, pattern, severity, desc_template, fix_template in SQL_INJECTION_RULES:
                for i, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        # Extract what looks like the user input variable
                        input_var = _extract_input_var(line)

                        findings.append({
                            "type": "SQL",
                            "severity": severity,
                            "file": filename,
                            "line": i,
                            "description": (
                                f"[{rule_name}] {desc_template.format(input_var=input_var)}. "
                                "LLMs frequently generate string-concatenated SQL queries. "
                                "This allows attackers to inject arbitrary SQL commands."
                            ),
                            "fix_code": fix_template.format(
                                safe_query="SELECT * FROM table WHERE id = ?",
                                param=input_var or "sanitized_input",
                            ),
                        })

        logger.info("SQLScanner found %d SQL injection vulnerabilities.", len(findings))
        return findings


def _extract_input_var(line: str) -> str:
    """Try to extract the name of the user-controlled variable from the line."""
    patterns = [
        r"(req\.(?:params|query|body)\.\w+)",
        r"(request\.(?:args|form|json)\[?['\"]?\w+)",
        r"\$\{(\w+)\}",
        r"\+\s*(\w+)",
    ]
    for p in patterns:
        match = re.search(p, line)
        if match:
            return match.group(1)
    return "user_input"
