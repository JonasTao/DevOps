import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.utils.logger import logger

def main():
    logger.info("=" * 60)
    logger.info("AutoOps 自动化运维工具启动")
    logger.info("=" * 60)
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    logger.info("应用窗口已启动")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
