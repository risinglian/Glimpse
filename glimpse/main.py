"""Glimpse - AI Desktop Memory Assistant
Application Entry Point
"""

import sys
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

from ui.main_window import MainWindow


def handle_exception(exc_type, exc_value, exc_traceback):
    """全局异常捕获"""
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))

    print(f"[错误] {exc_type.__name__}: {exc_value}")
    print(error_msg)

    # 显示错误对话框
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle("程序错误")
    msg_box.setText("程序运行时发生错误")
    msg_box.setDetailedText(error_msg)
    msg_box.exec()


def main():
    """主函数"""
    # 设置全局异常捕获
    sys.excepthook = handle_exception

    # 创建应用
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("Glimpse")
    app.setOrganizationName("GlimpseProject")

    # 创建并显示主窗口
    window = MainWindow()
    window.show()

    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
