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
        self._debounce_interval = 0.5
        self._cluster_threshold = 2.0
        self._last_region: Optional[Tuple[int, int, int, int]] = None

    def capture_fullscreen(self, delay: float = 0) -> Optional[CaptureResult]:
        if delay > 0:
            time.sleep(delay)

        if not self._check_debounce():
            return None

        try:
            screenshot = self._sct.grab(self._sct.monitors[1])
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            
            filename = f"screenshot_{int(time.time() * 1000)}.png"
            image_path = path_manager.get_screenshot_path(filename)
            
            img.save(str(image_path), "PNG")
            
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

        if self._is_clustered_region(region):
            return None

        try:
            monitor = {"top": y, "left": x, "width": w, "height": h}
            screenshot = self._sct.grab(monitor)
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            
            filename = f"screenshot_{int(time.time() * 1000)}.png"
            image_path = path_manager.get_screenshot_path(filename)
            
            img.save(str(image_path), "PNG")
            
            self._last_region = region
            self._last_capture_time = time.time()
            
            return CaptureResult(
                image_path=str(image_path),
                width=w,
                height=h,
                timestamp=time.time(),
            )
        except Exception as e:
            print(f"Capture error: {e}")
            return None

    def _check_debounce(self) -> bool:
        current_time = time.time()
        if current_time - self._last_capture_time < self._debounce_interval:
            return False
        return True

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

    def set_debounce_interval(self, interval: float):
        self._debounce_interval = interval

    def set_cluster_threshold(self, threshold: float):
        self._cluster_threshold = threshold

    def close(self):
        self._sct.close()


capture_manager = CaptureManager()
