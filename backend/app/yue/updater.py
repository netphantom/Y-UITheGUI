"""Startup check: install or upgrade the YuE2 inference package from its GitHub releases.

Runs before the engine is imported, so the new code is what gets loaded. Model weights
need no handling here: ``from_pretrained`` already syncs them with the Hugging Face Hub.
A failed check never blocks startup; the already installed version keeps working.
"""

import asyncio
import logging
import re
import sys
from importlib.metadata import PackageNotFoundError, version

import httpx
from packaging.version import InvalidVersion, Version

from app.config import Settings
from app.db import utcnow
from app.schemas import UpdateInfo

log = logging.getLogger(__name__)

# Release tags look like "yue2-v0.1.6".
_TAG_VERSION = re.compile(r"(\d+(?:\.\d+)+)")


def installed_version(package: str) -> str | None:
    try:
        return version(package)
    except PackageNotFoundError:
        return None


def version_from_tag(tag: str) -> str | None:
    match = _TAG_VERSION.search(tag)
    return match.group(1) if match else None


def is_newer(candidate: str, current: str | None) -> bool:
    if current is None:
        return True
    try:
        return Version(candidate) > Version(current)
    except InvalidVersion:
        return candidate != current


class Updater:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.info = UpdateInfo(state="idle", installed_version=installed_version(settings.yue_package))

    async def run(self) -> UpdateInfo:
        if not self.settings.auto_update:
            return self._set("disabled", message="Auto update disabled (YUI_AUTO_UPDATE=false)")
        try:
            self._set("checking")
            tag = self.settings.yue_pinned_tag or await self._latest_release_tag()
            latest = version_from_tag(tag)
            self.info.latest_version = latest
            if latest is None or not is_newer(latest, self.info.installed_version):
                return self._set("up_to_date")
            self._set("installing", message=f"Installing {tag}")
            await self._pip_install(tag)
            self.info.installed_version = installed_version(self.settings.yue_package)
            return self._set("updated", message=f"Installed {tag}")
        except Exception as exc:  # network down, GitHub rate limit, pip failure...
            log.exception("YuE2 update check failed")
            return self._set("failed", message=str(exc))

    async def _latest_release_tag(self) -> str:
        url = f"https://api.github.com/repos/{self.settings.yue_repo}/releases/latest"
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url, headers={"Accept": "application/vnd.github+json"})
            response.raise_for_status()
            return response.json()["tag_name"]

    async def _pip_install(self, tag: str) -> None:
        requirement = (
            f"{self.settings.yue_package} @ "
            f"git+https://github.com/{self.settings.yue_repo}.git@{tag}"
        )
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "pip", "install", "--upgrade", requirement,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        output, _ = await process.communicate()
        if process.returncode != 0:
            raise RuntimeError(f"pip install failed:\n{output.decode()[-2000:]}")

    def _set(self, state: str, message: str | None = None) -> UpdateInfo:
        self.info.state = state
        self.info.message = message
        self.info.checked_at = utcnow()
        log.info("YuE2 update: %s %s", state, message or "")
        return self.info
