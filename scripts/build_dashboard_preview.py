"""Build the interactive, server-free Strategy Lab for GitHub Pages.

Run ``npm ci --prefix web`` once before this command. The root and historical
/dashboard/ URL both serve the same application, including relative assets.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from export_web_data import export

ROOT = Path(__file__).resolve().parents[1]


def build_preview(output_root: Path) -> None:
    export(ROOT / "web" / "public" / "data")
    subprocess.run(["npm", "run", "build"], cwd=ROOT / "web", check=True)
    distribution = ROOT / "web" / "dist"
    output_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(distribution, output_root, dirs_exist_ok=True)
    shutil.copytree(distribution, output_root / "dashboard", dirs_exist_ok=True)
    (output_root / ".nojekyll").touch()


if __name__ == "__main__":
    build_preview(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "build" / "site")
