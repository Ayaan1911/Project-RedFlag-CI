$ErrorActionPreference = "Stop"
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

Write-Host "==========================================" -ForegroundColor Green
Write-Host "🚀 Initializing RedFlag CI Monorepo 🚀" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# 1. SETUP BACKEND
Write-Host "`n[1/3] Setting up Python Backend..." -ForegroundColor Cyan
if (-not (Test-Path backend)) {
    New-Item -ItemType Directory -Path backend | Out-Null
}
Push-Location backend

Write-Host "Creating Python virtual environment..."
python -m venv venv
Write-Host "Activating venv and installing requirements..."
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
if (Test-Path requirements.txt) {
    pip install -r requirements.txt
} else {
    Write-Host "Wait, requirements.txt is missing from backend." -ForegroundColor Yellow
}
Pop-Location

# 2. SETUP FRONTEND
Write-Host "`n[2/3] Setting up React Frontend..." -ForegroundColor Cyan
if (-not (Test-Path frontend)) {
    Write-Host "Creating Vite React application..."
    npm create vite@latest frontend -- --template react
}
Push-Location frontend
Write-Host "Installing frontend dependencies..."
npm install
Write-Host "Installing hackathon specific packages (Tailwind, Recharts, Octokit)..."
npm install recharts tailwindcss postcss autoprefixer @octokit/rest lucide-react
Write-Host "Initializing Tailwind CSS..."
npx tailwindcss init -p
Pop-Location

# 3. SETUP INFRASTRUCTURE
Write-Host "`n[3/3] Setting up AWS CDK Infrastructure..." -ForegroundColor Cyan
if (-not (Test-Path infrastructure)) {
    New-Item -ItemType Directory -Path infrastructure | Out-Null
}
Push-Location infrastructure
if (-not (Test-Path cdk.json)) {
    Write-Host "Initializing CDK Python App..."
    npx cdk init app --language python
}
Pop-Location

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "✅ RedFlag CI setup complete! ✅" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
