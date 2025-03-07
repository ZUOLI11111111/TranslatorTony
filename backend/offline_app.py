from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import config
import os
import json
import time
from dotenv import load_dotenv

app = Flask(__name__)
# 配置JSON响应不转义中文字符
app.config['JSON_AS_ASCII'] = False
# 为所有路由启用CORS，允许任何来源访问API
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# 加载.env文件中的配置
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    print(f"已加载环境变量: {dotenv_path}")
else:
    print("警告: 未找到.env文件")

# 配置服务器
DEBUG = os.getenv('DEBUG', 'True') == 'True'
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))

# 翻译默认设置
DEFAULT_SOURCE_LANG = 'auto'
DEFAULT_TARGET_LANG = 'en'

print("离线模式翻译服务启动中...")

@app.route('/')
def index():
    """首页 - 返回API状态信息"""
    return jsonify({
        "status": "ok",
        "message": "翻译API服务正在运行",
        "model": "离线模式",
        "offline_mode": True,
        "endpoints": [
            "/api/translate - 翻译API",
            "/api/languages - 获取支持的语言",
            "/api/check - 检查API密钥",
            "/api/health - 健康检查"
        ]
    })

def simple_offline_translate(text, source_lang, target_lang):
    """简单的离线翻译函数（无需API）"""
    print(f"使用离线模式翻译: {source_lang} -> {target_lang}")
    
    # 模拟API延迟
    time.sleep(1)
    
    # 基础翻译，非常简单的实现
    if source_lang == "zh" and target_lang == "en":
        # 非常简单的中英替换示例
        common_words = {
            "你好": "Hello",
            "世界": "World",
            "翻译": "Translation",
            "软件": "Software",
            "语言": "Language",
            "谢谢": "Thank you",
            "中文": "Chinese",
            "英语": "English"
        }
        
        translated = text
        for zh, en in common_words.items():
            if zh in text:
                translated = translated.replace(zh, en)
        return translated
    elif source_lang == "en" and target_lang == "zh":
        # 英译中
        common_words = {
            "Hello": "你好",
            "World": "世界",
            "Translation": "翻译",
            "Software": "软件",
            "Language": "语言",
            "Thank you": "谢谢",
            "Chinese": "中文",
            "English": "英语"
        }
        
        translated = text
        for en, zh in common_words.items():
            if en in text:
                translated = translated.replace(en, zh)
        return translated
    else:
        # 如果不是中英翻译，简单返回原文
        return f"[离线翻译模式] {text}"

@app.route('/api/translate', methods=['POST'])
def translate():
    """翻译API端点"""
    print("收到翻译请求")
    
    try:
        data = request.json
        print(f"翻译请求数据: {data}")
        
        if not data:
            return jsonify({"error": "未收到有效的JSON数据"}), 400
            
        text = data.get('text', '')
        source_lang = data.get('source_lang', DEFAULT_SOURCE_LANG)
        target_lang = data.get('target_lang', DEFAULT_TARGET_LANG)
        
        if not text:
            return jsonify({"error": "文本不能为空"}), 400
        
        # 使用离线翻译模式
        translated_text = simple_offline_translate(text, source_lang, target_lang)
        print(f"离线翻译结果: {translated_text[:50]}...")
        
        return jsonify({
            "original_text": text,
            "translated_text": translated_text,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "mode": "offline"
        })
        
    except Exception as e:
        print(f"翻译错误: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/languages', methods=['GET'])
def get_languages():
    """获取支持的语言列表"""
    print("收到获取语言列表请求")
    languages = {
        "zh": "中文",
        "en": "英语",
        "ja": "日语",
        "ko": "韩语",
        "fr": "法语",
        "de": "德语",
        "es": "西班牙语",
        "ru": "俄语",
        "ar": "阿拉伯语",
        "pt": "葡萄牙语",
        "it": "意大利语"
    }
    return jsonify(languages)

@app.route('/api/check', methods=['GET'])
def check_api():
    """检查API密钥是否已配置"""
    print("检查API配置")
    return jsonify({
        "status": "ok", 
        "message": "离线模式已启用", 
        "model": "离线模式",
        "offline_mode": True
    })

@app.route('/api/config', methods=['POST'])
def configure_api():
    """配置API密钥和模型"""
    print("收到API配置请求 - 离线模式")
    return jsonify({"status": "ok", "message": "离线模式已启用"})

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    print("收到健康检查请求")
    return jsonify({
        "status": "ok", 
        "message": "服务正常运行", 
        "model": "离线模式",
        "offline_mode": True
    })

if __name__ == '__main__':
    print(f"启动服务器: {HOST}:{PORT}, 调试模式: {DEBUG}")
    print(f"API访问地址: http://{HOST if HOST != '0.0.0.0' else 'localhost'}:{PORT}")
    print(f"使用离线翻译模式 - 不需要API密钥")
    print(f"支持的API端点: /api/translate, /api/languages, /api/check, /api/health")
    app.run(host=HOST, port=PORT, debug=DEBUG) 