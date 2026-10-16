import asyncio

from app.config import Settings
from app.yue.updater import Updater, is_newer, version_from_tag


def test_version_from_tag():
    assert version_from_tag("yue2-v0.1.6") == "0.1.6"
    assert version_from_tag("v1.2") == "1.2"
    assert version_from_tag("nightly") is None


def test_is_newer():
    assert is_newer("0.1.7", "0.1.6")
    assert not is_newer("0.1.6", "0.1.6")
    assert not is_newer("0.1.5", "0.1.6")
    assert is_newer("0.1.0", None)


def test_mock_engine_never_installs_yue2():
    updater = Updater(Settings(engine="mock", auto_update=True))
    assert asyncio.run(updater.run()).state == "skipped"
