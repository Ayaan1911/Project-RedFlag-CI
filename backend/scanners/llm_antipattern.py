from dataclasses import dataclass

@dataclass
class Finding:
    layer: str
    severity: str
    file: str
    line: int
    description: str
    fix: str

def scan_llm_antipatterns(files: list[dict]) -> list[Finding]:
    findings = []
    
    valid_extensions = (".py", ".js", ".ts", ".jsx", ".tsx")
    
    for file_obj in files:
        filename = file_obj.get("filename", "")
        content = file_obj.get("content", "")
        
        if not filename.endswith(valid_extensions):
            continue
            
        lines = content.split("\n")
        
        rule1_triggered = False
        rule2_triggered = False
        rule3_triggered = False
        
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # Rule 1 — CORS Wildcard
            if not rule1_triggered:
                if 'allow_origins' in line and '*' in line:
                    findings.append(Finding(
                        layer="E",
                        severity="high",
                        file=filename,
                        line=line_num,
                        description="CORS wildcard detected — all origins allowed",
                        fix="Replace allow_origins=['*'] with explicit list of allowed origins e.g. ['https://yourdomain.com']"
                    ))
                    rule1_triggered = True
                    
            # Rule 2 — Debug Mode Exposed
            if not rule2_triggered:
                if ('DEBUG' in line and 'True' in line) or 'debug=True' in line.replace(" ", ""):
                    findings.append(Finding(
                        layer="E",
                        severity="medium",
                        file=filename,
                        line=line_num,
                        description="Debug mode enabled in production code",
                        fix="Set DEBUG=False in production. Use environment variables: DEBUG=os.getenv('DEBUG', 'False') == 'True'"
                    ))
                    rule2_triggered = True
                    
            # Rule 3 — Exposed Admin/Debug Routes
            if not rule3_triggered:
                if '/admin' in line or '/debug' in line:
                    if 'Depends(' not in line and 'require_auth' not in line and 'login_required' not in line:
                        findings.append(Finding(
                        layer="E",
                        severity="high",
                        file=filename,
                        line=line_num,
                        description="Exposed admin/debug route without authentication middleware",
                        fix="Add authentication dependency: @app.get('/admin', dependencies=[Depends(require_auth)])"
                    ))
                        rule3_triggered = True
                        
        # Rule 4 — Missing Rate Limiting
        if 'FastAPI' in content or 'flask' in content:
            if 'slowapi' not in content and 'limiter' not in content and 'RateLimit' not in content:
                findings.append(Finding(
                    layer="E",
                    severity="medium",
                    file=filename,
                    line=1,
                    description="No rate limiting detected on API — vulnerable to abuse",
                    fix="Add rate limiting using slowapi: from slowapi import Limiter. Apply @limiter.limit('10/minute') to public endpoints"
                ))
                
    return findings
