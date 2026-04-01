"""
tests/test_scanners.py — Unit Tests for All NV Scan Engines + Scorer
Owner: Nikhil Virdi (NV)

Run: pytest backend/tests/ -v
"""

import pytest
import asyncio
import json


# ─── Helpers ──────────────────────────────────────────────

def run_async(coro):
    """Helper to run async functions in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ─── Test: Secret Scanner ─────────────────────────────────

class TestSecretScanner:

    def test_detects_openai_key(self):
        from backend.scanners.secret_scanner import SecretScanner
        scanner = SecretScanner()
        files = [{"filename": "config.js", "content": "const key = 'sk-proj-AbCdEfGhIjKlMnOpQrStUvWx1234567890'", "patch": ""}]
        findings = run_async(scanner.run(files))
        assert len(findings) >= 1
        assert findings[0]["type"] == "SECRET"
        assert findings[0]["severity"] == "CRITICAL"

    def test_detects_stripe_key(self):
        from backend.scanners.secret_scanner import SecretScanner
        scanner = SecretScanner()
        # Using a test-only pattern that matches our regex but won't trigger GitHub push protection
        test_key = "sk_live_" + "TESTONLY" * 4  # builds a fake key dynamically
        files = [{"filename": "config.py", "content": f"stripe_key = '{test_key}'", "patch": ""}]
        findings = run_async(scanner.run(files))
        assert len(findings) >= 1
        assert any(f["severity"] == "CRITICAL" for f in findings)

    def test_detects_aws_key(self):
        from backend.scanners.secret_scanner import SecretScanner
        scanner = SecretScanner()
        files = [{"filename": "deploy.sh", "content": "export AWS_KEY=AKIAIOSFODNN7EXAMPLE", "patch": ""}]
        findings = run_async(scanner.run(files))
        assert len(findings) >= 1

    def test_ignores_safe_files(self):
        from backend.scanners.secret_scanner import SecretScanner
        scanner = SecretScanner()
        files = [{"filename": "app.py", "content": "print('hello world')", "patch": ""}]
        findings = run_async(scanner.run(files))
        assert len(findings) == 0

    def test_skips_binary_files(self):
        from backend.scanners.secret_scanner import SecretScanner
        scanner = SecretScanner()
        files = [{"filename": "logo.png", "content": "sk-proj-fake", "patch": ""}]
        findings = run_async(scanner.run(files))
        assert len(findings) == 0


# ─── Test: Package Checker ────────────────────────────────

class TestPackageChecker:

    def test_detects_hallucinated_npm_package(self):
        from backend.scanners.package_checker import PackageChecker
        checker = PackageChecker()
        pkg_json = json.dumps({
            "dependencies": {
                "openai-stream-helper": "^1.0.0"
            }
        })
        files = [{"filename": "package.json", "content": pkg_json, "patch": ""}]
        findings = run_async(checker.run(files))
        assert len(findings) >= 1
        assert findings[0]["type"] == "PACKAGE"
        assert findings[0]["severity"] == "CRITICAL"
        assert "openai-stream-helper" in findings[0]["description"]

    def test_real_npm_package_passes(self):
        from backend.scanners.package_checker import PackageChecker
        checker = PackageChecker()
        pkg_json = json.dumps({
            "dependencies": {
                "express": "^4.18.0"
            }
        })
        files = [{"filename": "package.json", "content": pkg_json, "patch": ""}]
        findings = run_async(checker.run(files))
        assert len(findings) == 0

    def test_ignores_non_package_files(self):
        from backend.scanners.package_checker import PackageChecker
        checker = PackageChecker()
        files = [{"filename": "app.js", "content": "const x = 1;", "patch": ""}]
        findings = run_async(checker.run(files))
        assert len(findings) == 0


# ─── Test: SQL Scanner ───────────────────────────────────

class TestSQLScanner:

    def test_detects_js_concat_sqli(self):
        from backend.scanners.sql_scanner import SQLScanner
        scanner = SQLScanner()
        vuln_code = "const q = 'SELECT * FROM users WHERE id = ' + req.params.id;"
        files = [{"filename": "routes/users.js", "content": vuln_code, "patch": ""}]
        findings = run_async(scanner.run(files))
        assert len(findings) >= 1
        assert findings[0]["type"] == "SQL"
        assert findings[0]["severity"] == "CRITICAL"

    def test_detects_python_fstring_sqli(self):
        from backend.scanners.sql_scanner import SQLScanner
        scanner = SQLScanner()
        vuln_code = "cursor.execute(f\"SELECT * FROM users WHERE id = {user_id}\")"
        files = [{"filename": "db.py", "content": vuln_code, "patch": ""}]
        findings = run_async(scanner.run(files))
        assert len(findings) >= 1

    def test_safe_parameterized_query(self):
        from backend.scanners.sql_scanner import SQLScanner
        scanner = SQLScanner()
        safe_code = "cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))"
        files = [{"filename": "db.py", "content": safe_code, "patch": ""}]
        findings = run_async(scanner.run(files))
        assert len(findings) == 0


# ─── Test: Prompt Injection Scanner ───────────────────────

class TestPromptInjectionScanner:

    def test_detects_direct_input_to_llm(self):
        from backend.scanners.prompt_injection import PromptInjectionScanner
        scanner = PromptInjectionScanner()
        vuln_code = """
