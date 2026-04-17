"""Glimpse Settings Dialog
设置对话框实现
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QFileDialog,
    QDialogButtonBox, QGroupBox, QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class SettingsDialog(QDialog):
    """设置对话框

    包含快捷键、API配置、存储路径等设置项
    """

    settings_changed = pyqtSignal(dict)  # 设置变更信号

    # 默认设置
    DEFAULT_SETTINGS = {
        "hotkey": "Ctrl+Shift+S",
        "api_key": "",
        "api_url": "https://api.openai.com/v1",
        "data_path": str(Path.home() / "glimpse_data"),
        "retention_days": 30,
        "max_memories": 1000
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = self.DEFAULT_SETTINGS.copy()
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """初始化UI"""
        self.setWindowTitle("设置")
        self.setModal(True)
        self.setMinimumWidth(480)
        self.resize(520, 400)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # 标题
        title = QLabel("⚙️ 偏好设置")
        title.setFont(QFont("", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # ========== 快捷键设置 ==========
        hotkey_group = QGroupBox("快捷键")
        hotkey_layout = QHBoxLayout()

        self.hotkey_display = QLineEdit()
        self.hotkey_display.setReadOnly(True)
        self.hotkey_display.setStyleSheet("""
            QLineEdit {
                background-color: #f5f5f5;
                padding: 8px;
                border-radius: 6px;
            }
        """)
        hotkey_layout.addWidget(self.hotkey_display)

        self.hotkey_button = QPushButton("修改")
        self.hotkey_button.setFixedWidth(80)
        self.hotkey_button.clicked.connect(self._change_hotkey)
        hotkey_layout.addWidget(self.hotkey_button)

        hotkey_group.setLayout(hotkey_layout)
        layout.addWidget(hotkey_group)

        # ========== API设置 ==========
        api_group = QGroupBox("API 配置")
        api_form = QFormLayout()
        api_form.setSpacing(12)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("sk-...")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        api_form.addRow("API Key:", self.api_key_input)

        self.api_url_input = QLineEdit()
        self.api_url_input.setPlaceholderText("https://api.openai.com/v1")
        api_form.addRow("API 地址:", self.api_url_input)

        api_group.setLayout(api_form)
        layout.addWidget(api_group)

        # ========== 存储设置 ==========
        storage_group = QGroupBox("存储")
        storage_layout = QVBoxLayout()

        # 数据路径
        path_layout = QHBoxLayout()
        self.data_path_input = QLineEdit()
        self.data_path_input.setReadOnly(True)
        self.data_path_input.setStyleSheet("""
            QLineEdit {
                background-color: #f5f5f5;
                padding: 8px;
                border-radius: 6px;
            }
        """)
        path_layout.addWidget(self.data_path_input)

        self.browse_button = QPushButton("浏览...")
        self.browse_button.setFixedWidth(80)
        self.browse_button.clicked.connect(self._browse_data_path)
        path_layout.addWidget(self.browse_button)

        storage_layout.addLayout(path_layout)

        # 保留天数和最大数量
        limit_layout = QFormLayout()
        limit_layout.setSpacing(8)

        self.retention_spinbox = QSpinBox()
        self.retention_spinbox.setRange(1, 365)
        self.retention_spinbox.setSuffix(" 天")
        limit_layout.addRow("记忆保留:", self.retention_spinbox)

        self.max_memories_spinbox = QSpinBox()
        self.max_memories_spinbox.setRange(100, 10000)
        self.max_memories_spinbox.setSuffix(" 条")
        limit_layout.addRow("最大存储:", self.max_memories_spinbox)

        storage_layout.addLayout(limit_layout)
        storage_group.setLayout(storage_layout)
        layout.addWidget(storage_group)

        # 弹簧
        layout.addStretch()

        # ========== 底部按钮 ==========
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                border-radius: 6px;
            }
        """)
        buttons.accepted.connect(self._save_settings)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_settings(self):
        """加载设置到UI"""
        self.hotkey_display.setText(self.settings["hotkey"])
        self.api_key_input.setText(self.settings["api_key"])
        self.api_url_input.setText(self.settings["api_url"])
        self.data_path_input.setText(self.settings["data_path"])
        self.retention_spinbox.setValue(self.settings["retention_days"])
        self.max_memories_spinbox.setValue(self.settings["max_memories"])

    def _save_settings(self):
        """保存设置"""
        self.settings["hotkey"] = self.hotkey_display.text()
        self.settings["api_key"] = self.api_key_input.text()
        self.settings["api_url"] = self.api_url_input.text()
        self.settings["data_path"] = self.data_path_input.text()
        self.settings["retention_days"] = self.retention_spinbox.value()
        self.settings["max_memories"] = self.max_memories_spinbox.value()

        # 打印设置到控制台
        print("[设置保存]")
        for key, value in self.settings.items():
            if key == "api_key" and value:
                value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "****"
            print(f"  {key}: {value}")

        self.settings_changed.emit(self.settings)
        self.accept()

    def _change_hotkey(self):
        """修改快捷键"""
        # TODO: 实现快捷键录制对话框
        self.hotkey_display.setText("Ctrl+Shift+S")

    def _browse_data_path(self):
        """浏览数据路径"""
        current_path = self.data_path_input.text()
        path = QFileDialog.getExistingDirectory(
            self,
            "选择数据存储目录",
            current_path
        )
        if path:
            self.data_path_input.setText(path)

    def reset_defaults(self):
        """重置为默认设置"""
        self.settings = self.DEFAULT_SETTINGS.copy()
        self._load_settings()

    def get_settings(self) -> dict:
        """获取当前设置"""
        return self.settings.copy()
