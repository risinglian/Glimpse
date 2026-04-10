"""
Glimpse - AI 驱动的桌面级记忆检索系统
程序唯一入口，初始化 UI、数据库与全局路径

启动顺序：
1. 初始化容器（container）
2. 初始化路径（path_manager）
3. 初始化数据库（sqlite + chroma）
4. 初始化服务（ocr、embedding、ai）
5. 初始化任务队列
6. 启动 UI
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMessageBox


def main():
    from container import container

    print("Initializing container...")
    container.initialize_defaults()

    print("Initializing path manager...")
    from config.path_manager import path_manager

    print("Initializing databases...")
    from db.sqlite_manager import sqlite_manager
    from db.chroma_manager import chroma_manager

    print("Initializing services...")
    from services.ocr_engine import ocr_engine
    from services.ai_client import ai_client
    from services.search_service import search_service

    print("Initializing task queue...")
    from core.task_queue import task_queue

    print("Initializing keyboard manager...")
    from services.keyboard_manager import keyboard_manager
    from config.settings_manager import settings_manager

    screenshot_hotkey = settings_manager.get("hotkeys.screenshot", "<ctrl>+<shift>+g")

    def on_screenshot():
        print("Global screenshot shortcut pressed!")
        capture_manager = container.get("capture_manager")
        capture_manager.capture_fullscreen()

    keyboard_manager.register_hotkey(screenshot_hotkey, on_screenshot)
    keyboard_manager.start_listening()
    print(f"Global hotkey registered: {screenshot_hotkey}")

    print("Starting UI...")
    app = QApplication(sys.argv)
    app.setApplicationName("Glimpse")
    app.setOrganizationName("Glimpse")

    from ui.main_window import MainWindow

    try:
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        QMessageBox.critical(
            None,
            "启动失败",
            f"应用启动时发生错误：\n{str(e)}",
            QMessageBox.Ok
        )
        raise
    finally:
        container.shutdown()


if __name__ == "__main__":
    main()
