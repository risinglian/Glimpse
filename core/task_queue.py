"""
Task Queue - ThreadPoolExecutor 调度与任务生命周期管理
"""
import time
from typing import Callable, Optional, Any, Dict
from dataclasses import dataclass, field
from enum import Enum, auto
from concurrent.futures import ThreadPoolExecutor, Future
import threading


class TaskStatus(Enum):
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


@dataclass
class Task:
    id: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    callback: Optional[Callable] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

    @property
    def duration(self) -> Optional[float]:
        if self.started_at is None:
            return None
        end = self.completed_at or time.time()
        return end - self.started_at


class TaskQueue:
    """任务队列管理器 - 单例模式"""

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
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._tasks: Dict[str, Task] = {}
        self._futures: Dict[str, Future] = {}
        self._lock = threading.Lock()

    def submit(
        self,
        task_id: str,
        func: Callable,
        *args,
        callback: Optional[Callable] = None,
        **kwargs,
    ) -> Task:
        with self._lock:
            if task_id in self._tasks:
                existing = self._tasks[task_id]
                if existing.status in (TaskStatus.PENDING, TaskStatus.RUNNING):
                    return existing

            task = Task(
                id=task_id,
                func=func,
                args=args,
                kwargs=kwargs,
                callback=callback,
            )
            self._tasks[task_id] = task

        future = self._executor.submit(self._run_task, task)
        with self._lock:
            self._futures[task_id] = future

        return task

    def _run_task(self, task: Task) -> Any:
        task.status = TaskStatus.RUNNING
        task.started_at = time.time()

        try:
            result = task.func(*task.args, **task.kwargs)
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = time.time()
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = time.time()
        finally:
            if task.callback:
                try:
                    task.callback(task)
                except Exception:
                    pass

        return task.result

    def get_task(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def cancel_task(self, task_id: str) -> bool:
        with self._lock:
            if task_id not in self._tasks:
                return False
            task = self._tasks[task_id]
            if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
                return False
            if task_id in self._futures:
                self._futures[task_id].cancel()
            task.status = TaskStatus.CANCELLED
            return True

    def get_all_tasks(self) -> Dict[str, Task]:
        return self._tasks.copy()

    def clear_completed(self):
        with self._lock:
            completed_ids = [
                tid for tid, t in self._tasks.items()
                if t.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED)
            ]
            for tid in completed_ids:
                del self._tasks[tid]
                if tid in self._futures:
                    del self._futures[tid]

    def shutdown(self, wait: bool = True):
        self._executor.shutdown(wait=wait)


task_queue = TaskQueue()
