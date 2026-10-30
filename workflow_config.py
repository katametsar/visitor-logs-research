"""Public-release configuration; importing this module never reads visitor data."""
import os
from pathlib import Path


def workspace_root():
    value = os.environ.get("VISITOR_LOGS_WORKSPACE", "").strip()
    if not value:
        raise ValueError("Set VISITOR_LOGS_WORKSPACE to a separate existing restricted workspace.")
    root = Path(value).expanduser().resolve(strict=True)
    release = Path(__file__).resolve().parent
    if not root.is_dir() or root == release or release in root.parents or root in release.parents:
        raise ValueError("Workspace must be separate from the public source tree.")
    if (root / ".git").exists() or (root / "app.py").exists() or (root / "R" / "00_pipeline.R").exists():
        raise ValueError("Use a separate data workspace, never the original research repository.")
    for name in ("data_raw", "data_clean", "dashboard_data", "outputs", "visitor_map_clicker_v2"):
        if (root / name).is_symlink():
            raise ValueError("Workspace data directories must not be symbolic links.")
    return root


def device_sheet():
    return os.environ.get("VISITOR_LOGS_PYTHON_DEVICE_SHEET", "devices")
