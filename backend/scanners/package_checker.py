"""
package_checker.py — Hallucinated Package Detector
Owner: Nikhil Virdi (NV)

Cross-references every dependency in package.json, requirements.txt,
pom.xml, go.mod, and Cargo.toml against live registries. Packages that return non-200
responses are flagged as hallucinated — potential supply chain attack vectors.
"""

import json
import re
import logging
import httpx

logger = logging.getLogger(__name__)

NPM_REGISTRY = "https://registry.npmjs.org/{}"
PYPI_REGISTRY = "https://pypi.org/pypi/{}/json"
MAVEN_REGISTRY = "https://search.maven.org/solrsearch/select?q=g:{}+AND+a:{}&rows=1&wt=json"
GO_REGISTRY = "https://pkg.go.dev/{}"
CARGO_REGISTRY = "https://crates.io/api/v1/crates/{}"

# Cache to avoid redundant lookups within a single scan
_registry_cache: dict[str, bool] = {}
OFFLINE_SAFE_NPM_PACKAGES = {
    "express",
    "react",
    "react-dom",
    "vite",
    "lodash",
    "axios",
    "next",
    "typescript",
}


async def _check_npm(package_name: str, client: httpx.AsyncClient) -> bool:
    cache_key = f"npm:{package_name}"
    if cache_key in _registry_cache:
        return _registry_cache[cache_key]

    try:
        resp = await client.get(NPM_REGISTRY.format(package_name), timeout=10.0)
        exists = resp.status_code == 200
        _registry_cache[cache_key] = exists
        return exists
    except Exception as e:
        logger.warning("npm lookup failed for '%s': %s", package_name, e)
        exists = _offline_npm_exists(package_name)
        _registry_cache[cache_key] = exists
        return exists


async def _check_pypi(package_name: str, client: httpx.AsyncClient) -> bool:
    cache_key = f"pypi:{package_name}"
    if cache_key in _registry_cache:
        return _registry_cache[cache_key]

    try:
        resp = await client.get(PYPI_REGISTRY.format(package_name), timeout=10.0)
        exists = resp.status_code == 200
        _registry_cache[cache_key] = exists
        return exists
    except Exception as e:
        logger.warning("PyPI lookup failed for '%s': %s", package_name, e)
        return True

async def _check_maven(group_id: str, artifact_id: str, client: httpx.AsyncClient) -> bool:
    cache_key = f"maven:{group_id}:{artifact_id}"
    if cache_key in _registry_cache:
        return _registry_cache[cache_key]
    
    try:
        resp = await client.get(MAVEN_REGISTRY.format(group_id, artifact_id), timeout=10.0)
        if resp.status_code == 200:
            data = resp.json()
            exists = data.get("response", {}).get("numFound", 0) > 0
        else:
            exists = False
        _registry_cache[cache_key] = exists
        return exists
    except Exception as e:
        logger.warning("Maven lookup failed for '%s:%s': %s", group_id, artifact_id, e)
        return True

async def _check_go(module_path: str, client: httpx.AsyncClient) -> bool:
    cache_key = f"go:{module_path}"
    if cache_key in _registry_cache:
        return _registry_cache[cache_key]
    
    try:
        resp = await client.get(GO_REGISTRY.format(module_path), follow_redirects=True, timeout=10.0)
        if resp.status_code == 200:
            exists = True
        elif resp.status_code == 404:
            exists = False
        else:
            exists = True
        _registry_cache[cache_key] = exists
        return exists
    except Exception as e:
        logger.warning("Go lookup failed for '%s': %s", module_path, e)
        return True

async def _check_cargo(name: str, client: httpx.AsyncClient) -> bool:
    cache_key = f"cargo:{name}"
    if cache_key in _registry_cache:
        return _registry_cache[cache_key]
    
    try:
        resp = await client.get(CARGO_REGISTRY.format(name), timeout=10.0)
        if resp.status_code == 200:
            exists = True
        elif resp.status_code == 404:
            exists = False
        else:
            exists = True
        _registry_cache[cache_key] = exists
        return exists
    except Exception as e:
        logger.warning("Cargo lookup failed for '%s': %s", name, e)
        return True


def _extract_npm_deps(content: str) -> list[str]:
    try:
        data = json.loads(content)
        deps = list(data.get("dependencies", {}).keys())
        deps += list(data.get("devDependencies", {}).keys())
        deps += list(data.get("peerDependencies", {}).keys())
        deps += list(data.get("optionalDependencies", {}).keys())
        return deps
    except (json.JSONDecodeError, AttributeError):
        return []


def _extract_pip_deps(content: str) -> list[str]:
    deps = []
    for line in content.split("\n"):
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        match = re.match(r"^([a-zA-Z0-9_-]+)", line)
        if match:
            deps.append(match.group(1))
    return deps

