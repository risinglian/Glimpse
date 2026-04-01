"""
Glimpse - AI 桌面记忆助手
程序唯一入口，初始化 UI、数据库与全局路径
"""
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication

from config.path_manager import path_manager
from ui.signals import signals


def main():
    path_manager

    app = QApplication(sys.argv)
    app.setApplicationName("Glimpse")
    app.setOrganizationName("Glimpse")

    from ui.main_window import MainWindow
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
