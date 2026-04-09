# Glimpse 环境配置指南

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
OPENAI_BASE_URL=https://api.openai.com/v1
```

## 运行

```bash
python main.py
```

## 依赖说明

| 类别 | 依赖 | 说明 |
|------|------|------|
| UI | PySide6==6.11.0 | Qt for Python GUI 框架 |
| 数据库 | chromadb==0.4.18 | 向量数据库 |
| Embedding | sentence-transformers==2.2.2 | 文本嵌入模型 |
| 截图 | mss==9.0.1, Pillow==10.2.0 | 屏幕截图处理 |
| OCR | rapidocr-onnxruntime==1.4.4 | 文字识别 |
| 输入 | pynput==1.7.6 | 全局热键监听 |
| API | openai==1.13.3 | AI 接口调用 |
| 工具 | psutil==5.9.8, python-dateutil==2.9.0 | 系统工具 |

## 故障排除

### 依赖安装失败

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### SSL 证书错误 (macOS)

```bash
/Applications/Python\ 3.x/Install\ Certificates.command
```
