class LLMAntiPatternScanner:
    """
    Scans files for LLM-generated antipatterns (e.g. wildcard CORS, disabled auth).
    """
    async def run(self, files: list[dict]) -> list[dict]:
        findings = []
        
        valid_extensions = (".py", ".js", ".ts", ".jsx", ".tsx")
        
        for file_obj in files:
            filename = file_obj.get("filename", "")
            content = file_obj.get("content", "")
            patch = file_obj.get("patch", "")
            
            if not filename.endswith(valid_extensions):
                continue
                
            full_text = f"{content}\n{patch}"
            lines = full_text.split("\n")
            
            rule1_triggered = False
            rule2_triggered = False
            rule3_triggered = False
            
            for i, line in enumerate(lines, 1):
                # Rule 1 — CORS Wildcard
                if not rule1_triggered:
                    if 'allow_origins' in line and '*' in line:
                        findings.append({
                            "type": "LLM_ANTIPATTERN",
                            "severity": "HIGH",
                            "file": filename,
                            "line": i,
                            "description": "CORS wildcard detected — all origins allowed",
                            "fix_code": "Replace allow_origins=['*'] with explicit list of allowed origins e.g. ['https://yourdomain.com']"
                        })
                        rule1_triggered = True
                        
                # Rule 2 — Debug Mode Exposed
                if not rule2_triggered:
                    if ('DEBUG' in line and 'True' in line) or 'debug=True' in line.replace(" ", ""):
                        findings.append({
                            "type": "LLM_ANTIPATTERN",
                            "severity": "MEDIUM",
                            "file": filename,
                            "line": i,
                            "description": "Debug mode enabled in production code",
                            "fix_code": "Set DEBUG=False in production. Use environment variables: DEBUG=os.getenv('DEBUG', 'False') == 'True'"
                        })
                        rule2_triggered = True
                        
                # Rule 3 — Exposed Admin/Debug Routes
                if not rule3_triggered:
                    if '/admin' in line or '/debug' in line:
                        if 'Depends(' not in line and 'require_auth' not in line and 'login_required' not in line:
                            findings.append({
                                "type": "LLM_ANTIPATTERN",
                                "severity": "HIGH",
                                "file": filename,
                                "line": i,
                                "description": "Exposed admin/debug route without authentication middleware",
                                "fix_code": "Add authentication dependency: @app.get('/admin', dependencies=[Depends(require_auth)])"
                            })
                            rule3_triggered = True
                            
            # Rule 4 — Missing Rate Limiting
            if 'FastAPI' in full_text or 'flask' in full_text:
                if 'slowapi' not in full_text and 'limiter' not in full_text and 'RateLimit' not in full_text:
                    findings.append({
                        "type": "LLM_ANTIPATTERN",
                        "severity": "MEDIUM",
                        "file": filename,
                        "line": 1,
                        "description": "No rate limiting detected on API — vulnerable to abuse",
                        "fix_code": "Add rate limiting using slowapi: from slowapi import Limiter. Apply @limiter.limit('10/minute') to public endpoints"
                    })
                    
        return findings
