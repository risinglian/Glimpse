"""Glimpse Mock Data Service
模拟数据服务，用于开发和测试
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict
from dataclasses import dataclass, asdict


@dataclass
class Memory:
    """记忆数据模型"""
    id: str
    summary: str
    timestamp: str
    screenshot_preview: Optional[str] = None

    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)


class MockMemoryService:
    """模拟记忆服务

    提供假数据用于UI开发和测试
    """

    # 预设的假数据
    _MOCK_MEMORIES = [
        {
            "id": "mem_001",
            "summary": "用户在浏览 Figma 设计界面，正在编辑一个深色主题的登录页面设计稿，包含用户名、密码输入框和社交登录按钮。",
            "timestamp": "2026-04-17 14:32:15",
            "screenshot_preview": None
        },
        {
            "id": "mem_002",
            "summary": "VS Code 代码编辑器窗口，显示 Python 代码，正在编写一个 PyQt6 窗口类，包含信号定义和 UI 初始化方法。",
            "timestamp": "2026-04-17 13:18:42",
            "screenshot_preview": None
        },
        {
            "id": "mem_003",
            "summary": "浏览器打开 ChatGPT 对话页面，用户正在询问关于 PyQt6 布局管理的最佳实践建议。",
            "timestamp": "2026-04-17 11:05:30",
            "screenshot_preview": None
        },
        {
            "id": "mem_004",
            "summary": "文件资源管理器，用户在 D:\\UI_design 目录下查看项目文件结构，包含多个 .py 和 .md 文件。",
            "timestamp": "2026-04-17 10:22:08",
            "screenshot_preview": None
        },
        {
            "id": "mem_005",
            "summary": "Windows 设置界面，显示个性化设置，用户正在更改桌面壁纸为系统预设的风景图片。",
            "timestamp": "2026-04-16 23:45:55",
            "screenshot_preview": None
        },
        {
            "id": "mem_006",
            "summary": "Notion 笔记页面，用户正在记录项目需求文档，包含功能模块划分和技术栈选型。",
            "timestamp": "2026-04-16 21:15:33",
            "screenshot_preview": None
        },
        {
            "id": "mem_007",
            "summary": "PyCharm IDE 调试界面，正在调试 Django 后端 API，断点停在用户认证逻辑处。",
            "timestamp": "2026-04-16 16:42:10",
            "screenshot_preview": None
        },
        {
            "id": "mem_008",
            "summary": "Chrome 浏览器开发者工具，Network 面板显示 API 请求响应，状态码 200。",
            "timestamp": "2026-04-16 15:28:45",
            "screenshot_preview": None
        },
        {
            "id": "mem_009",
            "summary": "Slack 消息窗口，产品经理发送了新的功能需求截图，询问技术可行性。",
            "timestamp": "2026-04-16 11:55:22",
            "screenshot_preview": None
        },
        {
            "id": "mem_010",
            "summary": "GitHub 仓库页面，用户正在查看 Pull Request 的代码变更 diff 视图。",
            "timestamp": "2026-04-15 18:30:15",
            "screenshot_preview": None
        },
    ]

    def __init__(self):
        """初始化服务"""
        self._memories = [
            Memory(**m) for m in self._MOCK_MEMORIES
        ]

    def search(self, query: str) -> List[Memory]:
        """搜索记忆

        Args:
            query: 搜索关键词

        Returns:
            匹配的记忆列表
        """
        if not query or not query.strip():
            return []

        query_lower = query.lower()
        results = []

        for memory in self._memories:
            # 在摘要中搜索
            if query_lower in memory.summary.lower():
                results.append(memory)
            # 在时间戳中搜索
            elif query_lower in memory.timestamp.lower():
                results.append(memory)

        print(f"[Mock搜索] 查询: '{query}', 找到 {len(results)} 条结果")
        return results

    def get_recent(self, limit: int = 10) -> List[Memory]:
        """获取最近的记忆

        Args:
            limit: 返回数量限制

        Returns:
            最近的记忆列表（按时间倒序）
        """
        # 按时间戳倒序排列
        sorted_memories = sorted(
            self._memories,
            key=lambda m: m.timestamp,
            reverse=True
        )
        result = sorted_memories[:limit]
        print(f"[Mock数据] 获取最近 {len(result)} 条记忆")
        return result

    def get_by_id(self, memory_id: str) -> Optional[Memory]:
        """根据ID获取记忆

        Args:
            memory_id: 记忆ID

        Returns:
            记忆对象，不存在则返回 None
        """
        for memory in self._memories:
            if memory.id == memory_id:
                return memory
        return None

    def add(self, summary: str, timestamp: Optional[str] = None) -> Memory:
        """添加新记忆

        Args:
            summary: 记忆摘要
            timestamp: 时间戳（可选，默认当前时间）

        Returns:
            新创建的记忆对象
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        new_id = f"mem_{len(self._memories) + 1:03d}"
        memory = Memory(
            id=new_id,
            summary=summary,
            timestamp=timestamp,
            screenshot_preview=None
        )
        self._memories.append(memory)
        print(f"[Mock数据] 添加记忆: {new_id}")
        return memory

    def get_all(self) -> List[Memory]:
        """获取所有记忆

        Returns:
            所有记忆列表
        """
        return self._memories.copy()

    def count(self) -> int:
        """获取记忆总数

        Returns:
            记忆数量
        """
        return len(self._memories)


# 全局单例
_mock_service = None


def get_mock_service() -> MockMemoryService:
    """获取 Mock 服务实例（单例）"""
    global _mock_service
    if _mock_service is None:
        _mock_service = MockMemoryService()
    return _mock_service
