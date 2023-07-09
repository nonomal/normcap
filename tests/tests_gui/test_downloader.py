import os

import pytest
from pytestqt.qtbot import QtBot

from normcap.gui.downloader import Downloader, Worker


@pytest.mark.skipif(
    "GITHUB_ACTIONS" in os.environ, reason="Skip on Github Action Runner"
)
def test_downloader_retrieves_website(qtbot: QtBot):
    test_url = "https://www.google.com"
    downloader = Downloader()
    with qtbot.wait_signal(downloader.com.on_download_finished) as result:
        downloader.get(test_url)

    raw, url = result.args
    assert isinstance(raw, bytes)
    assert url == test_url

    text = raw.decode(encoding="utf-8", errors="ignore")
    assert "</html>" in text.lower()


def test_downloader_handles_not_existing_url(caplog, qtbot: QtBot):
    wrong_url = "https://not_existing_url.normcap"

    downloader = Downloader()

    with qtbot.assert_not_emitted(
        downloader.com.on_download_finished, wait=1500
    ), qtbot.wait_signal(downloader.com.on_download_failed) as result:
        downloader.get(wrong_url, timeout=0.5)

    assert result.signal_triggered
    assert wrong_url in result.args[0]
    assert "Exception" in result.args[0]


def test_worker_not_existing_url(qtbot):
    test_url = "https://does-not-exist-h4k8u4-p9v1m3-0kplnf.net"

    worker = Worker(test_url, timeout=1)
    with qtbot.waitSignal(worker.com.on_download_failed) as signal:
        worker.run()

    assert signal.args[0].startswith("Exception")
    assert signal.args[1] == test_url


def test_worker_existing_url(qtbot):
    test_url = "https://github.com"

    worker = Worker(test_url)
    with qtbot.waitSignal(worker.com.on_download_finished) as signal:
        worker.run()

    assert type(signal.args[0]) is bytes
    assert signal.args[1] == test_url
