import os
from pathlib import Path

APP_ROOT_DIR: Path = Path(os.path.abspath(__file__)).parents[2]

JSSP_DATA_PATH: str = os.path.join(APP_ROOT_DIR, "notebooks", "data", "jssp")
