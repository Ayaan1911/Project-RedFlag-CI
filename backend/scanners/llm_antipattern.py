from typing import List
import re

# Import the Finding dataclass from the IaC auditor module
from .iac_auditor import Finding

def scan_llm_antipatterns(files: List[dict]) -> List[Finding]:
    """
    Scans files for common LLM API and general backend security anti-patterns.
    
    Args:
        files: List of dicts containing 'filename' and 'content' strings.
        
    Returns:
        List of Finding objects identifying anti-pattern vulnerabilities.
    """
    findings = []
    
    for file_obj in files:
        filename = file_obj.get("filename", "")
        content = file_obj.get("content", "")
        lines = content.split("\n")
        
        # Pre-scan file context indicators
        has_fastapi = "fastapi" in content.lower()
        has_rate_limit = "slowapi" in content or "limits" in content
        
        for i, line in enumerate(lines):
            line_no_spaces = line.replace(' ', '')
            
            # allow_origins=["*"] or ['*'] -> CORS wildcard -> HIGH
            if "allow_origins=[\"*\"]" in line_no_spaces or "allow_origins=['*']" in line_no_spaces:
                findings.append(Finding(
                    layer="LLM Anti-pattern",
                    severity="HIGH",
                    file=filename,
                    line=i + 1,
                    description="CORS wildcard detected. Exposes API to all origins.",
                    fix=line.replace('["*"]', '["https://your-domain.com"]').replace("['*']", "['https://your-domain.com']")
                ))
            
            # DEBUG = True or debug=True -> exposed debug mode -> MEDIUM
            if "DEBUG = True" in line or "debug=True" in line_no_spaces:
                findings.append(Finding(
                    layer="LLM Anti-pattern",
                    severity="MEDIUM",
                    file=filename,
                    line=i + 1,
                    description="Debug mode is enabled, potentially leaking sensitive runtime state.",
                    fix=re.sub(r'debug\s*=\s*True', 'debug=False', line, flags=re.IGNORECASE)
                ))
                
            # Exposed /admin or /debug routes without auth -> HIGH
            if has_fastapi and (re.search(r'@.*\.get\([\'"]/admin\/?', line) or re.search(r'@.*\.get\([\'"]/debug\/?', line)):
                if "Depends(" not in line:
                    findings.append(Finding(
                        layer="LLM Anti-pattern",
                        severity="HIGH",
                        file=filename,
                        line=i + 1,
                        description="Exposed administration or debugging route without authorization dependencies.",
                        fix="Add an authentication dependency: e.g., @app.get('/admin', dependencies=[Depends(get_current_admin)])"
                    ))
                    
        # No rate limiting detected (missing slowapi/limits when FastAPI is present) -> MEDIUM
        if has_fastapi and not has_rate_limit:
            findings.append(Finding(
                layer="LLM Anti-pattern",
                severity="MEDIUM",
                file=filename,
                line=1,
                description="FastAPI service detected without rate limiting imports (slowapi or limits).",
                fix="Import and implement rate limiting: from slowapi import Limiter, _rate_limit_exceeded_handler."
            ))
            
    return findings
