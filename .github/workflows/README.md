# RedFlag CI GitHub Actions Integration

## Setup

1. Deploy your RedFlag CI backend (see main README)
2. Add this secret to your target repository:
   - `REDFLAG_API_URL` — your deployed backend URL
     e.g. `https://your-redflag-instance.onrender.com`

## How it works

On every Pull Request (open, update, reopen):
1. GitHub Actions triggers this workflow
2. The workflow sends a webhook payload to your RedFlag CI backend
3. The backend runs all 7 security scanners against the PR diff
4. Results are posted as a PR comment automatically

## Scanners included

- Secret detection
- Hallucinated package detection  
- SQL injection patterns
- Prompt injection patterns
- Git history archaeology
- IaC misconfiguration audit
- LLM anti-pattern detection
