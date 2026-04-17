# Glimpse - AI 桌面记忆助手

## 项目简介

Glimpse 是一个通过全局快捷键截屏、AI 自动分析并支持自然语言搜索的桌面记忆助手。用户只需按下快捷键即可截屏，系统会自动使用 AI 分析截图内容并生成摘要，之后可以通过自然语言查询（如"昨天关于设计的内容"）快速检索历史记忆。

## 当前进度

目前项目已完成 UI 框架搭建，包括主窗口（MainWindow）、设置对话框（SettingsDialog）、信号总线（GlimpseSignals）和 Mock 数据服务（MockMemoryService）。主窗口包含搜索框、记忆卡片列表和状态栏，支持基础的搜索演示功能。待完成的功能包括全局快捷键截图、AI API 接入、SQLite 数据库存储、真实的语义搜索服务以及截图预览显示。

## 环境搭建与运行

确保你的系统已安装 Python 3.9 或更高版本。进入项目根目录后，先安装项目依赖：pip install -r requirements.txt。安装完成后运行 python main.py 即可启动应用。预期效果是弹出一个窗口，顶部有搜索输入框和搜索按钮，中间区域显示 3-5 条示例记忆卡片（每张卡片包含截图占位区域、AI 摘要文本和时间戳），底部状态栏显示"监听中"提示。你可以尝试在搜索框输入关键词并按回车，控制台会打印搜索词，同时窗口中的卡片列表会根据搜索结果更新。

## 项目目录结构

```
glimpse/
├── main.py                    # 应用入口
├── requirements.txt           # 项目依赖
├── README.md                  # 项目说明文档
├── ui/                        # UI 组件模块
│   ├── __init__.py           # 模块导出声明
│   ├── main_window.py        # 主窗口实现（含 MemoryCard 组件）
│   ├── settings_dialog.py    # 设置对话框
│   ├── signals.py            # 全局信号总线
│   └── mock_data.py          # Mock 数据服务（开发测试用）
├── tests/                     # 测试模块
│   ├── __init__.py
│   └── test_ui.py            # UI 单元测试
├── services/                  # 业务逻辑模块（预留）
│   └── __init__.py
└── db/                        # 数据库模块（预留）
    └── __init__.py
```

## 对接说明

为方便后续模块集成，现约定数据接口格式如下。search_service.search(query: str) 方法应返回一个字典列表，每个字典包含 id（记忆唯一标识）、summary（AI 生成的文本摘要）、timestamp（时间戳字符串，格式如 "2026-04-17 14:30:00"）和 screenshot_path（截图文件路径，可为 None）。memory_service.get_recent(limit: int) 方法返回相同格式的列表。目前 UI 层使用的是 MockMemoryService 提供的假数据，后续替换成真实服务时，只需修改 main_window.py 中的导入语句，将 get_mock_service() 替换为真实服务的实例即可，UI 层的调用代码无需改动。

## GitHub 协作步骤

首先登录你的 GitHub 账号，然后 Fork 小组的主仓库（或直接 clone 到本地）。将本项目所有文件复制到仓库对应目录后，运行 python main.py 验证 UI 能正常打开。接着运行 pytest tests/ 确保所有测试通过。检查 UI 的搜索框输入功能和设置对话框是否符合小组约定的接口格式。确认无误后执行 git add . 和 git commit -m "添加 UI 框架"，然后 git push 到自己的远程仓库。最后在 GitHub 上提交 Pull Request 到主仓库，等待代码审查合并。

## 验收检查清单

请按以下清单逐项验证项目是否正确搭建：运行 python main.py 能打开窗口；搜索框能输入文字并按回车，控制台打印搜索词；点击菜单栏的"设置"能打开设置对话框；设置对话框中修改内容并点击保存，控制台打印保存的配置；界面中显示 3 到 5 条示例记忆卡片；运行 pytest tests/ 显示测试通过。

## 常见问题

如果依赖安装失败，请尝试升级 pip（python -m pip install --upgrade pip）或使用国内镜像源（pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple）。如果运行报错"No module named PyQt6"，说明依赖未安装成功，请重新执行 pip install PyQt6。如果运行报错"No module named ui"，请检查是否在项目根目录下运行 python main.py，并且 ui 文件夹下有 __init__.py 文件。
