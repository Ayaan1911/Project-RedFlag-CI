class IACAuditor:
    """
    Scans IaC files (Terraform, CloudFormation) for security misconfigurations.
    """
    async def run(self, files: list[dict]) -> list[dict]:
        findings = []
        
        for file_obj in files:
            filename = file_obj.get("filename", "")
            content = file_obj.get("content", "")
            patch = file_obj.get("patch", "")
            
            if not filename.endswith((".tf", ".yaml", ".yml")):
                continue
                
            # Combine content and patch for basic rule processing
            full_text = f"{content}\n{patch}"
            lines = full_text.split("\n")
            
            if filename.endswith(".tf"):
                for i, line in enumerate(lines, 1):
                    if 'Action' in line and '*' in line:
                        findings.append({
                            "type": "IAC",
                            "severity": "CRITICAL",
                            "file": filename,
                            "line": i,
                            "description": "Wildcard IAM action detected",
                            "fix_code": "Replace Action: '*' with specific actions e.g. ['s3:GetObject', 's3:PutObject']"
                        })
                    elif 'acl' in line and 'public-read' in line:
                        findings.append({
                            "type": "IAC",
                            "severity": "CRITICAL",
                            "file": filename,
                            "line": i,
                            "description": "Public S3 bucket ACL detected",
                            "fix_code": "Set acl='private' and enable S3 Block Public Access"
                        })
                    elif '0.0.0.0/0' in line:
                        findings.append({
                            "type": "IAC",
                            "severity": "HIGH",
                            "file": filename,
                            "line": i,
                            "description": "Open security group ingress detected",
                            "fix_code": "Restrict cidr_blocks to specific IP ranges"
                        })
                    elif 'encrypted' in line and 'false' in line:
                        findings.append({
                            "type": "IAC",
                            "severity": "MEDIUM",
                            "file": filename,
                            "line": i,
                            "description": "Unencrypted resource detected",
                            "fix_code": "Set encrypted=true"
                        })
                        
            elif filename.endswith((".yaml", ".yml")):
                for i, line in enumerate(lines, 1):
                    if 'Action' in line and ("'*'" in line or '"*"' in line):
                        findings.append({
                            "type": "IAC",
                            "severity": "CRITICAL",
                            "file": filename,
                            "line": i,
                            "description": "Wildcard IAM action in CloudFormation",
                            "fix_code": "Replace with specific IAM actions"
                        })
                    elif 'PublicReadAcl' in line or 'public-read' in line:
                        findings.append({
                            "type": "IAC",
                            "severity": "CRITICAL",
                            "file": filename,
                            "line": i,
                            "description": "Public S3 ACL in CloudFormation",
                            "fix_code": "Remove public ACL, enable BlockPublicAcls"
                        })
                        
        return findings
