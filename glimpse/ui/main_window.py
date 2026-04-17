"""Glimpse Main Window
主窗口实现
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QScrollArea, QFrame,
    QMessageBox, QStatusBar
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QFont


class MemoryCard(QFrame):
    """记忆卡片组件

    显示单个记忆的缩略图、AI 总结和时间戳
    """

    clicked = pyqtSignal()

    def __init__(self, summary: str, timestamp: str, parent=None):
        super().__init__(parent)
        self.summary = summary
        self.timestamp = timestamp
        self._setup_ui()

    def _setup_ui(self):
        """初始化卡片UI"""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: #ffffff;
                margin: 2px;
            }
            QFrame:hover {
                background-color: #f8f9fa;
                border-color: #2196F3;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # 截图缩略图占位
        self.thumbnail = QLabel()
        self.thumbnail.setFixedSize(240, 135)
        self.thumbnail.setStyleSheet("""
            QLabel {
                border: 2px dashed #bdbdbd;
                border-radius: 6px;
                background-color: #eeeeee;
            }
        """)
        self.thumbnail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail.setText("📷\n截图预览")
        layout.addWidget(self.thumbnail, 0, Qt.AlignmentFlag.AlignCenter)

        # AI 总结文本
        self.summary_label = QLabel(self.summary)
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet("""
            QLabel {
                color: #212121;
                font-size: 13px;
                line-height: 1.4;
            }
        """)
        layout.addWidget(self.summary_label)

        # 时间戳
        self.timestamp_label = QLabel(self.timestamp)
        self.timestamp_label.setStyleSheet("""
            QLabel {
                color: #757575;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.timestamp_label, 0, Qt.AlignmentFlag.AlignRight)

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        self.clicked.emit()
        super().mousePressEvent(event)


class EmptyStateWidget(QWidget):
    """空状态组件

    显示在无记忆时的提示界面
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """初始化空状态UI"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        # 图标
        icon_label = QLabel("🧠")
        icon_label.setStyleSheet("font-size: 64px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # 标题
        title_label = QLabel("暂无记忆")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #424242;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 提示文本
        hint_label = QLabel("按 Ctrl+Shift+S 开始截屏")
        hint_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #757575;
            }
        """)
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint_label)


class MainWindow(QMainWindow):
    """Glimpse 主窗口"""

    def __init__(self):
        super().__init__()
        self.memory_cards = []
        self._setup_ui()

    def _setup_ui(self):
        """设置主窗口UI"""
        # 窗口基本属性
        self.setWindowTitle("Glimpse - AI 桌面记忆助手")
        self.setMinimumSize(500, 600)
        self.resize(600, 750)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # ========== 顶部搜索区域 ==========
        search_widget = QWidget()
        search_layout = QHBoxLayout(search_widget)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入自然语言查询，如：'昨天关于设计的内容'...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 16px;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                font-size: 14px;
                background-color: #fafafa;
                color: #212121;
            }
            QLineEdit:focus {
                border-color: #2196F3;
                background-color: #ffffff;
            }
        """)
        self.search_input.returnPressed.connect(self._on_search)
        search_layout.addWidget(self.search_input)

        self.search_button = QPushButton("🔍 搜索")
        self.search_button.setFixedSize(100, 44)
        self.search_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        self.search_button.clicked.connect(self._on_search)
        search_layout.addWidget(self.search_button)

        main_layout.addWidget(search_widget)

        # ========== 中间内容区域 ==========
        self.content_stack = QVBoxLayout()
        self.content_stack.setContentsMargins(0, 0, 0, 0)

        # 空状态组件
        self.empty_state = EmptyStateWidget()
        self.content_stack.addWidget(self.empty_state)

        # 滚动区域（用于显示卡片列表）
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVisible(False)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #f5f5f5;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #bdbdbd;
                border-radius: 6px;
                min-height: 30px;
            }
        """)

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setSpacing(12)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.cards_container)
        self.content_stack.addWidget(self.scroll_area)

        main_layout.addLayout(self.content_stack, 1)

        # ========== 底部状态栏 ==========
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #f5f5f5;
                color: #616161;
                font-size: 12px;
                border-top: 1px solid #e0e0e0;
            }
        """)
        self.setStatusBar(self.status_bar)
        self._update_status("就绪")

        # ========== 菜单栏 ==========
        self._create_menu_bar()

    def _create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #ffffff;
                border-bottom: 1px solid #e0e0e0;
            }
            QMenuBar::item {
                padding: 6px 12px;
            }
            QMenuBar::item:selected {
                background-color: #e3f2fd;
            }
        """)

        # ========== 文件菜单 ==========
        file_menu = menubar.addMenu("文件(&F)")

        import_action = QAction("📥 导入截图", self)
        import_action.triggered.connect(self._on_import_screenshot)
        file_menu.addAction(import_action)

        export_action = QAction("📤 导出记忆", self)
        export_action.triggered.connect(self._on_export_memories)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("🚪 退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # ========== 设置菜单 ==========
        settings_menu = menubar.addMenu("设置(&S)")

        preferences_action = QAction("⚙️ 偏好设置", self)
        preferences_action.setShortcut("Ctrl+,")
        preferences_action.triggered.connect(self._open_settings)
        settings_menu.addAction(preferences_action)

        # ========== 帮助菜单 ==========
        help_menu = menubar.addMenu("帮助(&H)")

        about_action = QAction("ℹ️ 关于 Glimpse", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _on_search(self):
        """执行搜索"""
        query = self.search_input.text().strip()
        if query:
            print(f"[搜索] 查询词: {query}")
            self._update_status(f"搜索中: '{query}'")
        else:
            self._update_status("就绪")

    def _update_status(self, message: str):
        """更新状态栏"""
        self.status_bar.showMessage(message, 0)

    def _on_import_screenshot(self):
        """导入截图"""
        print("[导入] 导入功能开发中")

    def _on_export_memories(self):
        """导出记忆"""
        print("[导出] 导出功能开发中")

    def _open_settings(self):
        """打开设置对话框"""
        from .settings_dialog import SettingsDialog

        dialog = SettingsDialog(self)
        dialog.exec()

    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 Glimpse",
            """
            <h2>Glimpse</h2>
            <h3>AI 桌面记忆助手</h3>
            <p><b>版本:</b> 1.0.0</p>
            <p>全局快捷键截屏，AI 自动分析并存储，<br>支持自然语言搜索历史记忆。</p>
            <hr>
            <p style="color: #757575;">© 2026 Glimpse Project</p>
            """
        )

    def _show_content(self):
        """显示内容区域，隐藏空状态"""
        self.empty_state.setVisible(False)
        self.scroll_area.setVisible(True)

    def _show_empty_state(self):
        """显示空状态，隐藏内容区域"""
        self.empty_state.setVisible(True)
        self.scroll_area.setVisible(False)

    # ========== 公共方法 ==========

    def add_memory(self, summary: str, timestamp: str):
        """添加记忆卡片

        供其他模块调用，动态添加记忆到列表

        Args:
            summary: AI 生成的记忆摘要
            timestamp: 时间戳字符串
        """
        # 切换到内容视图
        if self.empty_state.isVisible():
            self._show_content()

        # 创建卡片
        card = MemoryCard(summary, timestamp)
        card.clicked.connect(lambda: print(f"[卡片点击] 时间: {timestamp}"))

        # 添加到列表顶部
        self.cards_layout.insertWidget(0, card)
        self.memory_cards.append(card)

        # 更新状态
        self._update_status(f"已添加 {len(self.memory_cards)} 条记忆")

    def clear_memories(self):
        """清空所有记忆"""
        for card in self.memory_cards:
            card.setParent(None)
        self.memory_cards.clear()
        self._show_empty_state()
        self._update_status("就绪")

    def get_memory_count(self) -> int:
        """获取记忆数量"""
        return len(self.memory_cards)
