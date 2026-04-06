"""
设置对话框
提供图形界面让用户修改配置
"""
import copy
import re
from typing import Dict, Any, Optional, Callable
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QWidget, QFormLayout, QLineEdit, QSpinBox,
    QDoubleSpinBox, QComboBox, QCheckBox, QPushButton,
    QLabel, QMessageBox, QGroupBox, QScrollArea
)
from PySide6.QtCore import Qt


class SettingsDialog(QDialog):
    """设置对话框"""

    HOTKEY_PATTERN = re.compile(r'^(<[^>]+>(\+<[^>]+>)*|\w+)$')

    def __init__(
        self,
        settings_manager,
        keyboard_manager,
        capture_manager,
        task_queue,
        parent=None
    ):
        super().__init__(parent)
        self._settings_manager = settings_manager
        self._keyboard_manager = keyboard_manager
        self._capture_manager = capture_manager
        self._task_queue = task_queue

        self._original_settings = settings_manager.get_all()
        self._pending_settings = copy.deepcopy(self._original_settings)
        self._degraded_services = []

        self._screenshot_callback: Optional[Callable] = None

        self._init_ui()
        self._load_current_settings()

    def _get_screenshot_callback(self) -> Callable:
        """懒加载截图回调函数（缓存）"""
        if self._screenshot_callback is None:
            def on_screenshot():
                from core.capture import capture_manager
                capture_manager.capture_fullscreen()
            self._screenshot_callback = on_screenshot
        return self._screenshot_callback
    
    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("设置")
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # 创建选项卡
        self._tabs = QTabWidget()
        
        # 快捷键设置
        self._hotkeys_tab = self._create_hotkeys_tab()
        self._tabs.addTab(self._hotkeys_tab, "快捷键")
        
        # 截图设置
        self._screenshot_tab = self._create_screenshot_tab()
        self._tabs.addTab(self._screenshot_tab, "截图")
        
        # AI 设置
        self._ai_tab = self._create_ai_tab()
        self._tabs.addTab(self._ai_tab, "AI 服务")
        
        # OCR 设置
        self._ocr_tab = self._create_ocr_tab()
        self._tabs.addTab(self._ocr_tab, "OCR")
        
        # UI 设置
        self._ui_tab = self._create_ui_tab()
        self._tabs.addTab(self._ui_tab, "界面")
        
        layout.addWidget(self._tabs)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self._reset_btn = QPushButton("恢复默认")
        self._reset_btn.clicked.connect(self._on_reset)
        button_layout.addWidget(self._reset_btn)
        
        button_layout.addStretch()
        
        self._cancel_btn = QPushButton("取消")
        self._cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self._cancel_btn)
        
        self._apply_btn = QPushButton("保存并应用")
        self._apply_btn.clicked.connect(self._on_apply)
        button_layout.addWidget(self._apply_btn)
        
        self._save_btn = QPushButton("保存")
        self._save_btn.clicked.connect(self._on_save)
        button_layout.addWidget(self._save_btn)
        
        layout.addLayout(button_layout)
        
        # 降级服务提示
        self._degraded_label = QLabel()
        self._degraded_label.setStyleSheet("color: orange;")
        self._degraded_label.setVisible(False)
        layout.addWidget(self._degraded_label)
    
    def _create_hotkeys_tab(self) -> QWidget:
        """创建快捷键设置选项卡"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        self._hotkey_screenshot = QLineEdit()
        self._hotkey_screenshot.setPlaceholderText("<ctrl>+<shift>+g")
        layout.addRow("截图快捷键:", self._hotkey_screenshot)
        
        self._hotkey_search = QLineEdit()
        self._hotkey_search.setPlaceholderText("<ctrl>+f")
        layout.addRow("搜索快捷键:", self._hotkey_search)
        
        self._hotkey_clear = QLineEdit()
        self._hotkey_clear.setPlaceholderText("<escape>")
        layout.addRow("清除快捷键:", self._hotkey_clear)
        
        return widget
    
    def _create_screenshot_tab(self) -> QWidget:
        """创建截图设置选项卡"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        self._debounce_interval = QDoubleSpinBox()
        self._debounce_interval.setRange(0.1, 60.0)
        self._debounce_interval.setSingleStep(0.5)
        self._debounce_interval.setSuffix(" 秒")
        layout.addRow("防抖间隔:", self._debounce_interval)
        
        self._cluster_threshold = QDoubleSpinBox()
        self._cluster_threshold.setRange(0.1, 30.0)
        self._cluster_threshold.setSingleStep(0.5)
        self._cluster_threshold.setSuffix(" 秒")
        layout.addRow("集群阈值:", self._cluster_threshold)
        
        self._max_captures = QSpinBox()
        self._max_captures.setRange(1, 100)
        layout.addRow("最大截图数:", self._max_captures)
        
        return widget
    
    def _create_ai_tab(self) -> QWidget:
        """创建 AI 设置选项卡"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        self._ai_api_key = QLineEdit()
        self._ai_api_key.setEchoMode(QLineEdit.Password)
        self._ai_api_key.setPlaceholderText("输入 API Key")
        layout.addRow("API Key:", self._ai_api_key)
        
        self._ai_model = QComboBox()
        self._ai_model.addItems([
            "gpt-4o-mini",
            "gpt-4o",
            "gpt-4-turbo",
            "claude-3-opus",
            "claude-3-sonnet"
        ])
        layout.addRow("模型:", self._ai_model)
        
        self._ai_timeout = QSpinBox()
        self._ai_timeout.setRange(10, 300)
        self._ai_timeout.setSuffix(" 秒")
        layout.addRow("超时时间:", self._ai_timeout)
        
        return widget
    
    def _create_ocr_tab(self) -> QWidget:
        """创建 OCR 设置选项卡"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        self._ocr_engine = QComboBox()
        self._ocr_engine.addItems(["rapidocr", "tesseract", "easyocr"])
        layout.addRow("OCR 引擎:", self._ocr_engine)
        
        self._ocr_language = QComboBox()
        self._ocr_language.addItems(["ch", "en", "ch+en"])
        layout.addRow("语言:", self._ocr_language)
        
        return widget
    
    def _create_ui_tab(self) -> QWidget:
        """创建 UI 设置选项卡"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        self._ui_theme = QComboBox()
        self._ui_theme.addItems(["light", "dark", "system"])
        layout.addRow("主题:", self._ui_theme)
        
        self._ui_auto_hide = QCheckBox("自动隐藏")
        layout.addRow("", self._ui_auto_hide)
        
        self._ui_start_minimized = QCheckBox("启动时最小化")
        layout.addRow("", self._ui_start_minimized)
        
        return widget
    
    def _load_current_settings(self):
        """加载当前设置到UI"""
        settings = self._settings_manager.get_all()
        
        # 快捷键设置
        hotkeys = settings.get("hotkeys", {})
        self._hotkey_screenshot.setText(hotkeys.get("screenshot", ""))
        self._hotkey_search.setText(hotkeys.get("search", ""))
        self._hotkey_clear.setText(hotkeys.get("clear", ""))
        
        # 截图设置
        screenshot = settings.get("screenshot", {})
        self._debounce_interval.setValue(screenshot.get("debounce_interval", 5.0))
        self._cluster_threshold.setValue(screenshot.get("cluster_threshold", 2.0))
        self._max_captures.setValue(screenshot.get("max_captures_per_window", 10))
        
        # AI 设置
        ai = settings.get("ai", {})
        self._ai_api_key.setText(ai.get("api_key", ""))
        model = ai.get("model", "gpt-4o-mini")
        index = self._ai_model.findText(model)
        if index >= 0:
            self._ai_model.setCurrentIndex(index)
        self._ai_timeout.setValue(ai.get("timeout", 30))
        
        # OCR 设置
        ocr = settings.get("ocr", {})
        engine = ocr.get("engine", "rapidocr")
        index = self._ocr_engine.findText(engine)
        if index >= 0:
            self._ocr_engine.setCurrentIndex(index)
        lang = ocr.get("language", "ch")
        index = self._ocr_language.findText(lang)
        if index >= 0:
            self._ocr_language.setCurrentIndex(index)
        
        # UI 设置
        ui = settings.get("ui", {})
        theme = ui.get("theme", "light")
        index = self._ui_theme.findText(theme)
        if index >= 0:
            self._ui_theme.setCurrentIndex(index)
        self._ui_auto_hide.setChecked(ui.get("auto_hide", False))
        self._ui_start_minimized.setChecked(ui.get("start_minimized", False))
    
    def _collect_settings_from_ui(self) -> Dict[str, Any]:
        """从UI收集设置"""
        return {
            "hotkeys": {
                "screenshot": self._hotkey_screenshot.text(),
                "search": self._hotkey_search.text(),
                "clear": self._hotkey_clear.text()
            },
            "screenshot": {
                "debounce_interval": self._debounce_interval.value(),
                "cluster_threshold": self._cluster_threshold.value(),
                "max_captures_per_window": self._max_captures.value()
            },
            "ai": {
                "api_key": self._ai_api_key.text(),
                "model": self._ai_model.currentText(),
                "timeout": self._ai_timeout.value()
            },
            "ocr": {
                "engine": self._ocr_engine.currentText(),
                "language": self._ocr_language.currentText()
            },
            "ui": {
                "theme": self._ui_theme.currentText(),
                "auto_hide": self._ui_auto_hide.isChecked(),
                "start_minimized": self._ui_start_minimized.isChecked()
            }
        }
    
    def _on_reset(self):
        """恢复默认设置"""
        reply = QMessageBox.question(
            self,
            "确认恢复默认",
            "确定要恢复所有设置为默认值吗？",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self._settings_manager.reset()
            default_settings = self._settings_manager.get_all()
            self._load_current_settings()
            self._pending_settings = copy.deepcopy(default_settings)
            self._original_settings = default_settings
            self._degraded_services = []
            self._update_degraded_label()
    
    def _on_save(self) -> bool:
        """保存设置（不应用）

        Returns:
            是否保存成功
        """
        new_settings = self._collect_settings_from_ui()

        if not self._validate_input(new_settings):
            return False

        if self._settings_manager.update(new_settings):
            self._pending_settings = new_settings
            self._original_settings = new_settings
            QMessageBox.information(self, "保存成功", "设置已保存")
            return True
        else:
            QMessageBox.warning(self, "保存失败", "无法保存设置")
            return False

    def _on_apply(self) -> bool:
        """应用设置（带热更新）

        Returns:
            是否应用成功
        """
        new_settings = self._collect_settings_from_ui()

        if not self._validate_input(new_settings):
            return False

        if not self._settings_manager.has_changes(new_settings):
            QMessageBox.information(self, "无需应用", "设置没有变化")
            return True

        reply = QMessageBox.question(
            self,
            "确认应用",
            "确定要应用新设置吗？部分服务可能会重启。",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return False

        success, degraded = self._apply_settings(new_settings)

        if success:
            self._pending_settings = new_settings
            self._original_settings = new_settings
            QMessageBox.information(self, "应用成功", "设置已应用")
            return True
        else:
            self._degraded_services = degraded
            self._update_degraded_label()
            QMessageBox.warning(
                self,
                "部分应用失败",
                f"以下服务应用失败：{', '.join(degraded)}\n请重启应用以完全应用所有设置。"
            )
            return False

    def _validate_input(self, settings: Dict[str, Any]) -> bool:
        """验证输入配置

        Args:
            settings: 要验证的配置字典

        Returns:
            配置是否合法
        """
        hotkeys = settings.get("hotkeys", {})
        for key, value in hotkeys.items():
            if value and not self.HOTKEY_PATTERN.match(value):
                QMessageBox.warning(
                    self,
                    "输入错误",
                    f"快捷键 '{key}' 格式不正确。\n正确格式示例：<ctrl>+<shift>+g 或 ctrl+c"
                )
                return False

        ai = settings.get("ai", {})
        if "api_key" in ai:
            api_key = ai["api_key"]
            if api_key and len(api_key.strip()) == 0:
                QMessageBox.warning(self, "输入错误", "API Key 不能只包含空白字符")
                return False

        screenshot = settings.get("screenshot", {})
        if screenshot.get("debounce_interval", 0) <= 0:
            QMessageBox.warning(self, "输入错误", "防抖间隔必须大于 0")
            return False
        if screenshot.get("max_captures_per_window", 0) <= 0:
            QMessageBox.warning(self, "输入错误", "最大截图数必须大于 0")
            return False

        return True
    
    def _apply_settings(self, new_settings: Dict[str, Any]) -> tuple:
        """应用设置（带热更新和错误处理）

        Returns:
            (是否完全成功, 降级服务列表)
        """
        success = True
        degraded = []

        old_screenshot_settings = self._capture_manager.get_settings()
        old_hotkeys = self._keyboard_manager.get_hotkeys()

        # 1. 等待或取消长时间运行的任务
        self._task_queue.wait_for_tasks_completion(timeout=5.0)
        cancelled = self._task_queue.cancel_all_pending()
        if cancelled > 0:
            print(f"已取消 {cancelled} 个待处理任务")

        # 2. 更新截图设置
        screenshot_settings = new_settings.get("screenshot", {})
        if not self._capture_manager.update_settings(screenshot_settings):
            degraded.append("截图设置")
            success = False
            self._capture_manager.update_settings(old_screenshot_settings)

        # 3. 更新快捷键设置
        hotkeys = new_settings.get("hotkeys", {})
        new_hotkeys = {}
        if hotkeys.get("screenshot"):
            new_hotkeys[hotkeys["screenshot"]] = self._get_screenshot_callback()

        if not self._keyboard_manager.reload_hotkeys(new_hotkeys):
            degraded.append("快捷键")
            success = False
            self._keyboard_manager.reload_hotkeys(old_hotkeys)

        # 4. 更新 AI 设置
        try:
            ai_settings = new_settings.get("ai", {})
            if ai_settings.get("api_key") != self._original_settings.get("ai", {}).get("api_key"):
                degraded.append("AI API Key (需要重启)")
        except Exception as e:
            degraded.append(f"AI 设置({str(e)})")
            success = False

        # 5. 更新 OCR 设置
        try:
            ocr_settings = new_settings.get("ocr", {})
            if ocr_settings.get("engine") != self._original_settings.get("ocr", {}).get("engine"):
                degraded.append("OCR 引擎 (需要重启)")
        except Exception as e:
            degraded.append(f"OCR 设置({str(e)})")
            success = False

        # 6. 更新 UI 设置
        try:
            ui_settings = new_settings.get("ui", {})
        except Exception as e:
            degraded.append(f"UI 设置({str(e)})")
            success = False

        # 7. 保存设置到文件
        if not self._settings_manager.update(new_settings):
            degraded.append("配置保存")
            success = False

        return success, degraded

    def _update_degraded_label(self):
        """更新降级服务提示"""
        if self._degraded_services:
            self._degraded_label.setText(
                f"⚠ 部分服务应用失败：{', '.join(self._degraded_services)}"
            )
            self._degraded_label.setVisible(True)
        else:
            self._degraded_label.setVisible(False)
    
    def get_degraded_services(self) -> list:
        """获取降级服务列表"""
        return self._degraded_services.copy()

    def closeEvent(self, event):
        """关闭对话框时的处理"""
        current_settings = self._collect_settings_from_ui()
        if current_settings != self._original_settings:
            reply = QMessageBox.question(
                self,
                "确认关闭",
                "有未保存的修改，确定要关闭吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                event.ignore()
                return
        event.accept()