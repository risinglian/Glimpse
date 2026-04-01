"""
Main Window - 主窗体与布局
"""
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QListWidget, QTextEdit
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction

from ui.signals import signals


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Glimpse - AI 桌面记忆助手")
        self.setMinimumSize(900, 600)

        self._current_memories = []
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._do_search)

        self._setup_ui()
        self._setup_shortcuts()
        self._setup_tray_icon()
        self._connect_signals()
        self._load_memories()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        toolbar = QWidget()
        toolbar_layout = QVBoxLayout(toolbar)

        self.screenshot_btn = QPushButton("截图 (Ctrl+Shift+G)")
        self.screenshot_btn.clicked.connect(self._on_screenshot)
        toolbar_layout.addWidget(self.screenshot_btn)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索记忆... (Ctrl+F)")
        self.search_input.textChanged.connect(self._on_search_text_changed)
        toolbar_layout.addWidget(self.search_input)

        layout.addWidget(toolbar)

        self.memory_list = QListWidget()
        self.memory_list.itemClicked.connect(self._on_memory_selected)
        layout.addWidget(self.memory_list)

        self.detail_panel = QTextEdit()
        self.detail_panel.setReadOnly(True)
        layout.addWidget(self.detail_panel)

        self.status_bar = QLabel("就绪")
        self.statusBar().addWidget(self.status_bar)

    def _setup_shortcuts(self):
        from PySide6.QtGui import QShortcut, QKeySequence

        self.search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self.search_shortcut.activated.connect(lambda: self.search_input.setFocus())

        self.screenshot_shortcut = QShortcut(QKeySequence("Ctrl+Shift+G"), self)
        self.screenshot_shortcut.activated.connect(self._on_screenshot)

        self.clear_shortcut = QShortcut(QKeySequence("Escape"), self)
        self.clear_shortcut.activated.connect(self._clear_search)

    def _setup_tray_icon(self):
        from PySide6.QtWidgets import QSystemTrayIcon
        from PySide6.QtGui import QIcon, QPixmap, QPainter

        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.blue)
        icon = QIcon(pixmap)

        self.tray_icon = QSystemTrayIcon(icon, self)
        self.tray_icon.activated.connect(self._on_tray_activated)

        menu = self.menuBar().addMenu("文件")
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.close)
        menu.addAction(quit_action)

    def _connect_signals(self):
        signals.screenshot_completed.connect(self._on_screenshot_complete)
        signals.memory_saved.connect(self._on_memory_saved)
        signals.search_completed.connect(self._on_search_completed)
        signals.error_occurred.connect(self._on_error)
        signals.status_updated.connect(self._on_status_updated)

    def _load_memories(self):
        from db.sqlite_manager import sqlite_manager
        self._current_memories = sqlite_manager.get_all_memories(limit=100)
        self._update_memory_list()

    def _update_memory_list(self):
        self.memory_list.clear()
        for memory in self._current_memories:
            self.memory_list.addItem(f"{memory.created_at[:19]} - {memory.ai_summary[:50]}...")

    def _on_thumbnail_loaded(self, memory_id, pixmap):
        pass

    def _on_screenshot(self):
        signals.screenshot_requested.emit()

    def _on_screenshot_complete(self, image_path: str):
        self.status_bar.setText(f"截图完成: {image_path}")
        self._load_memories()

    def _on_search_text_changed(self, text: str):
        self._search_timer.start(300)

    def _do_search(self):
        query = self.search_input.text().strip()
        if not query:
            self._current_memories = []
            from db.sqlite_manager import sqlite_manager
            self._current_memories = sqlite_manager.get_all_memories(limit=100)
        else:
            from db.sqlite_manager import sqlite_manager
            self._current_memories = sqlite_manager.search_memories(query)
        self._update_memory_list()

    def _clear_search(self):
        self.search_input.clear()
        self._do_search()

    def _on_memory_selected(self, item):
        index = self.memory_list.row(item)
        if 0 <= index < len(self._current_memories):
            memory = self._current_memories[index]
            self.detail_panel.setText(
                f"时间: {memory.created_at}\n"
                f"应用: {memory.app_name}\n"
                f"摘要: {memory.ai_summary}\n"
                f"图片: {memory.image_path}"
            )

    def _on_memory_saved(self, memory_id: str):
        self.status_bar.setText(f"记忆已保存: {memory_id}")
        self._load_memories()

    def _on_search_completed(self, results: list):
        self._current_memories = results
        self._update_memory_list()

    def _on_error(self, error_msg: str):
        self.status_bar.setText(f"错误: {error_msg}")

    def _on_status_updated(self, status: str):
        self.status_bar.setText(status)

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.showNormal()
            self.activateWindow()


def main():
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
