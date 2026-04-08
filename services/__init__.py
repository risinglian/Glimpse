"""
Services module
"""
from services.ai_client import ai_client
from services.ocr_engine import ocr_engine
from services.embedding_client import embedding_client
from services.keyboard_manager import keyboard_manager
from services.memory_service import memory_service
from services.search_service import search_service

__all__ = [
    "ai_client",
    "ocr_engine",
    "embedding_client",
    "keyboard_manager",
    "memory_service",
    "search_service",
]
