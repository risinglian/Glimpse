"""
Memory Service - 记忆流程编排服务
协调截图、OCR、AI摘要生成、存储的完整记忆流程
"""
import time
import uuid
from typing import Optional, Callable, List
from threading import Semaphore

from db.sqlite_manager import MemoryRecord


MAX_CONCURRENT_MEMORIES = 5


def _rollback_sqlite(sqlite_manager, memory_id: str) -> None:
    try:
        sqlite_manager.delete_memory(memory_id)
    except Exception as e:
        print(f"Rollback failed for memory {memory_id}: {e}")


class MemoryService:
    """记忆服务 - 编排记忆的完整生命周期"""

    _instance: Optional["MemoryService"] = None
    _init_lock = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            import threading
            with threading.Lock():
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
                    cls._init_lock = threading.Lock()
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        with self._init_lock:
            if self._initialized:
                return
            self._initialized = True
            self._semaphore = Semaphore(MAX_CONCURRENT_MEMORIES)
            self._active_count = 0
            self._active_lock = __import__("threading").Lock()
            self._on_progress: Optional[Callable[[str], None]] = None

    def set_progress_callback(self, callback: Callable[[str], None]) -> None:
        self._on_progress = callback

    def _report_progress(self, message: str) -> None:
        if self._on_progress:
            self._on_progress(message)

    def _get_container(self):
        from container import container
        return container

    def create_memory(
        self,
        image_path: str,
        app_name: str = "unknown",
        stream_callback: Optional[Callable[[str], None]] = None,
    ) -> Optional[str]:
        acquired = self._semaphore.acquire(timeout=30)
        if not acquired:
            raise RuntimeError("Too many memory creation tasks in progress")

        try:
            with self._active_lock:
                self._active_count += 1

            return self._create_memory_impl(image_path, app_name, stream_callback)
        finally:
            with self._active_lock:
                self._active_count -= 1
            self._semaphore.release()

    def _create_memory_impl(
        self,
        image_path: str,
        app_name: str,
        stream_callback: Optional[Callable[[str], None]] = None,
    ) -> Optional[str]:
        c = self._get_container()
        sqlite_manager = c.get("sqlite_manager")
        chroma_manager = c.get("chroma_manager")
        ocr_engine = c.get("ocr_engine")
        ai_client = c.get("ai_client")
        embedding_client = c.get("embedding_client")

        memory_id = str(uuid.uuid4())
        created_at = time.strftime("%Y-%m-%d %H:%M:%S")

        self._report_progress("正在提取文本...")
        text_content = ocr_engine.extract_text(image_path) or ""

        self._report_progress("正在生成摘要...")
        if ai_client.is_configured():
            ai_summary = ai_client.analyze_image(
                image_path,
                prompt="为这张截图生成简短的中文摘要，描述主要内容：",
                stream_callback=stream_callback,
            )
        else:
            ai_summary = text_content[:200] if text_content else "无内容"

        self._report_progress("正在存储记忆...")
        record = MemoryRecord(
            id=memory_id,
            created_at=created_at,
            image_path=str(image_path),
            ai_summary=ai_summary,
            app_name=app_name,
            text_content=text_content,
            sync_status="PENDING",
        )

        sqlite_success = sqlite_manager.insert_memory(record)
        if not sqlite_success:
            raise RuntimeError(f"Failed to insert memory {memory_id} to SQLite")

        chroma_success = True
        if text_content or ai_summary:
            embedding_text = f"{ai_summary} {text_content}".strip()
            embedding = embedding_client.get_embedding(embedding_text)
            if embedding:
                chroma_success = chroma_manager.add_memory(
                    memory_id=memory_id,
                    text=embedding_text,
                    embedding=embedding,
                    metadata={
                        "app_name": app_name,
                        "created_at": created_at,
                    },
                )

            if not chroma_success:
                _rollback_sqlite(sqlite_manager, memory_id)
                raise RuntimeError(f"Failed to insert memory {memory_id} to ChromaDB")

        self._report_progress("记忆已保存")
        return memory_id

    def create_memory_async(
        self,
        image_path: str,
        app_name: str = "unknown",
        on_complete: Optional[Callable[[Optional[str]], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ) -> None:
        c = self._get_container()
        task_queue = c.get("task_queue")

        def task():
            try:
                memory_id = self.create_memory(image_path, app_name)
                if on_complete:
                    on_complete(memory_id)
            except Exception as e:
                print(f"Memory creation error: {e}")
                if on_error:
                    on_error(str(e))

        task_queue.submit(task)

    def delete_memory(self, memory_id: str) -> bool:
        c = self._get_container()
        sqlite_manager = c.get("sqlite_manager")
        chroma_manager = c.get("chroma_manager")

        deleted_sqlite = sqlite_manager.delete_memory(memory_id)
        deleted_chroma = chroma_manager.delete_memory(memory_id)
        return deleted_sqlite or deleted_chroma

    def get_memory(self, memory_id: str) -> Optional[MemoryRecord]:
        c = self._get_container()
        sqlite_manager = c.get("sqlite_manager")
        return sqlite_manager.get_memory_by_id(memory_id)

    def get_recent_memories(self, limit: int = 100, offset: int = 0) -> List[MemoryRecord]:
        c = self._get_container()
        sqlite_manager = c.get("sqlite_manager")
        return sqlite_manager.get_all_memories(limit=limit, offset=offset)

    def get_active_count(self) -> int:
        with self._active_lock:
            return self._active_count


memory_service = MemoryService()
