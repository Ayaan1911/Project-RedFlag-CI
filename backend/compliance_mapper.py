"""
compliance_mapper.py — Compliance Framework Mapper (Problem 4.1)
Owner: Nikhil Virdi (NV)

Maps every RedFlag CI finding to compliance framework controls:
  - SOC 2 Type II
  - OWASP Top 10 (2021)
  - OWASP LLM Top 10 (2025)
  - CIS Benchmarks
  - AWS Well-Architected Framework

Pure Python dict lookup — zero Bedrock calls, zero latency.
"""

import logging

logger = logging.getLogger(__name__)

# ─── Compliance Map ──────────────────────────────────────
# finding_type → list of framework:control references

COMPLIANCE_MAP = {
    "SECRET": {
        "controls": [
            "SOC2:CC6.1",    # Logical and Physical Access Controls
            "SOC2:CC6.7",    # Restriction of Credential Reuse
            "CIS:13.1",     # Centralized Sensitive Data Management
            "OWASP:A07:2021", # Security Misconfiguration
        ],
        "audit_impact": "Hardcoded credentials violate SOC 2 Type II access control requirements (CC6.1, CC6.7). This finding will cause audit failure. Credentials must be stored in a secrets manager.",
    },
    "SQL": {
        "controls": [
            "OWASP:A03:2021", # Injection
            "SOC2:CC6.6",    # Security Operations
            "CIS:18.1",     # Application Software Security
        ],
        "audit_impact": "SQL injection vulnerability violates OWASP A03:2021 (Injection) — the #3 most critical web application risk. Parameterized queries are required for SOC 2 compliance.",
    },
    "PROMPT": {
        "controls": [
            "OWASP:A03:2021",     # Injection (prompt injection is injection)
            "OWASP:LLM01:2025",   # Prompt Injection (LLM-specific)
            "SOC2:CC6.6",        # Security Operations
            "SOC2:CC7.2",        # System Monitoring
        ],
        "audit_impact": "Prompt injection vulnerability violates OWASP LLM01:2025 (Prompt Injection) — the #1 LLM security risk. Unsanitized user input reaching LLM APIs enables system prompt extraction and behavior manipulation.",
    },
    "PACKAGE": {
        "controls": [
            "OWASP:A06:2021", # Vulnerable and Outdated Components
            "CIS:2.1",      # Software Inventory
            "SOC2:CC7.1",   # To Detect and Address Security Events
            "SOC2:CC8.1",   # Change Management
        ],
        "audit_impact": "Hallucinated or untrusted dependencies violate OWASP A06:2021 (Vulnerable Components) and SOC 2 change management controls (CC8.1). Dependency confusion attacks enable remote code execution.",
    },
    "IAC": {
        "controls": [
            "SOC2:CC6.1",    # Logical and Physical Access Controls
            "SOC2:CC6.3",    # Access Controls for Protected Information
            "CIS:5.1",      # Secure Configuration for Cloud Services
            "WAF:Security",  # Well-Architected Security Pillar
        ],
        "audit_impact": "Infrastructure misconfigurations (public S3, wildcard IAM) violate SOC 2 access control requirements and CIS cloud benchmarks. These expose data and compute resources to unauthorized access.",
    },
    "GIT": {
        "controls": [
            "SOC2:CC6.1",    # Logical and Physical Access Controls
            "SOC2:CC6.7",    # Restriction of Credential Reuse
            "OWASP:A07:2021", # Security Misconfiguration
            "CIS:13.1",     # Centralized Sensitive Data Management
        ],
        "audit_impact": "Secrets in git history remain permanently accessible. Even 'deleted' credentials violate SOC 2 CC6.7 until the credential is rotated AND purged from repository history.",
    },
    "PIPELINE": {
        "controls": [
            "SOC2:CC8.1",          # Change Management
            "CIS:16.1",           # Application Software Security
            "WAF:OperationalExcellence", # Well-Architected Ops Pillar
        ],
        "audit_impact": "Insecure CI/CD pipeline configurations (overly permissive workflow permissions, unpinned actions) violate SOC 2 change management controls and enable supply chain attacks.",
    },
    "LLM_ANTIPATTERN": {
        "controls": [
            "OWASP:A05:2021", # Security Misconfiguration
            "SOC2:CC6.6",    # Security Operations
            "CIS:18.1",     # Application Software Security
        ],
        "audit_impact": "LLM-generated anti-patterns (CORS wildcard, missing auth, exposed debug routes) violate basic security configuration requirements across SOC 2 and OWASP frameworks.",
    },
}


class ComplianceMapper:
    """Maps findings to compliance framework controls."""

    @staticmethod
    def map_finding(finding: dict) -> dict:
        """
        Add compliance data to a single finding.
        
        Returns dict with:
          - compliance_violations: list of control references
          - audit_impact: human-readable audit impact statement
        """
        finding_type = finding.get("type", "UNKNOWN")
        mapping = COMPLIANCE_MAP.get(finding_type)

        if mapping:
            return {
                "compliance_violations": mapping["controls"],
                "audit_impact": mapping["audit_impact"],
            }

        # Unknown type — generic mapping
        return {
            "compliance_violations": ["OWASP:A00:2021"],
            "audit_impact": "This finding may impact compliance posture. Manual review recommended.",
        }

    @staticmethod
    def build_compliance_summary(findings: list[dict]) -> dict:
        """
        Aggregate all compliance violations across findings.
        
        Returns:
          {
            owasp_violations: ['A03:2021', 'A06:2021', ...],
            soc2_violations: ['CC6.1', 'CC6.6', ...],
            cis_violations: ['13.1', '18.1', ...],
            waf_violations: ['Security', 'OperationalExcellence'],
            llm_owasp_violations: ['LLM01:2025'],
            total_controls_violated: int,
            audit_ready: bool
          }
        """
        owasp = set()
        soc2 = set()
        cis = set()
        waf = set()
        llm_owasp = set()

        for finding in findings:
            violations = finding.get("compliance_violations", [])
            for v in violations:
                if v.startswith("OWASP:LLM"):
                    llm_owasp.add(v.replace("OWASP:", ""))
                elif v.startswith("OWASP:"):
                    owasp.add(v.replace("OWASP:", ""))
                elif v.startswith("SOC2:"):
                    soc2.add(v.replace("SOC2:", ""))
                elif v.startswith("CIS:"):
                    cis.add(v.replace("CIS:", ""))
                elif v.startswith("WAF:"):
                    waf.add(v.replace("WAF:", ""))

        total = len(owasp) + len(soc2) + len(cis) + len(waf) + len(llm_owasp)

        return {
            "owasp_violations": sorted(list(owasp)),
            "soc2_violations": sorted(list(soc2)),
            "cis_violations": sorted(list(cis)),
            "waf_violations": sorted(list(waf)),
            "llm_owasp_violations": sorted(list(llm_owasp)),
            "total_controls_violated": total,
            "audit_ready": total == 0,
        }
