[README.md](https://github.com/user-attachments/files/26427833/README.md)
<div align="center">

```
██████╗ ███████╗██████╗ ███████╗██╗      █████╗  ██████╗      ██████╗██╗
██╔══██╗██╔════╝██╔══██╗██╔════╝██║     ██╔══██╗██╔════╝     ██╔════╝██║
██████╔╝█████╗  ██║  ██║█████╗  ██║     ███████║██║  ███╗    ██║     ██║
██╔══██╗██╔══╝  ██║  ██║██╔══╝  ██║     ██╔══██║██║   ██║    ██║     ██║
██║  ██║███████╗██████╔╝██║     ███████╗██║  ██║╚██████╔╝    ╚██████╗██║
╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═╝ ╚═════╝      ╚═════╝╚═╝
```

### **Your AI wrote the code. We detect, attack-simulate, explain, and fix it.**

[![Track](https://img.shields.io/badge/Track-01%20Coding%20Agents-red?style=for-the-badge)](.)
[![Hackathon](https://img.shields.io/badge/HACK'A'WAR-2026-black?style=for-the-badge)](.)
[![Team](https://img.shields.io/badge/Team-Neural%20Forge-orange?style=for-the-badge)](.)
[![Problems](https://img.shields.io/badge/Problem%20Statements-7-brightgreen?style=for-the-badge)](.)

[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock%20%7C%20Claude%20Sonnet%204-FF9900?style=flat-square&logo=amazon-aws)](.)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python)](.)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react)](.)
[![Lambda](https://img.shields.io/badge/AWS-Lambda-FF9900?style=flat-square&logo=amazon-aws)](.)

> **One pipeline. Seven problem statements. No other team in this room is doing that.**

</div>

---

## 🚨 What Is RedFlag CI?

RedFlag CI is a **GitHub-native, AI-powered CI/CD security pipeline** engineered specifically for the era of vibe-coded software. It integrates directly into any GitHub repository, activates on every pull request, and runs **9 parallel security scan layers** — detecting, explaining, simulating, and automatically fixing the security vulnerabilities that emerge from AI-generated codebases.

Unlike every existing security scanner (GitGuardian, Snyk, Semgrep, GitHub Advanced Security), RedFlag CI was **built for the threat profile of LLM-generated code** — with specialized detection for hallucinated packages, prompt injection, LLM anti-patterns, and AI-generated infrastructure misconfigurations.

```
Developer opens PR
       │
       ▼
GitHub Webhook ──► API Gateway ──► Lambda Orchestrator
                                          │
                          ┌───────────────┼───────────────┐
                          ▼               ▼               ▼
                   Secret Scanner   SQL Scanner    IaC Auditor
                   Package Checker  Prompt Inj.   Pipeline Analyzer
                   Git Archaeology  LLM Antipattern Exploit Sim.
                          │               │               │
                          └───────────────┴───────────────┘
                                          │
                                    Amazon Bedrock
                                  (Claude Sonnet 4)
                                          │
                          ┌───────────────┼───────────────┐
                          ▼               ▼               ▼
                    PR Comment        Auto-Fix PR     Dashboard
                  Vibe Risk: 91/100   redflag/fix-1   DynamoDB
```

**Core Loop:** Developer opens PR → GitHub webhook fires → Lambda executes 9-layer scan → Bedrock generates fixes → PR comment posted + Fix PR auto-created → Dashboard updated.

**Target scan time: under 90 seconds.**

---

## 🏆 Problem Statement Coverage

RedFlag CI solves **7 hackathon problem statements** with a single unified architecture.

| # | Problem Statement | Track | How It's Covered |
|---|---|---|---|
| **1.5** | Security Review Agent | 01 | 9 parallel scan engines — CORE product |
| **1.6** | Technical Debt Quantifier | 01 | Vibe Debt Score + vulnerability lifecycle tracking |
| **1.4** | Intelligent Prompt Router | 01 | `router.py` routes Haiku vs Sonnet per scan type |
| **1.1** | DevOps Autopilot | 01 | `pipeline_analyzer.py` scans GitHub Actions YAML |
| **1.2** | Well-Architected Review Agent | 01 | `iac_auditor.py` scores IaC against 6 WAF pillars |
| **2.3** | FinOps Autopilot | 02 | Breach cost + fix cost estimate per IaC finding |
| **4.1** | Zero-to-Audit Compliance Platform | 04 | `compliance_mapper.py` maps findings to SOC 2 / OWASP / CIS |

---

## ⚔️ The Six (+ More) Vulnerability Classes We Catch

| Vulnerability | How LLMs Produce It | Real-World Impact |
|---|---|---|
| **Hardcoded Secrets** | LLMs embed API keys directly — fastest path to working code | Account takeover, data breach — avg $4.45M cost |
| **Hallucinated Packages** | LLMs confidently suggest non-existent npm/pip packages | Supply chain attacks — attackers pre-register malicious versions |
| **SQL Injection** | LLMs default to string concatenation queries | Database compromise, full data exfiltration |
| **Prompt Injection** | Raw user input piped directly into LLM API calls | System prompt override, data extraction, model manipulation |
| **IaC Over-Permissions** | LLMs use wildcard IAM/public S3 because it "just works" | Full cloud account compromise |
| **Git History Exposure** | Developers delete secrets from latest commit, not history | Permanent credential exposure in version control |
| **Pipeline Vulnerabilities** | Unpinned actions, write-all permissions, missing caching | Supply chain + CI/CD compromise, wasted build time |

---

## ✨ Full Feature Set

### 🔴 Core Scan Engines (Problem 1.5)

**1. AI Code Fingerprinting Engine**
Classifies every changed file as AI-generated or human-written before scanning. AI-generated files receive a stricter, specialized ruleset. Lightweight binary classifier using `.cursorrules` detection, Copilot metadata, comment signatures, and structural patterns — no ML model required.

**2. Secret Detection Engine**
TruffleHog base layer + custom regex for modern AI service keys (`sk-proj-*`, `sk-ant-*`, Hugging Face, Cursor). Entropy analysis detects high-entropy strings even without known service signatures. Scans 40+ service patterns.

**3. Hallucinated Package Detector**
Async cross-reference of every dependency against live npm Registry and PyPI APIs. Packages returning non-200 responses are flagged as hallucinated — prime supply chain attack vectors. Extended with a full **trust score** (TRUSTED / SUSPICIOUS / DANGEROUS) based on weekly downloads, package age, repository presence, and maintainer count.

**4. SQL Injection Scanner**
Semgrep static analysis targeting string concatenation queries, f-string SQL, JavaScript template literals, and ORM raw query calls. Bedrock generates the parameterized equivalent as the auto-fix.

**5. Prompt Injection Vulnerability Scanner**
Traces data flow from HTTP request parameters through the call graph to LLM API call sites. Flags every route where `request.body`, `request.query`, or `request.params` reach a `messages[]` array unsanitized. The only CI/CD tool that detects prompt injection at the source code level.

**6. LLM Anti-Pattern Scanner**
Bedrock-powered detection of CORS wildcard configs, missing auth middleware, missing rate limiting, exposed debug routes, and unvalidated file upload handlers — specific patterns LLMs consistently generate.

**7. Git History Archaeology**
GitPython traverses the full commit log and applies secret detection to every historical file state. Finds secrets that were "deleted" from the latest commit but still live permanently in git history. Outputs the exact commit SHA and a ready-to-execute BFG Repo Cleaner purge command.

**8. IaC Permission Auditor**
Parses Terraform `.tf`, CloudFormation `template.yaml`, CDK stacks, and `serverless.yml`. Detects wildcard IAM, public S3 ACLs, `0.0.0.0/0` security groups, unencrypted RDS. Extended with WAF pillar scoring and FinOps cost impact.

**9. Pipeline Security Analyzer** *(Problem 1.1)*
Scans `.github/workflows/*.yml` for hardcoded secrets in `env:` blocks, `permissions: write-all`, unpinned third-party actions, missing `GITHUB_TOKEN` scoping, missing `actions/cache`, jobs with no `timeout-minutes`, and sequential jobs that could run in parallel.

---

### 🤖 AI-Powered Intelligence

**Exploit Simulation Mode** *(Problem 1.5 extension)*
For every Critical finding, Bedrock generates a real proof-of-concept attack payload specific to the vulnerable code in the PR. Not generic — the exact SQL payload that dumps your database.

```json
{
  "payload": "GET /users?id=1' OR '1'='1' UNION SELECT username,password FROM users--",
  "impact": "Dumps all user credentials from the database",
  "curl_example": "curl 'https://api.example.com/users?id=1%27...'"
}
```

**Root Cause Explainer** *(Problem 1.5 + 1.6)*
Explains *why* the LLM generated insecure code — the behavioral reason, not just the technical description. Converts RedFlag CI from a detection tool into a learning system.

```json
{
  "why_llm_generated_this": "LLMs optimize for working code, not safe code.",
  "llm_behavioral_pattern": "Shortest-path optimization bias",
  "how_to_avoid": "Add to .cursorrules: never use string concat for SQL"
}
```

**Intelligent Prompt Router** *(Problem 1.4)*
Routes each Bedrock call to the optimal model — simple tasks to Claude Haiku (10x cheaper, 3x faster), complex reasoning to Claude Sonnet 4. Measurable cost savings displayed on the dashboard.

| Scanner | Model | Reason |
|---|---|---|
| `secret_scanner`, `package_checker`, `sql_scanner`, `git_archaeology` | Claude Haiku | Pattern matching only |
| `llm_antipattern`, `prompt_injection`, `iac_auditor`, `fix_generation`, `exploit_sim`, `root_cause` | Claude Sonnet 4 | Needs reasoning |

> **This scan cost $0.003 vs $0.031 without routing — 90% cheaper.**

---

### 📊 Scoring & Compliance

**Multi-Dimensional Vibe Score** *(Problem 1.6)*
Three separate risk dimensions computed per PR:
- **Security Risk Score** (0–100): `min(100, sum(severity_weights))` — Critical=25, High=15, Medium=8, Low=3
- **AI Confidence Score** (0–100): Percentage of files flagged as AI-generated
- **Code Reliability Score** (HIGH/MEDIUM/LOW): Derived from test coverage gaps and complexity

**Compliance Framework Mapper** *(Problem 4.1)*
Maps every finding to SOC 2, OWASP Top 10, and CIS Benchmark controls automatically. A finding doesn't just say "SQL injection found" — it says **"SQL injection found — violates OWASP A03:2021 and SOC 2 CC6.6 — this will fail your audit."**

| Finding Type | Compliance Controls |
|---|---|
| `SECRET` | SOC2:CC6.1, SOC2:CC6.7, CIS:13.1, OWASP:A07:2021 |
| `SQL` | OWASP:A03:2021, SOC2:CC6.6, CIS:18.1 |
| `PROMPT` | OWASP:A03:2021, OWASP:LLM01:2025, SOC2:CC6.6 |
| `PACKAGE` | OWASP:A06:2021, CIS:2.1, SOC2:CC7.1 |
| `IAC` | SOC2:CC6.1, SOC2:CC6.3, CIS:5.1, WAF:Security |
| `PIPELINE` | SOC2:CC8.1, CIS:16.1, WAF:OperationalExcellence |

**Well-Architected Review** *(Problem 1.2)*
Maps every IaC finding to the relevant AWS Well-Architected Framework pillar with a per-pillar score.

**FinOps Cost Impact** *(Problem 2.3)*
Attaches real dollar figures to every IaC misconfiguration:
- `wildcard_iam` → **$4.45M breach risk** at **$0 fix cost**
- `oversized_instance` → **$240/month overspend**, **$2,880/year waste**

---

## 🏗️ Architecture

### Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Compute** | AWS Lambda (Python 3.12) | Serverless, event-driven scan execution |
| **API** | Amazon API Gateway | HTTPS webhook endpoint, signature validation |
| **AI** | Amazon Bedrock — Claude Sonnet 4 + Haiku | Fix generation, anti-pattern analysis, exploit simulation |
| **Database** | Amazon DynamoDB | Scan results, Vibe Risk Scores, trend data |
| **Storage** | Amazon S3 | Full scan reports, audit logs, fix patches |
| **Secrets** | AWS Secrets Manager | GitHub App keys, webhook secrets, credentials |
| **Alerts** | Amazon SNS | Critical finding notifications |
| **Observability** | Amazon CloudWatch | Lambda logs, custom metrics, dashboards |
| **Frontend** | React 18 + Vite + Recharts + Tailwind | Real-time security dashboard |
| **Hosting** | AWS Amplify | Static frontend with GitHub CD |
| **CI/CD Trigger** | GitHub Actions + GitHub App | PR webhook, bot comments, auto-fix PRs |

### Security Libraries

| Library | Purpose |
|---|---|
| **TruffleHog** | Secret scanning — 700+ service patterns, Git-native |
| **Semgrep** | SQL injection + anti-pattern static analysis |
| **GitPython** | Git commit history traversal |
| **pyhcl** | Terraform HCL parsing |
| **PyYAML** | CloudFormation / GitHub Actions YAML parsing |
| **httpx** | Async registry API calls (npm, PyPI) |

### Request Lifecycle — PR to Fix in Under 90 Seconds

```
1. TRIGGER     Developer opens PR → GitHub fires webhook POST to API Gateway
2. VALIDATE    API Gateway validates X-Hub-Signature-256 against Secrets Manager
3. ORCHESTRATE Lambda fetches PR diff → AI Code Fingerprinting runs
4. SCAN        asyncio.gather → 9 scan engines run in parallel
5. AI ANALYZE  Critical findings → Exploit Simulation + Root Cause via Bedrock
6. SCORE       Multi-dimensional Vibe Score computed → Results stored in DynamoDB
7. COMMENT     Structured finding report posted as PR comment
8. FIX PR      Branch created → Fixes committed → Auto-fix PR opened
9. ALERT       If score > 80 → SNS critical notification published
10. DASHBOARD  React dashboard polls API → Vibe Debt trend chart updated
```

> **Lambda uses the Fork-Join pattern** via `asyncio.gather` — total scan time is `max(scan_times)`, not `sum(scan_times)`.

---

## 📁 Project Structure

```
redflagci/
├── backend/
│   ├── handler.py                  # Lambda entry point, webhook receiver
│   ├── orchestrator.py             # asyncio.gather coordinator (9 scanners)
│   ├── fingerprint.py              # AI code detection heuristics
│   ├── scorer.py                   # Multi-dimensional Vibe Risk Score
│   ├── bedrock_client.py           # Amazon Bedrock wrapper
│   ├── router.py                   # Intelligent Prompt Router (Haiku vs Sonnet)
│   ├── github_client.py            # GitHub API: diff, comment, branch, PR
│   ├── compliance_mapper.py        # SOC2 / OWASP / CIS control mapper
│   └── scanners/
│       ├── secret_scanner.py       # TruffleHog + custom patterns
│       ├── package_checker.py      # npm / PyPI registry cross-reference
│       ├── reputation_scorer.py    # Package trust scoring
│       ├── sql_scanner.py          # Semgrep SQL injection rules
│       ├── git_archaeology.py      # GitPython commit history scanner
│       ├── prompt_injection.py     # Data flow tracer → LLM API calls
│       ├── iac_auditor.py          # IaC + WAF pillars + FinOps cost impact
│       ├── llm_antipattern.py      # Bedrock-powered anti-pattern detection
│       ├── pipeline_analyzer.py    # GitHub Actions YAML security + efficiency
│       ├── exploit_simulation.py   # PoC attack payload generator
│       ├── root_cause.py           # LLM behavioral root cause explainer
│       └── auto_fix_pr.py          # Branch creation, file patching, PR opening
├── infra/
│   ├── cdk_stack.py                # All AWS infrastructure (CDK)
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── MetricCards.jsx
│       │   ├── VibeDebtChart.jsx
│       │   ├── ScanTable.jsx
│       │   ├── FindingDetail.jsx
│       │   ├── ExploitPanel.jsx
│       │   ├── RootCausePanel.jsx
│       │   ├── ComplianceBadges.jsx
│       │   ├── ReputationBadge.jsx
│       │   ├── PipelineFinding.jsx
│       │   ├── WAFScoreCard.jsx
│       │   ├── FinOpsCostCard.jsx
│       │   ├── RouterSavingsCard.jsx
│       │   └── VulnerabilityLifecycle.jsx
│       ├── pages/
│       │   ├── Dashboard.jsx
│       │   └── RepoDetail.jsx
│       └── api/
│           └── client.js
├── demo/
│   └── vibe-coded-api/             # Intentionally vulnerable demo repository
├── .github/
│   └── workflows/
│       └── redflagci.yml           # GitHub Actions CI/CD trigger
├── README.md
└── DEMO_SCRIPT.md
```

---

## 🚀 Getting Started

### Prerequisites

```bash
# Backend
Python 3.12
pip install truffle-hog semgrep gitpython pyhcl pyyaml httpx boto3 fastapi

# Infrastructure
Node.js 20
AWS CLI (configured with credentials)
AWS CDK

# Frontend
Node.js 20
npm
```

### Environment Setup

```bash
# Published by MDA at Hour 2 — fill in your values
API_GATEWAY_URL=https://{id}.execute-api.{region}.amazonaws.com/prod
LAMBDA_FUNCTION_NAME=redflagci-scanner
DYNAMODB_TABLE_NAME=redflagci-scans
S3_BUCKET_NAME=redflagci-reports
AWS_REGION=ap-south-1

# GitHub App (fill these in)
GITHUB_APP_ID=
GITHUB_PRIVATE_KEY_PATH=
WEBHOOK_SECRET=

# Bedrock
BEDROCK_MODEL_ID=claude-sonnet-4-20250514
```

### Deploy Infrastructure

```bash
cd infra
pip install -r requirements.txt
cdk bootstrap
cdk deploy
```

### Deploy Backend

```bash
cd backend
pip install -r requirements.txt -t ./package
cd package && zip -r ../deployment.zip .
cd .. && zip -g deployment.zip *.py scanners/*.py
aws lambda update-function-code \
  --function-name redflagci-scanner \
  --zip-file fileb://deployment.zip
```

### Run Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 🎯 Live Demo Walkthrough

**Minute 1 — Set the scene**
Open the demo repository. Show the vibe-coded Express.js API. *"This entire app was generated by Cursor in 20 minutes. Looks fine. Let's open a PR."*

**Minute 2 — The scan**
Open a PR. Watch the RedFlag CI workflow trigger. **60 seconds later** — bot comment appears.
- Vibe Risk Score: **91/100** 🔴
- OpenAI key exposed on line 4
- Hallucinated package `openai-stream-helper`
- SQL injection on line 23
- Stripe key found in commit `a3f2c1d` — even though it was deleted

**Minute 3 — Attack simulation + root cause**
Scroll to SQL injection. Show the exploit payload: *"Here is the exact query that dumps your database right now."* Show compliance: *"This violates OWASP A03:2021 and SOC 2 CC6.6 — your next audit will fail because of this line."*

**Minute 4 — Cost intelligence + pipeline audit**
Show the public S3 bucket IaC finding. FinOps card: **$4.45M breach exposure, $0 fix cost.** WAF pillar score: Security **2/10.** Pipeline tab: RedFlag CI audited its own GitHub Actions workflow — found missing cache, estimated +40% build time wasted.

**Minute 5 — Fix PR + Dashboard**
Auto-fix PR: all 6 findings patched, ready to merge. Router savings card: **$0.003 vs $0.031 — 90% savings.** Vulnerability Lifecycle: **87 hours undetected → 27 minutes to fix.**

*"Seven hackathon problem statements. One pipeline. Your AI wrote it in 20 minutes. We secured, attacked, explained, and fixed it in 90 seconds."*

---

## 🔌 API Reference

### `GET /api/scans/{repo_id}`
Returns a list of scan summaries for a repository.

### `GET /api/scans/{repo_id}/{pr_number}`
Returns full scan detail including all findings, compliance violations, exploit payloads, and cost impact.

```json
{
  "pr_number": 1,
  "vibe_risk_score": 91,
  "ai_confidence_score": 87,
  "code_reliability_score": "LOW",
  "bedrock_cost_usd": 0.003,
  "cost_savings_pct": 90,
  "findings": [
    {
      "type": "SQL",
      "severity": "CRITICAL",
      "file": "routes/users.js",
      "line": 23,
      "description": "String concatenation SQL query — injectable",
      "fix_code": "...",
      "exploit_payload": {
        "payload": "GET /users?id=1' OR '1'='1' UNION SELECT ...",
        "impact": "Dumps all user credentials",
        "curl_example": "curl 'https://api.example.com/...'"
      },
      "root_cause": {
        "why_llm_generated_this": "LLMs optimize for working code, not safe code.",
        "llm_behavioral_pattern": "Shortest-path optimization bias",
        "how_to_avoid": "Add to .cursorrules: never use string concat for SQL"
      },
      "compliance_violations": ["OWASP:A03:2021", "SOC2:CC6.6", "CIS:18.1"],
      "audit_impact": "This finding will cause SOC 2 Type II audit failure"
    }
  ],
  "pipeline_findings": [...],
  "compliance_summary": {
    "owasp_violations": ["A03:2021", "A06:2021"],
    "soc2_violations": ["CC6.1", "CC6.6", "CC6.7"],
    "cis_violations": ["2.1", "13.1", "18.1"],
    "audit_ready": false
  },
  "auto_fix_pr_url": "https://github.com/org/repo/pull/2"
}
```

---

## 👥 Team Neural Forge

| Member | Role | Owns |
|---|---|---|
| **Nikhil Virdi** | Lead · Backend · AI Pipeline | Scan engines, Bedrock, GitHub API, orchestration, scoring, router, exploit sim, compliance mapper |
| **Mohammad Ayaan** | AWS Architect · DevOps | Infrastructure (CDK), Lambda deployment, IaC auditor, pipeline analyzer, auto-fix PR, WAF + FinOps |
| **Shivam Bhardwaj** | Frontend Engineer | React dashboard, all UI components, Recharts visualizations, Amplify deployment |
| **Eshan Shukla** | Frontend API Layer · Demo Repo | API client module, demo repo seeding, loading/error states, README, DEMO_SCRIPT |

> **Rule:** Nobody touches another member's files. All collaboration happens through frozen API contracts and integration checkpoints.

---

## 🏅 Why RedFlag CI Wins

| USP | Description | Competitive Gap |
|---|---|---|
| **AI-Code Aware** | First tool to differentiate AI-generated vs human-written code | No existing tool does this |
| **Prompt Injection Detection** | Detects prompt injection at source code level in CI/CD | Zero production tools offer this today |
| **Hallucinated Package Detection** | Live registry cross-reference for every dependency | Snyk scans known CVEs — can't detect non-existent packages |
| **Exploit Simulation** | Generates real PoC attack payloads per Critical finding | No scanner demonstrates the actual exploit |
| **Root Cause Analysis** | Explains *why* LLMs generate insecure code | No tool provides behavioral AI explanation |
| **Auto-Fix PRs** | Opens a fix PR automatically — not just a report | GitGuardian reports. RedFlag CI fixes. |
| **Git History Archaeology** | Finds secrets in history that were "deleted" from latest commit | Most tools scan current state only |
| **7 Problem Statements** | One pipeline covers 7 hackathon problems | No other team is doing this |

---

<div align="center">

**HACK'A'WAR 2026 · Team Neural Forge · RIT Bengaluru**

*Vibe code freely. Ship safely.*

</div>
