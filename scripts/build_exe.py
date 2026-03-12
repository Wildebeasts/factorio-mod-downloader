import os
import sys
import PyInstaller.__main__
from pathlib import Path

def build():
    # Base configuration
    project_root = Path(__file__).resolve().parent.parent
    name = "FactorioModDownloader"
    entry_point = str(project_root / "src" / "factorio_mod_downloader" / "__main__.py")
    icon = str(project_root / "factorio_downloader.ico")
    
    print(f"Building {name} from {entry_point}...")

    # Data files structure: (source, destination_in_bundle)
    # We map assets to "assets" so resource_path() works correctly
    datas = [
        (str(project_root / "src" / "factorio_mod_downloader" / "assets"), "assets"),
    ]

    # Packages that need all metadata and submodules collected (from pyproject.toml)
    collect_all = [
        "requests",
        "chromedriver_autoinstaller",
        "selenium",
        "customtkinter",
        "ctkmessagebox",
        "bs4",
        "PIL",
    ]

    # PyInstaller arguments
    args = [
        entry_point,
        f"--name={name}",
        "--onefile",
        "--windowed",
        f"--icon={icon}",
        "--noconfirm",
        "--clean",
    ]

    # Add data files
    for src, dst in datas:
        args.append(f"--add-data={src}{os.pathsep}{dst}")

    # Add package collections
    for package in collect_all:
        args.append("--collect-all")
        args.append(package)

    # Execute PyInstaller
    print(f"Running PyInstaller with arguments: {' '.join(args)}")
    PyInstaller.__main__.run(args)

if __name__ == "__main__":
    build()
