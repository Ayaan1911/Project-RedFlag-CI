# RedFlag CI — Push to GitHub Script
# Run this ONCE from PowerShell inside c:\Users\Asus\RedFlagCI

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Green
Write-Host "  Pushing RedFlag CI to GitHub..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Initialize git if not already done
if (-not (Test-Path ".git")) {
    git init
    Write-Host "Git initialized." -ForegroundColor Cyan
}

# Add remote (skip if already exists)
$remotes = git remote
if ($remotes -notcontains "origin") {
    git remote add origin https://github.com/Ayaan1911/Project-RedFlag-CI.git
    Write-Host "Remote 'origin' added." -ForegroundColor Cyan
} else {
    Write-Host "Remote 'origin' already exists." -ForegroundColor Yellow
}

# Stage everything
git add .

# Commit
git commit -m "feat: NV Phase 0-4 — Full backend scan pipeline, Bedrock AI, scoring, API endpoints"

# Push to main
git branch -M main
git push -u origin main

# Create and push NV's working branch
git checkout -b branch/nv-backend 2>$null
git push -u origin branch/nv-backend

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Done! Code is live on GitHub." -ForegroundColor Green
Write-Host "  Repo: https://github.com/Ayaan1911/Project-RedFlag-CI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Green