const openai = require('openai');
const client = new openai();
app.post('/chat', async (req, res) => {
    const response = await client.chat.completions.create({
        model: 'gpt-4',
        messages: [{role: 'user', content: req.body.message}]
    });
});
"""
        files = [{"filename": "routes/chat.js", "content": vuln_code, "patch": ""}]
        findings = run_async(scanner.run(files))
        assert len(findings) >= 1
        assert findings[0]["type"] == "PROMPT"

    def test_safe_file_no_llm_calls(self):
        from backend.scanners.prompt_injection import PromptInjectionScanner
        scanner = PromptInjectionScanner()
        safe_code = "console.log('hello world');"
        files = [{"filename": "app.js", "content": safe_code, "patch": ""}]
        findings = run_async(scanner.run(files))
        assert len(findings) == 0


# ─── Test: Git Archaeology Scanner ────────────────────────

class TestGitArchaeologyScanner:

    def test_detects_removed_secret_in_patch(self):
        from backend.scanners.git_archaeology import GitArchaeologyScanner
        scanner = GitArchaeologyScanner()
        # Build fake key dynamically to avoid GitHub push protection
        fake_key = "sk_live_" + "TESTONLY" * 4
        patch = f"-const key = '{fake_key}';\n+// key removed for security\n"
        files = [{"filename": "config.js", "content": "", "patch": patch}]
        findings = run_async(scanner.run(files))
        assert len(findings) >= 1
        assert findings[0]["type"] == "GIT"
        assert findings[0]["severity"] == "CRITICAL"

    def test_no_findings_for_clean_patch(self):
        from backend.scanners.git_archaeology import GitArchaeologyScanner
        scanner = GitArchaeologyScanner()
        patch = """+const app = express();
