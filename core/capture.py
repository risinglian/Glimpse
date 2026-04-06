"""
Capture - pynput 与 mss 的封装，包含集群防抖算法
"""
import time
from typing import Optional, Callable, Tuple
from dataclasses import dataclass
from threading import Lock

import mss
import numpy as np
from PIL import Image

from config.path_manager import path_manager


@dataclass
class CaptureResult:
    image_path: str
    width: int
    height: int
    timestamp: float
    app_name: Optional[str] = None


class CaptureManager:
    """截图管理器 - 单例模式，包含集群防抖"""

    _instance = None
    _lock = Lock()
    _settings_lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._sct = mss.mss()
        self._last_capture_time = 0
        self._debounce_interval = 5.0
        self._cluster_threshold = 2.0
        self._last_region: Optional[Tuple[int, int, int, int]] = None
        self._capture_count = 0
        self._capture_window_start = 0
        self._max_captures_per_window = 10
        self._fullscreen_debounce_time = 0
        self._region_debounce_time = 0

    def capture_fullscreen(self, delay: float = 0) -> Optional[CaptureResult]:
        if delay > 0:
            time.sleep(delay)

        if not self._check_debounce(is_fullscreen=True):
            return None

        if self._check_force_split():
            return None

        try:
            screenshot = self._sct.grab(self._sct.monitors[1])
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

            filename = f"screenshot_{int(time.time() * 1000)}.png"
            image_path = path_manager.get_screenshot_path(filename)

            img.save(str(image_path), "PNG")

            self._update_capture_count(is_fullscreen=True)

            return CaptureResult(
                image_path=str(image_path),
                width=screenshot.width,
                height=screenshot.height,
                timestamp=time.time(),
            )
        except Exception as e:
            print(f"Capture error: {e}")
            return None

    def capture_region(self, region: Tuple[int, int, int, int]) -> Optional[CaptureResult]:
        x, y, w, h = region
        if w <= 0 or h <= 0:
            return None

        if not self._check_debounce(is_fullscreen=False):
            return None

        if self._check_force_split():
            return None

        if self._is_clustered_region(region):
            return None

        try:
            monitor = {"top": y, "left": x, "width": w, "height": h}
            screenshot = self._sct.grab(monitor)
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

            filename = f"screenshot_{int(time.time() * 1000)}.png"
            image_path = path_manager.get_screenshot_path(filename)

            img.save(str(image_path), "PNG")

            self._update_capture_count(is_fullscreen=False)

            self._last_region = region

            return CaptureResult(
                image_path=str(image_path),
                width=w,
                height=h,
                timestamp=time.time(),
            )
        except Exception as e:
            print(f"Capture error: {e}")
            return None

    def _check_debounce(self, is_fullscreen: bool = True) -> bool:
        current_time = time.time()
        last_time = self._fullscreen_debounce_time if is_fullscreen else self._region_debounce_time
        if current_time - last_time < self._debounce_interval:
            return False
        return True

    def _check_force_split(self) -> bool:
        current_time = time.time()
        if current_time - self._capture_window_start >= self._debounce_interval:
            self._capture_window_start = current_time
            self._capture_count = 0

        if self._capture_count >= self._max_captures_per_window:
            return True
        return False

    def _update_capture_count(self, is_fullscreen: bool = True):
        self._capture_count += 1
        current_time = time.time()
        if is_fullscreen:
            self._fullscreen_debounce_time = current_time
        else:
            self._region_debounce_time = current_time

    def _is_clustered_region(self, region: Tuple[int, int, int, int]) -> bool:
        if self._last_region is None:
            return False

        x1, y1, w1, h1 = region
        x2, y2, w2, h2 = self._last_region

        x_overlap = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
        y_overlap = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
        overlap_area = x_overlap * y_overlap

        area1 = w1 * h1
        area2 = w2 * h2
        iou = overlap_area / (area1 + area2 - overlap_area + 1e-6)

        time_diff = time.time() - self._last_capture_time

        return iou > 0.5 and time_diff < self._cluster_threshold

    def set_debounce_interval(self, interval: float) -> bool:
        """设置防抖间隔
        
        Args:
            interval: 防抖间隔（秒）
            
        Returns:
            是否设置成功
        """
        try:
            self._debounce_interval = float(interval)
            return True
        except (ValueError, TypeError):
            return False

    def set_cluster_threshold(self, threshold: float) -> bool:
        """设置集群阈值
        
        Args:
            threshold: 集群阈值（秒）
            
        Returns:
            是否设置成功
        """
        try:
            self._cluster_threshold = float(threshold)
            return True
        except (ValueError, TypeError):
            return False

    def set_max_captures_per_window(self, max_captures: int) -> bool:
        """设置每个窗口最大截图数量
        
        Args:
            max_captures: 最大截图数量
            
        Returns:
            是否设置成功
        """
        try:
            self._max_captures_per_window = int(max_captures)
            return True
        except (ValueError, TypeError):
            return False

    def update_settings(self, settings: dict) -> bool:
        """更新截图设置（用于热更新，原子操作）
        
        Args:
            settings: 包含截图设置的字典
            
        Returns:
            是否更新成功
        """
        with self._settings_lock:
            old_debounce = self._debounce_interval
            old_cluster = self._cluster_threshold
            old_max = self._max_captures_per_window

            try:
                if "debounce_interval" in settings:
                    if not self.set_debounce_interval(settings["debounce_interval"]):
                        return False
                if "cluster_threshold" in settings:
                    if not self.set_cluster_threshold(settings["cluster_threshold"]):
                        return False
                if "max_captures_per_window" in settings:
                    if not self.set_max_captures_per_window(settings["max_captures_per_window"]):
                        return False
                return True
            except Exception:
                self._debounce_interval = old_debounce
                self._cluster_threshold = old_cluster
                self._max_captures_per_window = old_max
                return False

    def get_settings(self) -> dict:
        """获取当前截图设置"""
        return {
            "debounce_interval": self._debounce_interval,
            "cluster_threshold": self._cluster_threshold,
            "max_captures_per_window": self._max_captures_per_window
        }

    def close(self):
        self._sct.close()


capture_manager = CaptureManager()
