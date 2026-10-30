"""Allow numbered scripts to run directly from any current directory."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workflow_config import workspace_root, device_sheet
