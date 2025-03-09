from flask import Flask, request, jsonify, stream_with_context, Response
from flask_cors import CORS
import requests
import config
import os
import json
import time
from dotenv import load_dotenv
import threading

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
            "max_tokens": 8192
        }
        
        print(f"发送请求到DeepSeek API，模型: {model}")
        response = requests.post(
            f"{DEEPSEEK_API_URL}/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=300  # 增加超时时间到5分钟
        )
        
        # 检查请求是否成功
        response.raise_for_status()
        result = response.json()
        print("API请求成功")
        return result
        
    except requests.exceptions.Timeout as e:
        print(f"API请求超时: {str(e)}")
        raise
    except requests.exceptions.HTTPError as e:
        print(f"API请求HTTP错误: {str(e)}")
        # 尝试获取更详细的错误信息
        try:
            error_data = e.response.json()
            print(f"错误详情: {error_data}")
        except:
            pass
        raise
    except Exception as e:
        print(f"API请求错误: {str(e)}")
        raise

def call_deepseek_api_streaming(messages, model="deepseek-chat"):
    """调用DeepSeek API的流式版本，使用流式模式"""
    try:
        print(f"调用DeepSeek API（流式模式），模型: {model}")
        print(f"API基础URL: {DEEPSEEK_API_URL}")
        
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
            "max_tokens": 8192,
            "stream": True  # 启用流式响应
        }
        
        print(f"发送流式请求到DeepSeek API，模型: {model}")
        response = requests.post(
            f"{DEEPSEEK_API_URL}/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=300,  # 增加超时时间到5分钟
            stream=True   # 启用流式响应
        )
        
        # 检查请求是否成功
        response.raise_for_status()
        return response
        
    except Exception as e:
        print(f"流式API请求错误: {str(e)}")
        raise

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
        
        
        
        # 调用deepseek API
        messages = [
            {"role": "system", "content": "你是一个专业翻译助手，能够准确流畅地进行多语言翻译。"},
            {"role": "user", "content": prompt}
        ]
        
        model = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
        response = call_deepseek_api(messages, model)
        
        # 从响应中提取翻译文本
        translated_text = response['choices'][0]['message']['content'].strip()
        print(f"翻译结果: {translated_text[:50]}...")
        
        # 保存翻译记录到Java后端数据库
        try:
            storage_success = save_to_database(text, translated_text, source_lang, target_lang, request.remote_addr)
            if storage_success:
                print("数据存储成功")
            else:
                print("数据存储失败，但不影响翻译功能")
        except Exception as e:
            print(f"保存到数据库失败: {str(e)}")
            # 继续处理，不影响翻译结果返回
        
        return jsonify({
            "original_text": text,
            "translated_text": translated_text,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "mode": "api",
            "stored": storage_success if 'storage_success' in locals() else False
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

def save_to_database(original_text, translated_text, source_lang, target_lang, ip_address):
    """保存翻译记录到Java后端数据库"""
    java_backend_url = os.getenv('JAVA_BACKEND_URL', 'http://localhost:8080/api/translations')
    
    try:
        data = {
            "originalText": original_text,
            "translatedText": translated_text,
            "sourceLang": source_lang,
            "targetLang": target_lang,
            "ipAddress": ip_address,
            "model": DEEPSEEK_MODEL
        }
        
        # 发送POST请求到Java后端
        response = requests.post(
            java_backend_url,
            headers={"Content-Type": "application/json"},
            json=data,
            timeout=5  # 5秒超时
        )
        
        if response.status_code == 201:
            print("翻译记录已保存到数据库")
            return True
        else:
            print(f"保存到数据库失败: HTTP {response.status_code}")
            print(response.text)
            return False
    
    except Exception as e:
        print(f"连接Java后端失败: {str(e)}")
        # 这里我们只记录错误，不阻止主要功能
        return False

@app.route('/api/translate/stream', methods=['POST'])
def translate_stream():
    """
    流式翻译API端点
    请求JSON格式:
    {
        "text": "要翻译的文本",
        "source_lang": "源语言代码(可选)",
        "target_lang": "目标语言代码"
    }
    """
    print("收到流式翻译请求")
    if not DEEPSEEK_API_KEY:
        return jsonify({"error": "未配置API密钥"}), 500
        
    try:
        data = request.json
        print(f"流式翻译请求数据: {data}")
        
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
        
        print(f"流式翻译提示: {prompt[:50]}...")
        
        # 调用DeepSeek API (流式模式)
        messages = [
            {"role": "system", "content": "你是一个专业翻译助手，能够准确流畅地进行多语言翻译。"},
            {"role": "user", "content": prompt}
        ]
        
        model = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
        
        def generate():
            # 首先发送一个初始化事件，让前端知道连接已建立
            yield f"data: {json.dumps({'type': 'start', 'source_lang': source_lang, 'target_lang': target_lang})}\n\n"
            
            try:
                # 调用流式API
                api_response = call_deepseek_api_streaming(messages, model)
                
                # 流式处理响应
                partial_message = ""
                for line in api_response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data_str = line[6:]  # 去掉 "data: " 前缀
                            if data_str != '[DONE]':
                                try:
                                    data_json = json.loads(data_str)
                                    if 'choices' in data_json:
                                        delta = data_json['choices'][0].get('delta', {})
                                        if 'content' in delta:
                                            content = delta['content']
                                            partial_message += content
                                            # 发送当前的增量内容和累积的内容
                                            response_data = {
                                                'type': 'update',
                                                'delta': content,
                                                'text': partial_message
                                            }
                                            yield f"data: {json.dumps(response_data)}\n\n"
                                except json.JSONDecodeError:
                                    print(f"无法解析JSON: {data_str}")
                
                # 翻译完成后发送完成事件
                yield f"data: {json.dumps({'type': 'end', 'text': partial_message})}\n\n"
                
                # 保存翻译结果到数据库（异步，不影响响应）
                try:
                    threading.Thread(
                        target=save_to_database,
                        args=(text, partial_message, source_lang, target_lang, request.remote_addr)
                    ).start()
                except Exception as e:
                    print(f"异步保存到数据库失败: {str(e)}")
                    
            except Exception as e:
                print(f"流式翻译过程中出错: {str(e)}")
                error_data = {'type': 'error', 'message': str(e)}
                yield f"data: {json.dumps(error_data)}\n\n"
        
        # 返回流式响应
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',  # 防止Nginx缓冲
                'Connection': 'keep-alive'
            }
        )
        
    except Exception as e:
        print(f"流式翻译错误: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 确保调试信息直接输出到控制台
if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'True') == 'True'
    
    print(f"启动服务器: {host}:{port}, 调试模式: {debug}")
    print(f"API访问地址: http://{host if host != '0.0.0.0' else 'localhost'}:{port}")
    print(f"支持的API端点: /api/translate, /api/languages, /api/check, /api/config, /api/health")
    app.run(host=host, port=port, debug=debug)
