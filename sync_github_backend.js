const fs = require('fs');
const https = require('https');
const path = require('path');

const REPO = "Ayaan1911/Project-RedFlag-CI";
const BRANCH = "main";

const filesToSync = [
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
];

const baseDir = __dirname;
console.log(`Syncing backend files from ${REPO}...`);

const downloadFile = (filePath) => {
    return new Promise((resolve, reject) => {
        const url = `https://raw.githubusercontent.com/${REPO}/${BRANCH}/${filePath}`;
        const localPath = path.join(baseDir, filePath.replace(/\//g, path.sep));
        
        fs.mkdirSync(path.dirname(localPath), { recursive: true });
        
        https.get(url, (res) => {
            if (res.statusCode !== 200) {
                reject(new Error(`Status Code: ${res.statusCode}`));
                return;
            }
            const fileStream = fs.createWriteStream(localPath);
            res.pipe(fileStream);
            fileStream.on('finish', () => {
                fileStream.close();
                console.log(`Successfully downloaded ${filePath}`);
                resolve();
            });
        }).on('error', (err) => {
            reject(err);
        });
    });
};

(async () => {
    for (const file of filesToSync) {
        try {
            await downloadFile(file);
        } catch (e) {
            console.error(`Failed to download ${file}: ${e.message}`);
        }
    }
    console.log('\nSync complete! Backend is now updated with the GitHub repository.');
})();
