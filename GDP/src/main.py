import sys
import os
from pathlib import Path

current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from ui.app import run_app

if __name__ == "__main__":
    run_app()