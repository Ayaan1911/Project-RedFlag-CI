# RedFlag CI — Push Frontend Codebase to GitHub
$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Green
Write-Host "  Pushing nv-frontend to GitHub... " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Untrack the old 'frontend' folder from Git to prevent duplicates.
# (This keeps your local frontend folder running perfectly!)
git rm -r --cached "frontend" *>$null

$ErrorActionPreference = "Stop"

# Use robocopy to mirror frontend to nv-frontend while excluding heavy directories
Write-Host "Cloning codebase (excluding node_modules)..." -ForegroundColor Cyan
robocopy ".\frontend" ".\nv-frontend" /E /XD node_modules dist .git /NFL /NDL /NJH /NJS

# Robocopy returns codes < 8 on success
if ($LASTEXITCODE -ge 8) {
    Write-Host "Failed to clone frontend directory. Robocopy exit code: $LASTEXITCODE" -ForegroundColor Red
    exit 1
}

Write-Host "Staging nv-frontend in Git..." -ForegroundColor Cyan
git add nv-frontend

Write-Host "Committing changes..." -ForegroundColor Cyan
git commit -m "feat: Upload NV Liquid Glass Frontend Application UI"

Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
git push

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Success! Your Frontend is live on GitHub." -ForegroundColor Green
Write-Host "  Folder: /nv-frontend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Green
