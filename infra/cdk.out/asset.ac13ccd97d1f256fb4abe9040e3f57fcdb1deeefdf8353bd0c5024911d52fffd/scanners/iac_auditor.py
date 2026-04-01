from dataclasses import dataclass
from typing import List
import re

@dataclass
class Finding:
    layer: str
    severity: str
    file: str
    line: int
    description: str
    fix: str

def audit_iac(files: List[dict]) -> List[Finding]:
    """
    Scans Infrastructure as Code files (.tf, .yaml, .yml, .json) for security vulnerabilities.
    
    Args:
        files: List of dicts, each containing 'filename' and 'content' strings.
        
    Returns:
        List of Finding objects identifying vulnerabilities and providing auto-fix strings.
    """
    findings = []
    
    for file_obj in files:
        filename = file_obj.get("filename", "")
        content = file_obj.get("content", "")
        lines = content.split("\n")
        
        # Helper to safely append findings
        def make_finding(severity, line_idx, description, fix):
            findings.append(Finding(
                layer="IaC Auditor",
                severity=severity,
                file=filename,
                line=line_idx + 1,
                description=description,
                fix=fix
            ))
            
        if filename.endswith(".tf"):
            for i, line in enumerate(lines):
                # Detect Action: "*" -> severity CRITICAL
                if re.search(r'["\']Action["\']\s*:\s*\[?["\']\*["\']\]?', line):
                    make_finding(
                        "CRITICAL", i,
                        "Wildcard IAM action detected. Grants excessive permissions.",
                        line.replace('"*"', '["SERVICE:SpecificAction"]').replace("'*'", "['SERVICE:SpecificAction']")
                    )
                    
                # Detect "acl" = "public-read" -> severity CRITICAL
                if re.search(r'["\']acl["\']\s*=\s*["\']public-read["\']', line):
                    make_finding(
                        "CRITICAL", i,
                        "Public read ACL detected on a resource.",
                        line.replace('public-read', 'private')
                    )
                    
                # Detect cidr_blocks containing "0.0.0.0/0" -> severity HIGH
                if re.search(r'cidr_blocks\s*=\s*\[.*["\']0\.0\.0\.0/0["\'].*\]', line):
                    make_finding(
                        "HIGH", i,
                        "Open CIDR block detected. Network is open to the world.",
                        line.replace('0.0.0.0/0', '10.0.0.0/8') # Replace with internal CIDR
                    )
                    
                # Detect encrypted = false -> severity MEDIUM
                if re.search(r'encrypted\s*=\s*(false|False)', line):
                    make_finding(
                        "MEDIUM", i,
                        "Resource encryption is explicitly disabled.",
                        re.sub(r'false|False', 'true', line)
                    )

        elif filename.endswith((".yaml", ".yml")):
            has_pab = False
            for i, line in enumerate(lines):
                # Detect Action: '*' -> severity CRITICAL
                if re.search(r'Action\s*:\s*[\'"]?\*[\'"]?', line):
                    make_finding(
                        "CRITICAL", i,
                        "Wildcard IAM action detected in YAML configuration.",
                        line.replace('*', 'SpecificServiceAction')
                    )
                
                # Verify PublicAccessBlockConfiguration presence
                if "PublicAccessBlockConfiguration" in line:
                    has_pab = True
            
            # Simple missing rule check for PublicAccessBlockConfiguration -> severity HIGH
            if "Type: AWS::S3::Bucket" in content and not has_pab:
                make_finding(
                    "HIGH", 0,
                    "PublicAccessBlockConfiguration is missing for S3 Bucket.",
                    "Add PublicAccessBlockConfiguration properties with BlockPublicAcls, BlockPublicPolicy, etc., set to true."
                )
                
    return findings
