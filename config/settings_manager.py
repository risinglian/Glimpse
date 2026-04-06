"""
设置管理器
负责配置的读写和管理
"""
import copy
import json
from pathlib import Path
from typing import Dict, Any, Optional, Set

from config.path_manager import path_manager


SETTINGS_SCHEMA: Set[str] = {
    "hotkeys",
    "screenshot",
    "ai",
    "ocr",
    "database",
    "ui"
}


class SettingsManager:
    """设置管理器 - 单例模式"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._settings_file = path_manager.config_dir / "settings.json"
        self._settings = self._load_settings()

    def _deep_copy_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """深拷贝配置"""
        return copy.deepcopy(settings)

    def _load_settings(self) -> Dict[str, Any]:
        """加载设置文件"""
        if not self._settings_file.exists():
            return self._get_default_settings()

        try:
            with open(self._settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return self._get_default_settings()

    def _get_default_settings(self) -> Dict[str, Any]:
        """获取默认设置"""
        default_settings = {
            "hotkeys": {
                "screenshot": "<ctrl>+<shift>+g",
                "search": "<ctrl>+<f>",
                "clear": "<escape>"
            },
            "screenshot": {
                "debounce_interval": 5.0,
                "cluster_threshold": 2.0,
                "max_captures_per_window": 10
            },
            "ai": {
                "api_key": "",
                "model": "gpt-4o-mini",
                "timeout": 30
            },
            "ocr": {
                "engine": "rapidocr",
                "language": "ch"
            },
            "database": {
                "sqlite_timeout": 30,
                "chroma_collection": "memories"
            },
            "ui": {
                "theme": "light",
                "auto_hide": False,
                "start_minimized": False
            }
        }

        self._save_settings(default_settings)
        return default_settings

    def _save_settings(self, settings: Dict[str, Any]):
        """保存设置到文件"""
        try:
            with open(self._settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except IOError:
            pass

    def _validate_settings(self, settings: Dict[str, Any], allow_partial: bool = False) -> bool:
        """校验配置结构（递归验证）

        Args:
            settings: 要校验的配置字典
            allow_partial: 是否允许部分键（True 用于 update 时的增量校验）

        Returns:
            配置是否合法
        """
        if not isinstance(settings, dict):
            return False

        for key in SETTINGS_SCHEMA:
            if key not in settings:
                if allow_partial:
                    continue
                return False

            section = settings[key]
            if not isinstance(section, dict):
                return False

            if key == "hotkeys":
                if not self._validate_hotkeys(section):
                    return False
            elif key == "screenshot":
                if not self._validate_screenshot(section):
                    return False
            elif key == "ai":
                if not self._validate_ai(section):
                    return False
            elif key == "ocr":
                if not self._validate_ocr(section):
                    return False
            elif key == "database":
                if not self._validate_database(section):
                    return False
            elif key == "ui":
                if not self._validate_ui(section):
                    return False

        return True

    def _validate_hotkeys(self, section: Dict[str, Any]) -> bool:
        """验证 hotkeys 配置"""
        if not isinstance(section, dict):
            return False
        for key, value in section.items():
            if not isinstance(key, str) or not isinstance(value, str):
                return False
        return True

    def _validate_screenshot(self, section: Dict[str, Any]) -> bool:
        """验证 screenshot 配置"""
        if not isinstance(section, dict):
            return False
        if "debounce_interval" in section:
            if not isinstance(section["debounce_interval"], (int, float)):
                return False
            if section["debounce_interval"] <= 0:
                return False
        if "cluster_threshold" in section:
            if not isinstance(section["cluster_threshold"], (int, float)):
                return False
        if "max_captures_per_window" in section:
            if not isinstance(section["max_captures_per_window"], int):
                return False
            if section["max_captures_per_window"] <= 0:
                return False
        return True

    def _validate_ai(self, section: Dict[str, Any]) -> bool:
        """验证 ai 配置"""
        if not isinstance(section, dict):
            return False
        if "api_key" in section and section["api_key"] and not isinstance(section["api_key"], str):
            return False
        if "model" in section and not isinstance(section["model"], str):
            return False
        if "timeout" in section:
            if not isinstance(section["timeout"], int):
                return False
            if section["timeout"] <= 0:
                return False
        return True

    def _validate_ocr(self, section: Dict[str, Any]) -> bool:
        """验证 ocr 配置"""
        if not isinstance(section, dict):
            return False
        if "engine" in section and not isinstance(section["engine"], str):
            return False
        if "language" in section and not isinstance(section["language"], str):
            return False
        return True

    def _validate_database(self, section: Dict[str, Any]) -> bool:
        """验证 database 配置"""
        if not isinstance(section, dict):
            return False
        if "sqlite_timeout" in section:
            if not isinstance(section["sqlite_timeout"], (int, float)):
                return False
        if "chroma_collection" in section and not isinstance(section["chroma_collection"], str):
            return False
        return True

    def _validate_ui(self, section: Dict[str, Any]) -> bool:
        """验证 ui 配置"""
        if not isinstance(section, dict):
            return False
        if "theme" in section and not isinstance(section["theme"], str):
            return False
        if "auto_hide" in section and not isinstance(section["auto_hide"], bool):
            return False
        if "start_minimized" in section and not isinstance(section["start_minimized"], bool):
            return False
        return True

    def get(self, key: str, default: Any = None) -> Any:
        """获取设置值

        Args:
            key: 设置键，支持点号分隔的路径，如 "hotkeys.screenshot"
            default: 默认值

        Returns:
            设置值或默认值
        """
        keys = key.split('.')
        value = self._settings

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> bool:
        """设置值

        Args:
            key: 设置键，支持点号分隔的路径
            value: 设置值

        Returns:
            是否设置成功
        """
        keys = key.split('.')
        settings = self._settings

        for k in keys[:-1]:
            if k not in settings:
                settings[k] = {}
            settings = settings[k]

        settings[keys[-1]] = value

        self._save_settings(self._settings)
        return True

    def get_all(self) -> Dict[str, Any]:
        """获取所有设置（深拷贝）"""
        return self._deep_copy_settings(self._settings)

    def update(self, settings: Dict[str, Any]) -> bool:
        """更新多个设置（原子操作）

        Args:
            settings: 要更新的设置

        Returns:
            是否更新成功
        """
        if not self._validate_settings(settings, allow_partial=True):
            return False

        temp_settings = self._deep_copy_settings(self._settings)
        try:
            for key, value in settings.items():
                if isinstance(value, dict) and key in temp_settings and isinstance(temp_settings[key], dict):
                    temp_settings[key].update(value)
                else:
                    temp_settings[key] = value

            self._save_settings(temp_settings)
            self._settings = temp_settings
            return True
        except Exception:
            return False

    def reset(self):
        """重置为默认设置"""
        self._settings = self._get_default_settings()

    def reload(self):
        """重新从磁盘加载配置"""
        try:
            self._settings = self._load_settings()
        except Exception:
            self._settings = self._get_default_settings()

    def has_changes(self, new_settings: Dict[str, Any]) -> bool:
        """检查新设置是否有变化（基于内存比较）

        Args:
            new_settings: 新的设置字典

        Returns:
            是否有变化
        """
        return self._settings != new_settings


settings_manager = SettingsManager()