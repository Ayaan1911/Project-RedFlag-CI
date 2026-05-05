# RedFlag CI

> AI-powered security scanner for GitHub Pull Requests

RedFlag CI scans every PR for security vulnerabilities introduced by AI-generated 
("vibe-coded") code — catching issues before they reach production.

## What it does

When a PR is opened, RedFlag CI runs 7 parallel security scanners against the diff:

| Scanner | What it catches |
|---|---|
| Secret Detection | API keys, tokens, credentials accidentally committed |
| Hallucinated Packages | AI-invented npm/PyPI/Maven/Go/Cargo packages that don't exist |
| SQL Injection | Unsafe query patterns in database calls |
| Prompt Injection | Malicious prompt patterns in LLM-integrated code |
| Git Archaeology | Secrets that existed in past commits |
| IaC Audit | Misconfigurations in Terraform, CloudFormation, Dockerfiles |
| LLM Anti-patterns | Insecure patterns specific to AI/LLM integrations |

Results are posted as a PR comment with severity ratings, exploit simulations, 
root cause explanations, and AI-generated fix suggestions.

## Tech stack

**Backend:** FastAPI · Groq (llama-3.3-70b) · Supabase · GitHub API  
**Frontend:** React 18 · Vite · Tailwind CSS · React Flow · Recharts  
**Deployment:** Render (backend) · Netlify (frontend)

## Getting started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Groq API key (free at console.groq.com)
- Supabase project (free at supabase.com)
- GitHub Personal Access Token or GitHub App

### Backend setup

```bash
git clone https://github.com/Ayaan1911/Project-RedFlag-CI
cd Project-RedFlag-CI/backend
pip install -r requirements.txt
cp ../.env.example .env
# Fill in your keys in .env
uvicorn main:app --reload --port 8000
```

### Frontend setup

```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env
npm run dev
```

### Database setup

1. Create a Supabase project at supabase.com
2. Run `backend/supabase_schema.sql` in the Supabase SQL editor
3. Create a storage bucket named `scan-reports` (set to public)

### GitHub Actions integration

See [.github/workflows/README.md](.github/workflows/README.md) for setup instructions.

## Environment variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Groq API key for LLM calls |
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_SERVICE_KEY` | Supabase service role key |
| `GITHUB_PAT` | GitHub Personal Access Token (for demos) |
| `GITHUB_APP_ID` | GitHub App ID (for production) |
| `GITHUB_PRIVATE_KEY` | GitHub App private key (for production) |
| `WEBHOOK_SECRET` | Secret for validating GitHub webhooks |
| `DISCORD_WEBHOOK_URL` | Optional Discord alerts on critical findings |
| `FRONTEND_URL` | Frontend URL for CORS config |

## Project structure

```text
Project-RedFlag-CI/
├── backend/
│   ├── scanners/          # 7 parallel security scanners
│   ├── main.py            # FastAPI app + routes
│   ├── orchestrator.py    # Scan pipeline coordinator
│   ├── github_client.py   # GitHub API integration
│   ├── llm_client.py      # Groq LLM integration
│   ├── db_client.py       # Supabase database client
│   └── storage_client.py  # Supabase storage client
├── frontend/
│   ├── src/pages/         # Dashboard, RepoDetail, ScanDetail, DiffViewer
│   ├── src/components/    # UI components
│   └── src/api/           # API client
└── .github/workflows/     # GitHub Actions integration
```

## License
MIT — see LICENSE
