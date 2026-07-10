#!/usr/bin/env python3
"""Check and optionally install runtime dependencies for this skill."""

from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path


DEPENDENCIES = [
    {
        "import_name": "markdown",
        "package_name": "markdown",
        "used_by": "format.py",
        "required_for": "Markdown to WeChat HTML formatting",
    },
    {
        "import_name": "requests",
        "package_name": "requests",
        "used_by": "publish.py, comment_reply.py",
        "required_for": "WeChat API publishing and comment replies",
    },
]


def is_available(import_name: str) -> bool:
    return importlib.util.find_spec(import_name) is not None


def install_packages(packages: list[str]) -> int:
    command = [sys.executable, "-m", "pip", "install", *packages]
    print("Installing missing packages with:")
    print("  " + " ".join(command))
    return subprocess.call(command)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check wechat-format Python dependencies."
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install missing packages with the current Python interpreter.",
    )
    args = parser.parse_args()

    print(f"Python: {sys.executable}")
    print(f"Version: {sys.version.split()[0]}")

    missing = []
    for dep in DEPENDENCIES:
        if is_available(dep["import_name"]):
            print(f"[OK] {dep['package_name']} ({dep['used_by']})")
        else:
            print(
                f"[MISSING] {dep['package_name']} - "
                f"{dep['required_for']} ({dep['used_by']})"
            )
            missing.append(dep["package_name"])

    if not missing:
        print("All dependencies are available.")
        return 0

    print("\nMissing packages:")
    for package in missing:
        print(f"  - {package}")

    if not args.install:
        script_path = Path(__file__).resolve()
        print("\nInstall them with:")
        print(f"  {sys.executable} -m pip install {' '.join(missing)}")
        print("\nOr run:")
        print(f"  {sys.executable} {script_path} --install")
        return 1

    return install_packages(missing)


if __name__ == "__main__":
    raise SystemExit(main())
