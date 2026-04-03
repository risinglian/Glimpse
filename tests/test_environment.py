"""
环境验证脚本
用于验证Glimpse项目的环境配置是否正确
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def test_python_version():
    """测试Python版本"""
    print("=== 测试Python版本 ===")
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    
    # 检查Python版本是否为3.10.x
    if version.major == 3 and version.minor == 10:
        print(f"OK: Python版本满足要求 (3.10.{version.micro})")
        return True
    else:
        print("FAIL: Python环境版本错误，需要 3.10.x")
        return False


def test_dependencies():
    """测试依赖安装情况"""
    print("\n=== 测试依赖安装 ===")
    
    # 正确映射：包名 → 导入名
    package_import_map = {
        'PySide6': 'PySide6',
        'chromadb': 'chromadb',
        'sentence-transformers': 'sentence_transformers',
        'transformers': 'transformers',
        'huggingface_hub': 'huggingface_hub',
        'tokenizers': 'tokenizers',
        'numpy': 'numpy',
        'mss': 'mss',
        'Pillow': 'PIL',
        'pynput': 'pynput',
        'rapidocr-onnxruntime': 'rapidocr_onnxruntime',
        'openai': 'openai',
        'requests': 'requests',
        'python-dotenv': 'dotenv',
        'psutil': 'psutil',
        'python-dateutil': 'dateutil',
        'pytest': 'pytest',
        'pytest-qt': 'pytestqt',
        'pytest-cov': 'pytest_cov',
        'certifi': 'certifi',
        'charset_normalizer': 'charset_normalizer',
        'idna': 'idna',
        'urllib3': 'urllib3'
    }
    
    missing_packages = []
    
    for package, import_name in package_import_map.items():
        try:
            module = __import__(import_name)
            version = getattr(module, "__version__", "unknown")
            print(f"OK: {package} 已安装 (版本: {version})")
            
            if package == "Pillow":
                from PIL import Image
                print("  - Pillow: 测试成功")
            elif package == "requests":
                print("  - requests: 测试成功")
            elif package == "psutil":
                import psutil
                print(f"  - psutil: 系统CPU使用率: {psutil.cpu_percent():.1f}%")
        except ImportError:
            missing_packages.append(package)
            print(f"FAIL: {package} 未安装")
    
    if missing_packages:
        print(f"\nERROR: 缺少以下依赖: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    else:
        print("\nOK: 所有依赖都已正确安装")
        return True


def test_module_imports():
    """测试模块导入"""
    print("\n=== 测试模块导入 ===")
    
    modules = [
        'config.path_manager',
        'ui.main_window',
        'ui.signals',
        'core.capture',
        'core.task_queue',
        'services.ai_client',
        'services.ocr_engine',
        'db.sqlite_manager',
        'db.chroma_manager'
    ]
    
    import_errors = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"OK: {module} 导入成功")
        except Exception as e:
            import_errors.append((module, str(e)))
            print(f"FAIL: {module} 导入失败: {e}")
    
    if import_errors:
        print("\nERROR: 部分模块导入失败")
        for module, error in import_errors:
            print(f"  - {module}: {error}")
        return False
    else:
        print("\nOK: 所有模块导入成功")
        return True


def test_path_manager():
    """测试路径管理器"""
    print("\n=== 测试路径管理器 ===")
    
    try:
        from config.path_manager import path_manager
        print("OK: 路径管理器初始化成功")
        print(f"  - 数据目录: {path_manager.data_root}")
        print(f"  - 截图目录: {path_manager.screenshots_dir}")
        print(f"  - SQLite路径: {path_manager.sqlite_path}")
        print(f"  - ChromaDB路径: {path_manager.chroma_path}")
        return True
    except Exception as e:
        print(f"FAIL: 路径管理器测试失败: {e}")
        return False


def test_database_connections():
    """测试数据库连接"""
    print("\n=== 测试数据库连接 ===")
    
    try:
        from db.sqlite_manager import SQLiteManager
        sqlite_manager = SQLiteManager()
        print("OK: SQLite 连接成功")
        
        from db.chroma_manager import ChromaManager
        chroma_manager = ChromaManager()
        print("OK: ChromaDB 连接成功")
        
        return True
    except Exception as e:
        print(f"FAIL: 数据库连接测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("=== 开始环境验证 ===\n")
    
    tests = [
        test_python_version,
        test_dependencies,
        test_module_imports,
        test_path_manager,
        test_database_connections
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "="*50)
    print("=== 环境验证结果 ===")
    print("="*50)
    
    if all(results):
        print("OK: 所有测试通过！环境配置正确。")
        print("\n你可以运行: python main.py 来启动应用")
        return 0
    else:
        print("FAIL: 部分测试失败，请检查环境配置。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
