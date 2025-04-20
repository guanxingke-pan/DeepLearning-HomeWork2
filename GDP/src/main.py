import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

# 导入run_app函数而不是GdpApp类
from ui.app import run_app

if __name__ == "__main__":
    run_app()