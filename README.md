# AssistGen - 基于大语言模型构建的智能客服系统

一个基于 FastAPI 和 Vue 3 构建的前后端分离的智能客服助手项目，支持多种大语言模型，如DeepSeek V3，Qwen2.5系列，Llama3系列等。涵盖了 Agent、RAG 在智能客服领域的主流应用落地需求场景。 

## 功能特性

### 1. 通用问答能力
- **支持 DeepSeek V3 在线API**
- **支持 使用 Ollama 接入任意对话模型，如Qwen2.5系列，Llama3系列**
- **灵活的模配置**

### 2. 深度思考能力
- **支持 DeepSeek R1 在线API**
- **支持 使用 Ollama 接入任意 Deepseek r1 模型系列**
- **灵活的模配置**


### 3. ollama 性能测试工具
- 单请求性能测试
- 并发性能测试
- 系统资源监控
- 自动化测试报告

## 快速启动

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `env.example` 文件到 `llm_backend/.env` 文件中，并根据实际情况修改配置：

```env
# LLM 服务配置
CHAT_SERVICE=OLLAMA  # 或 DEEPSEEK
REASON_SERVICE=OLLAMA  # 或 DEEPSEEK

# Ollama 配置
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=deepseek-coder:6.7b
OLLAMA_REASON_MODEL=deepseek-coder:6.7b

# DeepSeek 配置（如果使用）
DEEPSEEK_API_KEY=your-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
```
### 3. 安装Mysql数据库并在 `.env` 文件中配置数据库连接信息

### 4. 启动服务

```bash
# 进入后端目录
cd llm_backend

# 启动服务（默认端口 9000）
python run.py

# 如果需要修改 IP 和端口，编辑 run.py 中的配置：
uvicorn.run(
    "main:app",
    host="0.0.0.0",  # 修改监听地址
    port=8000,       # 修改端口号
    access_log=False,
    log_level="error",
    reload=True
)
```

服务启动后可以访问：
- API 文档：http://localhost:8000/docs
- 前端界面：http://localhost:8000

## 技术栈

- 后端：
  - FastAPI
  - SQLAlchemy
  - MySQL
  - Ollama/DeepSeek

- 前端：
  - Vue 3
  - Element Plus
  - TypeScript

## 注意事项

1. 生产环境部署时：
   - 修改 `.env` 中的 `SECRET_KEY`
   - 配置正确的 CORS 设置
   - 使用 HTTPS
   - 关闭 `reload=True`

2. 开发环境：
   - 可以启用 `reload=True` 实现热重载
   - 可以设置 `log_level="debug"` 查看更多日志

## License

MIT 