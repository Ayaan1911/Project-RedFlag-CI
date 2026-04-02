import os
import urllib.request

REPO = "Ayaan1911/Project-RedFlag-CI"
BRANCH = "main"

files_to_sync = [
    "backend/__init__.py",
    "backend/auto_fix_pr.py",
    "backend/bedrock_client.py",
    "backend/compliance_mapper.py",
    "backend/fingerprint.py",
    "backend/github_client.py",
    "backend/handler.py",
    "backend/main.py",
    "backend/orchestrator.py",
    "backend/requirements.txt",
    "backend/router.py",
    "backend/scanners/__init__.py",
    "backend/scanners/exploit_simulation.py",
    "backend/scanners/git_archaeology.py",
    "backend/scanners/iac_auditor.py",
    "backend/scanners/llm_antipattern.py",
    "backend/scanners/package_checker.py",
    "backend/scanners/prompt_injection.py",
    "backend/scanners/reputation_scorer.py",
    "backend/scanners/root_cause.py",
    "backend/scanners/secret_scanner.py",
    "backend/scanners/sql_scanner.py",
    "backend/scorer.py",
    "backend/tests/__init__.py",
    "backend/tests/test_scanners.py",
]

base_dir = os.path.dirname(os.path.abspath(__file__))

print(f"Syncing backend files from {REPO}...")

for file_path in files_to_sync:
    url = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{file_path}"
    local_path = os.path.join(base_dir, file_path.replace("/", os.sep))
    
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    
    print(f"Downloading {file_path}...")
    try:
        urllib.request.urlretrieve(url, local_path)
    except Exception as e:
        print(f"Failed to download {file_path}: {e}")

print("\nSync complete! Backend is now successfully updated with the GitHub repository.")
