"""Ensure Playwright Chromium browser is installed."""

from __future__ import annotations

import os
import subprocess
import sys
import threading

_install_lock = threading.Lock()
_chromium_ready = False


def _chromium_executable_path() -> str | None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None

    try:
        with sync_playwright() as pw:
            path = pw.chromium.executable_path
            return path if path and os.path.isfile(path) else None
    except Exception:
        return None


def _verify_chromium_launch() -> bool:
    """Quick launch test — catches corrupt or incomplete browser downloads."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            browser.close()
        return True
    except Exception as exc:
        print(f"[Playwright] Chromium launch test failed: {exc}")
        return False


def install_chromium() -> None:
    """Download Chromium via `python -m playwright install chromium`."""
    print("[Playwright] Chromium chưa có — đang tải tự động (lần đầu có thể mất vài phút)...")
    cmd = [sys.executable, "-m", "playwright", "install", "chromium"]
    subprocess.run(cmd, check=True)

    if sys.platform == "linux":
        print("[Playwright] Installing Linux system dependencies...")
        subprocess.run(
            [sys.executable, "-m", "playwright", "install-deps", "chromium"],
            check=False,
        )

    print("[Playwright] Chromium đã cài xong.")


def ensure_chromium_installed() -> None:
    """Install Chromium if missing or broken."""
    global _chromium_ready

    if _chromium_ready:
        return

    with _install_lock:
        if _chromium_ready:
            return

        if _chromium_executable_path() and _verify_chromium_launch():
            _chromium_ready = True
            return

        if _chromium_executable_path():
            print("[Playwright] Chromium binary found but launch failed — reinstalling...")

        install_chromium()

        if not _chromium_executable_path():
            raise RuntimeError(
                "Chromium vẫn chưa sẵn sàng sau khi cài. "
                "Thử chạy thủ công: python -m playwright install chromium"
            )

        if not _verify_chromium_launch():
            raise RuntimeError(
                "Chromium đã tải nhưng không khởi động được. "
                "Đóng mọi cửa sổ Chromium cũ rồi thử lại."
            )

        _chromium_ready = True
