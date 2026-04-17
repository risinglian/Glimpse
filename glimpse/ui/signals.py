"""Glimpse Signal Bus
全局信号总线，用于组件间通信
"""

from PyQt6.QtCore import QObject, pyqtSignal


class GlimpseSignals(QObject):
    """Glimpse 全局信号总线

    单例模式，通过 get_signals() 获取实例
    """

    # 截图相关信号
    screenshot_taken = pyqtSignal(str, str)  # 截图完成信号，参数：(图片路径, AI摘要)

    # 搜索相关信号
    search_triggered = pyqtSignal(str)        # 搜索触发信号，参数：查询词

    # 状态相关信号
    status_updated = pyqtSignal(str)          # 状态更新信号，参数：状态文本


# 全局信号实例
_signals = None


def get_signals() -> GlimpseSignals:
    """获取全局信号总线实例（单例）"""
    global _signals
    if _signals is None:
        _signals = GlimpseSignals()
    return _signals
