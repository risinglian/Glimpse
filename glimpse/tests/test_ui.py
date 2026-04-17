"""Glimpse UI Tests
使用 pytest 和 pytest-qt 进行 UI 测试
"""

import pytest
from PyQt6.QtWidgets import QApplication, QLabel
from pytestqt import qtbot


# ========== Fixtures ==========

@pytest.fixture(scope="session")
def app(qtbot):
    """创建 QApplication 实例（会话级别，复用）"""
    test_app = QApplication.instance()
    if test_app is None:
        test_app = QApplication([])
    yield test_app


@pytest.fixture
def main_window(app, qtbot):
    """创建主窗口实例"""
    from ui.main_window import MainWindow
    window = MainWindow()
    qtbot.addWidget(window)
    return window


# ========== 主窗口测试 ==========

class TestMainWindow:
    """主窗口测试类"""

    def test_window_opens(self, main_window):
        """测试：主窗口能正常打开"""
        assert main_window is not None
        assert main_window.windowTitle() == "Glimpse - AI 桌面记忆助手"

    def test_window_has_minimum_size(self, main_window):
        """测试：主窗口有最小尺寸"""
        assert main_window.minimumWidth() >= 500
        assert main_window.minimumHeight() >= 600

    def test_empty_state_shows_icon(self, main_window):
        """测试：空状态显示图标"""
        assert main_window.empty_state.isVisible()
        # 检查空状态中的图标标签
        icon_label = main_window.empty_state.findChild(QLabel)
        assert icon_label is not None
        assert "🧠" in icon_label.text()

    def test_empty_state_shows_title(self, main_window):
        """测试：空状态显示标题"暂无记忆""" """
        # 获取空状态中的所有标签
        labels = main_window.empty_state.findChildren(QLabel)
        # 找到包含"暂无记忆"的标签
        title_found = any("暂无记忆" in label.text() for label in labels)
        assert title_found, "未找到'暂无记忆'标题"

    def test_empty_state_shows_hint(self, main_window):
        """测试：空状态显示快捷键提示"""
        labels = main_window.empty_state.findChildren(QLabel)
        # 找到包含快捷键提示的标签
        hint_found = any("Ctrl+Shift+S" in label.text() for label in labels)
        assert hint_found, "未找到快捷键提示"

    def test_has_search_input(self, main_window):
        """测试：主窗口有搜索输入框"""
        assert hasattr(main_window, 'search_input')
        assert main_window.search_input.placeholderText() != ""

    def test_has_search_button(self, main_window):
        """测试：主窗口有搜索按钮"""
        assert hasattr(main_window, 'search_button')
        assert main_window.search_button.text() == "🔍 搜索"

    def test_has_status_bar(self, main_window):
        """测试：主窗口有状态栏"""
        assert main_window.statusBar() is not None

    def test_search_prints_to_console(self, main_window, qtbot, capsys):
        """测试：搜索操作打印到控制台"""
        main_window.search_input.setText("test query")
        main_window._on_search()

        # 捕获控制台输出
        captured = capsys.readouterr()
        assert "[搜索]" in captured.out
        assert "test query" in captured.out

    def test_add_memory_switches_from_empty_state(self, main_window):
        """测试：添加记忆后从空状态切换到内容视图"""
        # 初始状态应该是空状态可见
        assert main_window.empty_state.isVisible()
        assert not main_window.scroll_area.isVisible()

        # 添加记忆
        main_window.add_memory("测试摘要", "2026-04-17 12:00:00")

        # 应该切换到内容视图
        assert not main_window.empty_state.isVisible()
        assert main_window.scroll_area.isVisible()
        assert len(main_window.memory_cards) == 1

    def test_clear_memories_returns_to_empty_state(self, main_window):
        """测试：清空记忆后返回空状态"""
        # 先添加一条记忆
        main_window.add_memory("测试摘要", "2026-04-17 12:00:00")

        # 清空记忆
        main_window.clear_memories()

        # 应该返回空状态
        assert main_window.empty_state.isVisible()
        assert not main_window.scroll_area.isVisible()
        assert len(main_window.memory_cards) == 0


# ========== 设置对话框测试 ==========

class TestSettingsDialog:
    """设置对话框测试类"""

    def test_dialog_opens(self, main_window, qtbot):
        """测试：设置对话框能正常打开"""
        from ui.settings_dialog import SettingsDialog

        dialog = SettingsDialog(main_window)
        qtbot.addWidget(dialog)

        assert dialog.windowTitle() == "设置"
        assert dialog.isModal()

    def test_dialog_has_hotkey_setting(self, main_window):
        """测试：对话框有快捷键设置"""
        from ui.settings_dialog import SettingsDialog

        dialog = SettingsDialog(main_window)
        settings = dialog.get_settings()

        assert "hotkey" in settings
        assert settings["hotkey"] == "Ctrl+Shift+S"


# ========== 信号总线测试 ==========

class TestSignals:
    """信号总线测试类"""

    def test_get_signals_returns_singleton(self, app):
        """测试：get_signals 返回单例"""
        from ui.signals import get_signals

        signals1 = get_signals()
        signals2 = get_signals()
        assert signals1 is signals2

    def test_screenshot_taken_signal(self, app, qtbot):
        """测试：screenshot_taken 信号"""
        from ui.signals import get_signals

        signals = get_signals()
        received = []

        def handler(path, summary):
            received.append((path, summary))

        signals.screenshot_taken.connect(handler)

        with qtbot.wait_signal(signals.screenshot_taken):
            signals.screenshot_taken.emit("/path/to/screenshot.png", "AI摘要")

        assert received == [("/path/to/screenshot.png", "AI摘要")]

    def test_search_triggered_signal(self, app, qtbot):
        """测试：search_triggered 信号"""
        from ui.signals import get_signals

        signals = get_signals()
        received = []

        def handler(query):
            received.append(query)

        signals.search_triggered.connect(handler)

        with qtbot.wait_signal(signals.search_triggered):
            signals.search_triggered.emit("test query")

        assert received == ["test query"]

    def test_status_updated_signal(self, app, qtbot):
        """测试：status_updated 信号"""
        from ui.signals import get_signals

        signals = get_signals()
        received = []

        def handler(message):
            received.append(message)

        signals.status_updated.connect(handler)

        with qtbot.wait_signal(signals.status_updated):
            signals.status_updated.emit("test status")

        assert received == ["test status"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
