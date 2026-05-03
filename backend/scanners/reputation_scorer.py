"""
reputation_scorer.py — Dependency Reputation Scanner (Problem 1.5 extension)
Owner: Nikhil Virdi (NV)

Extends hallucinated package detection to a full trust scoring system.
A package that exists with 3 downloads, created yesterday, and no GitHub
repo is equally dangerous as a non-existent package.

Trust Levels:
  TRUSTED:    downloads > 10000/week AND age > 180 days AND has_repo
  SUSPICIOUS: downloads < 1000/week OR age < 30 days OR no repo
  DANGEROUS:  downloads < 100/week AND age < 7 days (typosquat profile)
"""

import logging
from datetime import datetime, timezone

import httpx

logger = logging.getLogger(__name__)

# ─── Trust Thresholds ────────────────────────────────────

TRUSTED_MIN_DOWNLOADS = 10000
SUSPICIOUS_MAX_DOWNLOADS = 1000
DANGEROUS_MAX_DOWNLOADS = 100
TRUSTED_MIN_AGE_DAYS = 180
SUSPICIOUS_MAX_AGE_DAYS = 30
DANGEROUS_MAX_AGE_DAYS = 7


class ReputationScorer:
    """Scores package reputation based on download count, age, and metadata."""

    def __init__(self):
        self._cache = {}

    async def score_npm_package(self, package_name: str) -> dict:
        """Score an npm package's reputation."""
        if package_name in self._cache:
            return self._cache[package_name]

        result = {
            "package": package_name,
            "ecosystem": "npm",
            "trust_level": "UNKNOWN",
            "weekly_downloads": 0,
            "package_age_days": 0,
            "has_repository": False,
            "maintainer_count": 0,
            "last_publish_days_ago": 0,
        }

        async with httpx.AsyncClient(timeout=10) as client:
            # 1. Get package metadata from npm
            try:
                meta_resp = await client.get(f"https://registry.npmjs.org/{package_name}")
                if meta_resp.status_code != 200:
                    result["trust_level"] = "DANGEROUS"
                    result["reason"] = "Package does not exist in npm registry"
                    self._cache[package_name] = result
                    return result

                meta = meta_resp.json()

                # Extract creation date
                time_data = meta.get("time", {})
                created_str = time_data.get("created", "")
                if created_str:
                    try:
                        created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                        result["package_age_days"] = (datetime.now(timezone.utc) - created).days
                    except Exception:
                        pass

                # Extract last publish date
                modified_str = time_data.get("modified", "")
                if modified_str:
                    try:
                        modified = datetime.fromisoformat(modified_str.replace("Z", "+00:00"))
                        result["last_publish_days_ago"] = (datetime.now(timezone.utc) - modified).days
                    except Exception:
                        pass

                # Check for repository
                latest_version = meta.get("dist-tags", {}).get("latest", "")
                versions = meta.get("versions", {})
                latest_data = versions.get(latest_version, {})
                repo = latest_data.get("repository", meta.get("repository"))
                result["has_repository"] = repo is not None and bool(repo)

                # Count maintainers
                maintainers = meta.get("maintainers", [])
                result["maintainer_count"] = len(maintainers)

            except Exception as e:
                logger.warning("npm metadata fetch failed for %s: %s", package_name, e)

            # 2. Get weekly download count
            try:
                dl_resp = await client.get(
                    f"https://api.npmjs.org/downloads/point/last-week/{package_name}"
                )
                if dl_resp.status_code == 200:
                    result["weekly_downloads"] = dl_resp.json().get("downloads", 0)
            except Exception as e:
                logger.warning("npm downloads fetch failed for %s: %s", package_name, e)

        # 3. Calculate trust level
        result["trust_level"] = self._calculate_trust_level(result)
        self._cache[package_name] = result
        return result

    async def score_pypi_package(self, package_name: str) -> dict:
        """Score a PyPI package's reputation."""
        if package_name in self._cache:
            return self._cache[package_name]

        result = {
            "package": package_name,
            "ecosystem": "pypi",
            "trust_level": "UNKNOWN",
            "weekly_downloads": 0,
            "package_age_days": 0,
            "has_repository": False,
            "maintainer_count": 0,
            "last_publish_days_ago": 0,
        }

        async with httpx.AsyncClient(timeout=10) as client:
            # 1. Get package metadata from PyPI
            try:
                meta_resp = await client.get(f"https://pypi.org/pypi/{package_name}/json")
                if meta_resp.status_code != 200:
                    result["trust_level"] = "DANGEROUS"
                    result["reason"] = "Package does not exist in PyPI registry"
                    self._cache[package_name] = result
                    return result

                meta = meta_resp.json()
                info = meta.get("info", {})

                # Check repo
                project_urls = info.get("project_urls") or {}
                home_page = info.get("home_page", "")
                result["has_repository"] = bool(
                    project_urls.get("Source") or
                    project_urls.get("Repository") or
                    project_urls.get("GitHub") or
                    (home_page and "github" in home_page.lower())
                )

                # Package age from first release
                releases = meta.get("releases", {})
                all_dates = []
                for version, files in releases.items():
                    for f in files:
                        upload_time = f.get("upload_time_iso_8601") or f.get("upload_time")
                        if upload_time:
                            try:
                                dt = datetime.fromisoformat(upload_time.replace("Z", "+00:00"))
                                all_dates.append(dt)
                            except Exception:
                                pass

                if all_dates:
                    oldest = min(all_dates)
                    newest = max(all_dates)
                    result["package_age_days"] = (datetime.now(timezone.utc) - oldest).days
                    result["last_publish_days_ago"] = (datetime.now(timezone.utc) - newest).days

            except Exception as e:
                logger.warning("PyPI metadata fetch failed for %s: %s", package_name, e)

            # 2. Get download stats
            try:
                stats_resp = await client.get(
                    f"https://pypistats.org/api/packages/{package_name}/recent"
                )
                if stats_resp.status_code == 200:
                    data = stats_resp.json().get("data", {})
                    result["weekly_downloads"] = data.get("last_week", 0)
            except Exception as e:
                logger.warning("PyPI stats fetch failed for %s: %s", package_name, e)

        # 3. Calculate trust level
        result["trust_level"] = self._calculate_trust_level(result)
        self._cache[package_name] = result
        return result

    def _calculate_trust_level(self, data: dict) -> str:
        """
        Calculate trust level based on signals.
        
        TRUSTED:    downloads > 10K/week AND age > 180 days AND has_repo
        SUSPICIOUS: downloads < 1K/week OR age < 30 days OR no repo
        DANGEROUS:  downloads < 100/week AND age < 7 days
        """
        downloads = data.get("weekly_downloads", 0)
        age = data.get("package_age_days", 0)
        has_repo = data.get("has_repository", False)

        # DANGEROUS check first
        if downloads < DANGEROUS_MAX_DOWNLOADS and age < DANGEROUS_MAX_AGE_DAYS:
            return "DANGEROUS"

        # TRUSTED check
        if (downloads >= TRUSTED_MIN_DOWNLOADS and
                age >= TRUSTED_MIN_AGE_DAYS and
                has_repo):
            return "TRUSTED"

        # SUSPICIOUS if any red flag
        if (downloads < SUSPICIOUS_MAX_DOWNLOADS or
                age < SUSPICIOUS_MAX_AGE_DAYS or
                not has_repo):
            return "SUSPICIOUS"

        # Default to TRUSTED if no red flags
        return "TRUSTED"
