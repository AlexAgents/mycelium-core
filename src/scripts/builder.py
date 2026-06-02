"""
PyInstaller build helper.
"""

import os
import platform
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def clean():

    for folder in (
        "build",
        "dist",
        "__pycache__",
    ):

        path = ROOT / folder

        if path.exists():

            shutil.rmtree(
                path,
                ignore_errors=True,
            )


def build():

    separator = ";"

    if (
        platform.system()
        != "Windows"
    ):
        separator = ":"

    cmd = (
        "pyinstaller "
        "--noconfirm "
        "--windowed "
        "--name MYCELIUM_CORE "
        "--icon src/assets/icons/app.ico "
        f"--add-data "
        f"\"src/ui/themes"
        f"{separator}"
        f"src/ui/themes\" "
        f"--add-data "
        f"\"src/ui/i18n"
        f"{separator}"
        f"src/ui/i18n\" "
        "main.py"
    )

    os.system(cmd)


def main():

    clean()

    build()


if __name__ == "__main__":
    main()