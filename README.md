# 智能翻译助手

一个基于LLM API的本地部署翻译工具，提供简洁的用户界面和高质量的翻译服务。本项目使用DeepSeek Chat模型作为默认翻译引擎。

## 系统要求

- Python 3.6+
- Node.js 14+
- npm 6+

## 项目结构

```
translator-app/
├── backend/            # Flask后端
│   ├── app.py          # 主应用文件
│   ├── config.py       # 配置文件
│   ├── requirements.txt # Python依赖
│   └── .env            # 环境变量
├── frontend/           # React前端
│   ├── public/         # 静态资源
│   ├── src/            # 源代码
│   ├── package.json    # npm依赖
│   └── .env            # 前端环境变量
├── start-backend.sh    # 后端启动脚本
├── start-frontend.sh   # 前端启动脚本
└── start               # 一键启动脚本
```

## 部署步骤

### 1. 克隆项目

```bash
git clone https://github.com/ZUOLI11111111/TranslatorTony.git
cd translator-app
```

### 2. 配置环境变量

在`backend/.env`文件中配置API密钥和其他设置：

```
DEEPSEEK_API_KEY=你的DeepSeek_API密钥
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_API_URL=https://api.deepseek.com
OPENAI_API_KEY=你的OpenAI_API密钥
OPENAI_MODEL=gpt-3.5-turbo
DEBUG=True
HOST=0.0.0.0
PORT=5000
```

### 3. 安装依赖

#### 后端依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 前端依赖

```bash
cd frontend
npm install
```

## 启动应用

### 方法一：使用脚本启动（推荐）

项目提供了便捷的启动脚本：

1. 启动后端：

```bash
./start-backend.sh
```

2. 启动前端（在另一个终端）：

```bash
./start-frontend.sh
```

### 方法二：手动启动

#### 启动后端

```bash
cd backend
python3 app.py
```

后端服务将在 http://localhost:5000 运行。

#### 启动前端

```bash
cd frontend
npm start
```

前端应用将在 http://localhost:3000 运行。

## 验证安装

1. 打开浏览器访问 http://localhost:3000
2. 检查是否可以正常访问翻译界面
3. 尝试进行简单翻译测试

## 常见问题

1. **API密钥错误**：
   - 检查 `backend/.env` 文件中的API密钥是否正确配置

2. **后端无法启动**：
   - 确认所有依赖已正确安装
   - 检查端口5000是否被占用
   - 确认Python版本兼容

3. **前端无法启动**：
   - 确认Node.js和npm版本兼容
   - 检查端口3000是否被占用
   - 确认所有npm依赖已正确安装

4. **无法连接到后端**：
   - 确认后端服务正在运行
   - 检查防火墙设置是否阻止连接

## 注意事项

- 本应用需要有效的LLM API密钥才能使用
- 默认使用DeepSeek Chat模型进行翻译
- 大型文本翻译可能需要更长的处理时间

## 许可证

MIT # TranslatorTony
