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

# 配置DeepSeek API密钥
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com')
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')


print(f"API配置状态: {'已配置' if DEEPSEEK_API_KEY else '未配置'}")
print(f"使用模型:  DEEPSEEK_MODEL")
print(f"API基础URL: {DEEPSEEK_API_URL}")
print(f"完整API路径: {DEEPSEEK_API_URL}/v1/chat/completions")

@app.route('/')
def index():
    """首页 - 返回API状态信息"""
    return jsonify({
        "status": "ok",
        "message": "翻译API服务正在运行",
        "model": DEEPSEEK_MODEL,
        "endpoints": [
            "/api/translate - 翻译API",
            "/api/languages - 获取支持的语言",
            "/api/check - 检查API密钥",
            "/api/config - 配置API密钥",
            "/api/health - 健康检查"
        ]
    })


def call_deepseek_api(messages, model="deepseek-chat"):
    """调用DeepSeek API，包含错误处理"""
    try:
        print(f"调用DeepSeek API，模型: {model}")
        print(f"API基础URL: {DEEPSEEK_API_URL}")
        print(f"请求URL: {DEEPSEEK_API_URL}/v1/chat/completions")
                
        # 检查API密钥
        if not DEEPSEEK_API_KEY:
            raise ValueError("未配置DeepSeek API密钥")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 4096
        }
        
        print(f"发送请求到DeepSeek API，模型: {model}")
        response = requests.post(
            f"{DEEPSEEK_API_URL}/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=120  # 增加超时时间到2分钟
        )
        
        # 检查请求是否成功
        response.raise_for_status()
        result = response.json()
        print("API请求成功")
        return result
        
    except requests.exceptions.Timeout as e:
        print(f"API请求超时: {str(e)}")
        raise ValueError(f"API请求超时。详细错误: {str(e)}")
    except requests.exceptions.HTTPError as e:
        print(f"API HTTP错误: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            status_code = e.response.status_code
            if status_code == 404:
                raise ValueError(f"API端点未找到(404)。请检查API URL是否正确: {DEEPSEEK_API_URL}/v1/chat/completions")
            elif status_code == 401:
                raise ValueError("API密钥无效或已过期(401)")
            else:
                raise ValueError(f"API HTTP错误({status_code}): {str(e)}")
        else:
            raise ValueError(f"API HTTP错误: {str(e)}")
    except requests.exceptions.RequestException as e:
        print(f"API请求失败: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print(f"响应状态码: {e.response.status_code}")
            print(f"响应内容: {e.response.text}")
        
    except Exception as e:
        print(f"处理API请求时出错: {str(e)}")
        # 处理其他异常
        return {
            "choices": [
                {
                    "message": {
                        "content": f"[错误] 调用API时出现问题: {str(e)}"
                    }
                }
            ]
        }

@app.route('/api/translate', methods=['POST'])
def translate():
    """
    翻译API端点
    请求JSON格式:
    {
        "text": "要翻译的文本",
        "source_lang": "源语言代码(可选)",
        "target_lang": "目标语言代码"
    }
    """
    print("收到翻译请求")
    if not DEEPSEEK_API_KEY:
        return jsonify({"error": "未配置API密钥"}), 500
        
    try:
        data = request.json
        print(f"翻译请求数据: {data}")
        
        if not data:
            return jsonify({"error": "未收到有效的JSON数据"}), 400
            
        text = data.get('text', '')
        source_lang = data.get('source_lang', config.DEFAULT_SOURCE_LANG)
        target_lang = data.get('target_lang', config.DEFAULT_TARGET_LANG)
        
        if not text:
            return jsonify({"error": "文本不能为空"}), 400
            
        # 准备翻译提示
        if source_lang == 'auto':
            prompt = f"将以下文本翻译成{target_lang}语言:\n\n{text}"
        else:
            prompt = f"将以下{source_lang}文本翻译成学生写的实验报告且机器味道不浓的{target_lang}语言:\n\n{text}"
        
        print(f"翻译提示: {prompt[:50]}...")
        
        
        
        # 调用DeepSeek API
        messages = [
            {"role": "system", "content": "你是一个专业翻译助手，能够准确流畅地进行多语言翻译。"},
            {"role": "user", "content": prompt}
        ]
        
        model = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
        response = call_deepseek_api(messages, model)
        
        # 从响应中提取翻译文本
        translated_text = response['choices'][0]['message']['content'].strip()
        print(f"翻译结果: {translated_text[:50]}...")
        
        return jsonify({
            "original_text": text,
            "translated_text": translated_text,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "mode": "api"
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
    
    if DEEPSEEK_API_KEY:
        return jsonify({
            "status": "ok", 
            "message": "API密钥已配置", 
            "model": DEEPSEEK_MODEL,
            "offline_mode": False
        })
    else:
        return jsonify({"status": "error", "message": "API密钥未配置"}), 500

@app.route('/api/config', methods=['POST'])
def configure_api():
    """配置API密钥和模型"""
    # 声明全局变量 - 必须在函数开始处声明
    global DEEPSEEK_API_KEY, DEEPSEEK_MODEL, DEEPSEEK_API_URL, OFFLINE_MODE
    
    print("收到API配置请求")
    try:
        data = request.json
        print(f"配置数据: {data}")
        if not data:
            return jsonify({"error": "未收到有效的JSON数据"}), 400
        
        
        
        # 正常API模式，需要API密钥
        api_key = data.get('api_key')
        model = data.get('model', 'deepseek-chat')
        api_url = data.get('api_url', 'https://api.deepseek.com')
        
        if not api_key:
            return jsonify({"error": "API密钥不能为空"}), 400
    except Exception as e:
        print(f"配置保存失败: {str(e)}")
        return jsonify({"error": f"配置保存失败: {str(e)}"}), 500

# 添加一个简单的健康检查端点
@app.route('/api/health', methods=['GET'])
def health_check():
    print("收到健康检查请求")
    return jsonify({
        "status": "ok", 
        "message": "服务正常运行", 
        "model": DEEPSEEK_MODEL,
    })

# 确保调试信息直接输出到控制台
if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'True') == 'True'
    
    print(f"启动服务器: {host}:{port}, 调试模式: {debug}")
    print(f"API访问地址: http://{host if host != '0.0.0.0' else 'localhost'}:{port}")
    print(f"支持的API端点: /api/translate, /api/languages, /api/check, /api/config, /api/health")
    app.run(host=host, port=port, debug=debug)
