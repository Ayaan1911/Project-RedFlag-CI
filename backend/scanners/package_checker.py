"""
package_checker.py — Hallucinated Package Detector
Owner: Nikhil Virdi (NV)

Cross-references every dependency in package.json and requirements.txt
against live npm and PyPI registries. Packages that return non-200
responses are flagged as hallucinated — potential supply chain attack vectors.
"""

import json
import re
import logging
import httpx

logger = logging.getLogger(__name__)

NPM_REGISTRY = "https://registry.npmjs.org/{}"
PYPI_REGISTRY = "https://pypi.org/pypi/{}/json"

# Cache to avoid redundant lookups within a single scan
_registry_cache: dict[str, bool] = {}


async def _check_npm(package_name: str, client: httpx.AsyncClient) -> bool:
    """Returns True if the package exists on npm, False if hallucinated."""
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
        return True  # Fail open — don't false-positive on network issues


async def _check_pypi(package_name: str, client: httpx.AsyncClient) -> bool:
    """Returns True if the package exists on PyPI, False if hallucinated."""
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


def _extract_npm_deps(content: str) -> list[str]:
    """Extract all dependency names from a package.json file."""
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
    """Extract package names from a requirements.txt file."""
    deps = []
    for line in content.split("\n"):
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        # Parse 'package==1.0.0', 'package>=1.0', 'package'
        match = re.match(r"^([a-zA-Z0-9_-]+)", line)
        if match:
            deps.append(match.group(1))
    return deps


class PackageChecker:
    """Checks npm and PyPI registries to detect hallucinated packages."""

    async def run(self, files: list[dict]) -> list[dict]:
        """Run package verification across all dependency files."""
        findings = []

        async with httpx.AsyncClient() as client:
            for file_info in files:
                filename = file_info.get("filename", "")
                content = file_info.get("content", "")

                if not content:
                    continue

                # ─── npm packages ───
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
                                "fix_code": f"// Remove '{dep}' from package.json dependencies.\n// Verify the correct package name on npmjs.com.",
                            })

                # ─── PyPI packages ───
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
                                "fix_code": f"# Remove '{dep}' from requirements.\n# Find the correct package at pypi.org.",
                            })

        logger.info("PackageChecker found %d hallucinated packages.", len(findings))
        return findings
