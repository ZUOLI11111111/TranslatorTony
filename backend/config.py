import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# API配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
DEEPSEEK_API_URL = os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com')

# 服务器配置
DEBUG = os.getenv('DEBUG', 'True') == 'True'
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))

# 翻译默认设置
DEFAULT_SOURCE_LANG = 'auto'
DEFAULT_TARGET_LANG = 'en'

# DeepSeek模型列表
DEEPSEEK_MODELS = {
    "deepseek-chat": "DeepSeek Chat（通用对话）",
    "deepseek-coder": "DeepSeek Coder（代码生成）",
    "deepseek-lite": "DeepSeek Lite（轻量版）",
    "deepseek-r1": "DeepSeek R1（最新版本）"
}
