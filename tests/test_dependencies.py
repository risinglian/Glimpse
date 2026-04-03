#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试所有依赖是否正确安装
能运行 = 环境正常
"""

import os

os.environ["CHROMA_TELEMETRY_DISABLED"] = "true"

def test_dependencies():
    print("=== 开始测试所有依赖 ===")
    failed = []

    # ==========================
    # 1. 测试核心 UI
    # ==========================
    try:
        from PySide6.QtWidgets import QApplication
        app = QApplication([])
        print("✅ PySide6 正常")
    except Exception as e:
        print("❌ PySide6 失败:", str(e))
        failed.append("PySide6")

    # ==========================
    # 2. 测试数据库 & 嵌入
    # ==========================
    try:
        import chromadb
        client = chromadb.Client()
        print("✅ chromadb 正常")
    except Exception as e:
        print("❌ chromadb 失败:", str(e))
        failed.append("chromadb")

    try:
        # 仅测试导入，完全不触发网络
        import sentence_transformers
        print("✅ sentence-transformers 正常")
    except Exception as e:
        print("❌ sentence-transformers 失败:", str(e))
        failed.append("sentence-transformers")

    try:
        import numpy as np
        arr = np.array([1, 2, 3])
        print(f"✅ numpy 正常 (版本: {np.__version__})")
    except Exception as e:
        print("❌ numpy 失败:", str(e))
        failed.append("numpy")

    # ==========================
    # 3. 截图 & 处理
    # ==========================
    try:
        import mss
        with mss.mss() as sct:
            pass
        print("✅ mss 正常")
    except Exception as e:
        print("❌ mss 失败:", str(e))
        failed.append("mss")

    try:
        from PIL import Image
        img = Image.new('RGB', (10, 10))
        print("✅ Pillow 正常")
    except Exception as e:
        print("❌ Pillow 失败:", str(e))
        failed.append("Pillow")

    try:
        import pynput
        from pynput import mouse, keyboard
        print("✅ pynput 正常")
    except Exception as e:
        print("❌ pynput 失败:", str(e))
        failed.append("pynput")

    try:
        from rapidocr_onnxruntime import RapidOCR
        ocr = RapidOCR()
        print("✅ rapidocr-onnxruntime 正常")
    except Exception as e:
        print("❌ rapidocr-onnxruntime 失败:", str(e))
        failed.append("rapidocr-onnxruntime")

    # ==========================
    # 4. API 相关
    # ==========================
    try:
        import openai
        print(f"✅ openai 正常 (版本: {openai.__version__})")
    except Exception as e:
        print("❌ openai 失败:", str(e))
        failed.append("openai")

    try:
        import requests
        print("✅ requests 正常")
    except Exception as e:
        print("❌ requests 失败:", str(e))
        failed.append("requests")

    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ python-dotenv 正常")
    except Exception as e:
        print("❌ python-dotenv 失败:", str(e))
        failed.append("python-dotenv")

    # ==========================
    # 5. 工具类
    # ==========================
    try:
        import psutil
        print("✅ psutil 正常")
    except Exception as e:
        print("❌ psutil 失败:", str(e))
        failed.append("psutil")

    try:
        from dateutil import parser
        print("✅ python-dateutil 正常")
    except Exception as e:
        print("❌ python-dateutil 失败:", str(e))
        failed.append("python-dateutil")

    # ==========================
    # 最终结果
    # ==========================
    print("\n" + "="*50)
    if failed:
        print(f"❌ 测试失败，缺少/异常包：{', '.join(failed)}")
    else:
        print("✅ 所有依赖 100% 正常！可以直接运行项目！")
    print("="*50)

if __name__ == "__main__":
    test_dependencies()