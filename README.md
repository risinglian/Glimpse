# Glimpse

AI 驱动的桌面记忆检索系统。截图后自动进行 OCR 和 AI 摘要分析，支持语义搜索。

## 环境要求

- Python 3.10+
- Windows / macOS / Linux

## 依赖安装

```bash
pip install -r requirements.txt
```

## 配置

创建 `.env` 文件：

```
OPENAI_API_KEY=your_api_key_here
```

## 运行

```bash
python main.py
```

## 项目结构

```
Glimpse/
├── main.py                 # 程序入口
├── container.py            # 依赖注入容器
├── config/                 # 配置
├── core/                   # 核心功能（截图、任务队列）
├── db/                     # 数据库（SQLite、ChromaDB）
├── services/               # 业务服务（记忆、搜索）
├── ui/                     # 界面
└── GlimpseData/            # 数据存储
```

## 快捷键

- `Ctrl+Shift+G` - 全局截图
- `Ctrl+F` - 聚焦搜索框
- `Escape` - 清空搜索