+app.listen(3000);
"""
        files = [{"filename": "app.js", "content": "", "patch": patch}]
        findings = run_async(scanner.run(files))
        assert len(findings) == 0


# ─── Test: AI Fingerprinter ───────────────────────────────

class TestAIFingerprinter:

    def test_detects_cursorrules_file(self):
        from backend.fingerprint import AIFingerprinter
        fp = AIFingerprinter()
        files = [
            {"filename": ".cursorrules", "content": "rules content", "patch": ""},
            {"filename": "app.py", "content": "print('hi')", "patch": ""},
        ]
        findings = fp.analyze_files(files)
        # Both files should get flagged because .cursorrules is in the PR
        assert len(findings) >= 1

    def test_detects_ai_comment(self):
        from backend.fingerprint import AIFingerprinter
        fp = AIFingerprinter()
        files = [{"filename": "utils.py", "content": "# Generated by GitHub Copilot\ndef add(a, b):\n    return a + b", "patch": ""}]
        findings = fp.analyze_files(files)
        assert len(findings) >= 1
        assert files[0]["is_ai_generated"] is True


# ─── Test: Vibe Risk Scorer ───────────────────────────────

class TestVibeRiskScorer:

    def test_score_calculation(self):
        from backend.scorer import VibeRiskScorer
        findings = [
            {"severity": "CRITICAL"},
            {"severity": "CRITICAL"},
            {"severity": "HIGH"},
            {"severity": "MEDIUM"},
            {"severity": "LOW"},
        ]
        # 25 + 25 + 15 + 8 + 3 = 76
        score = VibeRiskScorer.calculate_score(findings)
        assert score == 76

    def test_score_caps_at_100(self):
        from backend.scorer import VibeRiskScorer
        findings = [{"severity": "CRITICAL"}] * 10  # 25 × 10 = 250 → capped to 100
        score = VibeRiskScorer.calculate_score(findings)
        assert score == 100

    def test_empty_findings_score_zero(self):
        from backend.scorer import VibeRiskScorer
        score = VibeRiskScorer.calculate_score([])
        assert score == 0

    def test_severity_summary(self):
        from backend.scorer import VibeRiskScorer
        findings = [
            {"severity": "CRITICAL"},
            {"severity": "CRITICAL"},
            {"severity": "HIGH"},
            {"severity": "LOW"},
        ]
        summary = VibeRiskScorer.get_severity_summary(findings)
        assert summary == {"critical": 2, "high": 1, "medium": 0, "low": 1}

    def test_risk_levels(self):
        from backend.scorer import VibeRiskScorer
        assert VibeRiskScorer.get_risk_level(0) == "SAFE"
        assert VibeRiskScorer.get_risk_level(5) == "SAFE"
        assert VibeRiskScorer.get_risk_level(20) == "LOW_RISK"
        assert VibeRiskScorer.get_risk_level(50) == "MODERATE"
        assert VibeRiskScorer.get_risk_level(75) == "HIGH_RISK"
        assert VibeRiskScorer.get_risk_level(91) == "CRITICAL_RISK"
        assert VibeRiskScorer.get_risk_level(100) == "CRITICAL_RISK"

    def test_risk_badge_format(self):
        from backend.scorer import VibeRiskScorer
        badge = VibeRiskScorer.build_risk_badge(91)
        assert "CRITICAL RISK" in badge
        assert "91/100" in badge

    def test_demo_repo_expected_score(self):
        """
        The demo repo has 6 vulnerabilities:
          4 CRITICAL (secret, package, SQL, git) = 4 × 25 = 100
          1 HIGH (prompt injection) = 15
          1 HIGH (IaC) = 15
        Total = 130 → capped to 100.
        But since we detect ~4 CRITICAL + 1 HIGH from NV scanners:
        4×25 + 1×15 = 115 → capped to 100, so score should be 100.
        
        With our actual scanners finding fewer (depends on IAC being MDA's):
          3 CRITICAL (secret, package, SQL) + 1 CRITICAL (git) + 1 HIGH (prompt) = 
          4×25 + 1×15 = 115 → 100
        """
        from backend.scorer import VibeRiskScorer
        demo_findings = [
            {"severity": "CRITICAL", "type": "SECRET"},
            {"severity": "CRITICAL", "type": "PACKAGE"},
            {"severity": "CRITICAL", "type": "SQL"},
            {"severity": "CRITICAL", "type": "GIT"},
            {"severity": "HIGH", "type": "PROMPT"},
        ]
        score = VibeRiskScorer.calculate_score(demo_findings)
        # 4×25 + 1×15 = 115 → capped to 100
        assert score == 100
