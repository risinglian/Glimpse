# Glimpse 环境配置指南

本文档介绍如何设置 Glimpse 的开发环境。

## 环境要求

- **Python**: 3.10 或更高版本
- **操作系统**: macOS / Linux / Windows

## 依赖说明

| 类别 | 依赖 | 说明 |
|------|------|------|
| **UI** | PySide6==6.6.1 | Qt for Python GUI 框架 |
| **数据库** | chromadb==0.4.22 | 向量数据库 |
| **Embedding** | transformers, sentence-transformers, torch | AI 嵌入模型 |
| **截图** | mss==9.0.1, Pillow==10.2.0 | 屏幕截图处理 |
| **输入** | pynput==1.7.6 | 全局热键监听 |
| **API** | openai==1.13.3, requests==2.31.0 | AI 接口调用 |
| **工具** | psutil, python-dotenv, python-dateutil | 系统工具 |

---

## 选择指南

**venv（推荐大多数用户）：**
- ✅ Python 标准库自带，无需额外安装
- ✅ 轻量级，创建速度快
- ✅ 适合纯 Python 项目

**Conda（适合以下情况）：**
- ✅ 需要管理非 Python 依赖（如 CUDA、MKL 等）
- ✅ 需要使用 Conda 特有的包
- ✅ 已经在使用 Anaconda/Miniconda 生态

---

## 环境配置

### macOS / Linux

```bash
# 1. 进入项目目录
cd /path/to/Glimpse

# 2. 创建虚拟环境
python3 -m venv venv

# 3. 激活虚拟环境
source venv/bin/activate

# 4. 升级 pip
pip install --upgrade pip setuptools wheel

# 5. 安装依赖
pip install -r requirements.txt
```

### Windows PowerShell

```powershell
# 1. 进入项目目录
cd D:\ISI\Glimpse

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 4. 升级 pip
pip install --upgrade pip setuptools wheel

# 5. 安装依赖
pip install -r requirements.txt
```

---

## 配置环境变量

复制 `.env.example` 为 `.env` 并填入配置：

```bash
# API 配置
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
```

---

## 运行应用

```bash
# 激活环境后
python main.py
```

---

## 依赖管理

### 使用清华镜像加速（推荐国内用户）

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 导出当前环境的依赖

```bash
pip freeze > requirements.txt
```

---

## 项目结构

```
Glimpse/
├── main.py                 # 程序唯一入口
├── config/
│   └── path_manager.py      # 核心路径路由中心
├── ui/
│   ├── main_window.py       # 主窗体与布局
│   └── signals.py           # 跨线程通信的全局信号总线
├── core/
│   ├── capture.py           # 截图与防抖算法
│   └── task_queue.py        # 任务队列管理
├── services/
│   ├── ai_client.py         # AI 接口调用
│   └── ocr_engine.py        # OCR 引擎
├── db/
│   ├── sqlite_manager.py    # SQLite 元数据存储
│   └── chroma_manager.py   # 向量数据库管理
└── GlimpseData/            # 数据存储目录（自动创建）
    ├── screenshots/         # 截图存储
    ├── database/            # 数据库文件
    ├── logs/                # 日志文件
    └── cache/               # 缓存目录
```

---

## 故障排除

### Python 版本过低

```bash
# macOS (Homebrew)
brew install python@3.10

# Ubuntu/Debian
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-pip

# Windows: https://www.python.org/downloads/
```

### SSL 证书错误 (macOS)

```bash
/Applications/Python\ 3.x/Install\ Certificates.command
```

### 权限错误

```bash
chmod +x main.py
```

### 依赖安装失败

```bash
# 先升级 pip
pip install --upgrade pip setuptools wheel

# 使用镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 获取帮助

- 项目文档: [README.md](README.md)
- 日志文件: `GlimpseData/logs/glimpse.log`

---

**祝使用愉快！**