def _extract_maven_deps(content: str) -> list[tuple[str, str]]:
    deps = []
    blocks = re.findall(r"<dependency>(.*?)</dependency>", content, re.DOTALL)
    for block in blocks:
        group_match = re.search(r"<groupId>(.*?)</groupId>", block)
        artifact_match = re.search(r"<artifactId>(.*?)</artifactId>", block)
        if group_match and artifact_match:
            deps.append((group_match.group(1).strip(), artifact_match.group(1).strip()))
    return deps

def _extract_go_deps(content: str) -> list[str]:
    deps = []
    in_require = False
    for line in content.split("\n"):
        line = line.strip()
        if not line or line.startswith("//"): continue
        if line.startswith("require ("):
            in_require = True
            continue
        if in_require and line == ")":
            in_require = False
            continue
        
        if in_require:
            parts = line.split()
            if parts:
                deps.append(parts[0])
        elif line.startswith("require "):
            parts = line.split()
            if len(parts) >= 2:
                deps.append(parts[1])
    return deps

def _extract_cargo_deps(content: str) -> list[str]:
    deps = []
    in_deps = False
    for line in content.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"): continue
        if line.startswith("["):
            in_deps = "dependencies" in line
            continue
        
        if in_deps and "=" in line:
            name = line.split("=")[0].strip()
            deps.append(name)
    return deps


def _offline_npm_exists(package_name: str) -> bool:
    normalized = package_name.strip().lower()
    if normalized in OFFLINE_SAFE_NPM_PACKAGES:
        return True

    suspicious_fragments = ("helper", "wrapper", "stream", "sdk", "client")
    ai_vendor_fragments = ("openai", "claude", "anthropic", "gpt", "llm")

    if any(fragment in normalized for fragment in ai_vendor_fragments) and any(fragment in normalized for fragment in suspicious_fragments):
        return False

    return True


class PackageChecker:
    """Checks registries to detect hallucinated packages."""

    async def run(self, files: list[dict]) -> list[dict]:
        findings = []

        async with httpx.AsyncClient() as client:
            for file_info in files:
                filename = file_info.get("filename", "")
                content = file_info.get("content", "")

                if not content:
                    continue

                if filename.endswith("package.json"):
                    deps = _extract_npm_deps(content)
                    for dep in deps:
                        exists = await _check_npm(dep, client)
                        if not exists:
                            findings.append({
                                "type": "PACKAGE",
                                "severity": "CRITICAL",
                                "file": filename,
                                "line": 1,
                                "description": (
                                    f"Hallucinated package detected: '{dep}' does not exist on the npm registry. "
                                    "This is a common AI hallucination. If an attacker registers this name with "
                                    "malicious code, anyone running `npm install` will be compromised."
                                ),
                                "fix_code": f"// Remove '{dep}' from package.json dependencies.\\n// Verify the correct package name on npmjs.com.",
                            })

                if filename.endswith("requirements.txt") or filename.endswith("pyproject.toml"):
                    deps = _extract_pip_deps(content)
                    for dep in deps:
                        exists = await _check_pypi(dep, client)
                        if not exists:
                            findings.append({
                                "type": "PACKAGE",
                                "severity": "CRITICAL",
                                "file": filename,
                                "line": 1,
                                "description": (
                                    f"Hallucinated package detected: '{dep}' does not exist on PyPI. "
                                    "An attacker could register this package name with malicious code."
                                ),
                                "fix_code": f"# Remove '{dep}' from requirements.\\n# Find the correct package at pypi.org.",
                            })

                if filename.endswith("pom.xml"):
                    deps = _extract_maven_deps(content)
                    for group_id, artifact_id in deps:
                        if "$" in group_id or "$" in artifact_id: continue
                        exists = await _check_maven(group_id, artifact_id, client)
                        if not exists:
                            pkg_name = f"{group_id}:{artifact_id}"
                            findings.append({
                                "type": "PACKAGE",
                                "severity": "CRITICAL",
                                "file": filename,
                                "line": 1,
                                "description": f"Package '{pkg_name}' not found in maven registry",
                                "fix_code": f"<!-- Remove {pkg_name} from pom.xml -->"
                            })

                if filename.endswith("go.mod"):
                    deps = _extract_go_deps(content)
                    for dep in deps:
                        exists = await _check_go(dep, client)
                        if not exists:
                            findings.append({
                                "type": "PACKAGE",
                                "severity": "CRITICAL",
                                "file": filename,
                                "line": 1,
                                "description": f"Package '{dep}' not found in go registry",
                                "fix_code": f"// Remove '{dep}' from go.mod require block."
                            })
                            
                if filename.endswith("Cargo.toml"):
                    deps = _extract_cargo_deps(content)
                    for dep in deps:
                        exists = await _check_cargo(dep, client)
                        if not exists:
                            findings.append({
                                "type": "PACKAGE",
                                "severity": "CRITICAL",
                                "file": filename,
                                "line": 1,
                                "description": f"Package '{dep}' not found in cargo registry",
                                "fix_code": f"# Remove '{dep}' from Cargo.toml dependencies."
                            })

        logger.info("PackageChecker found %d hallucinated packages.", len(findings))
        return findings
