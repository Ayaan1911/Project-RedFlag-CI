from dataclasses import dataclass

@dataclass
class Finding:
    layer: str
    severity: str
    file: str
    line: int
    description: str
    fix: str

def audit_iac(files: list[dict]) -> list[Finding]:
    findings = []
    
    for file_obj in files:
        filename = file_obj.get("filename", "")
        content = file_obj.get("content", "")
        
        if not filename.endswith((".tf", ".yaml", ".yml")):
            continue
            
        lines = content.split("\n")
        
        if filename.endswith(".tf"):
            for i, line in enumerate(lines):
                if 'Action' in line and '*' in line:
                    findings.append(Finding(
                        layer="G",
                        severity="critical",
                        file=filename,
                        line=i + 1,
                        description="Wildcard IAM action detected",
                        fix="Replace Action: '*' with specific actions e.g. ['s3:GetObject', 's3:PutObject']"
                    ))
                elif 'acl' in line and 'public-read' in line:
                    findings.append(Finding(
                        layer="G",
                        severity="critical",
                        file=filename,
                        line=i + 1,
                        description="Public S3 bucket ACL detected",
                        fix="Set acl='private' and enable S3 Block Public Access"
                    ))
                elif '0.0.0.0/0' in line:
                    findings.append(Finding(
                        layer="G",
                        severity="high",
                        file=filename,
                        line=i + 1,
                        description="Open security group ingress detected",
                        fix="Restrict cidr_blocks to specific IP ranges"
                    ))
                elif 'encrypted' in line and 'false' in line:
                    findings.append(Finding(
                        layer="G",
                        severity="medium",
                        file=filename,
                        line=i + 1,
                        description="Unencrypted resource detected",
                        fix="Set encrypted=true"
                    ))
                    
        elif filename.endswith((".yaml", ".yml")):
            for i, line in enumerate(lines):
                if 'Action' in line and ("'*'" in line or '"*"' in line):
                    findings.append(Finding(
                        layer="G",
                        severity="critical",
                        file=filename,
                        line=i + 1,
                        description="Wildcard IAM action in CloudFormation",
                        fix="Replace with specific IAM actions"
                    ))
                elif 'PublicReadAcl' in line or 'public-read' in line:
                    findings.append(Finding(
                        layer="G",
                        severity="critical",
                        file=filename,
                        line=i + 1,
                        description="Public S3 ACL in CloudFormation",
                        fix="Remove public ACL, enable BlockPublicAcls"
                    ))
                    
    return findings
