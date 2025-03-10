import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import config
import os
import threading
from dotenv import load_dotenv
import time

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

# 配置llm API密钥
API_KEY = os.getenv('CHATGLM_API_KEY')
API_URL = os.getenv('CHATGLM_API_URL')
MODEL = os.getenv('CHATGLM_MODEL')


print(f"API配置状态: {'已配置' if API_KEY else '未配置'}")
print(f"使用模型:  MODEL")
print(f"API基础URL: {API_URL}")
print(f"完整API路径: {API_URL}")

@app.route('/')
def index():
    """首页 - 返回API状态信息"""
    return jsonify({
        "status": "ok",
        "message": "翻译API服务正在运行",
        "model": MODEL,
        "endpoints": [
            "/api/translate - 翻译API",
            "/api/languages - 获取支持的语言",
            "/api/check - 检查API密钥",
            "/api/config - 配置API密钥",
            "/api/health - 健康检查"
        ]
    })


def call_llm_api(messages, model):
    """调用llm API，包含错误处理"""
    try:
        print(f"调用llm API，模型: {model}")
        print(f"API基础URL: {API_URL}")
        print(f"请求URL: {API_URL}")
                
        # 检查API密钥
        if not API_KEY:
            raise ValueError("未配置API密钥")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 8192
        }
        
        print(f"发送请求到llm API，模型: {model}")
        response = requests.post(
            f"{API_URL}",
            headers=headers,
            json=payload,
            timeout=300  
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
                raise ValueError(f"API端点未找到(404)。请检查API URL是否正确: {API_URL}")
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
    if not API_KEY:
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
        
        
        
        # 调用LLM API
        messages = [
            {"role": "system", "content": "你是一个专业翻译助手，能够准确流畅地进行多语言翻译。"},
            {"role": "user", "content": prompt}
        ]
        
        model = os.getenv('CHATGLM_MODEL')
        print(f"使用模型: {model}")
        response = call_llm_api(messages, model)
        
        # 从响应中提取翻译文本
        translated_text = response['choices'][0]['message']['content'].strip()
        print(f"翻译结果: {translated_text[:50]}...")
        
        # 尝试保存翻译记录，但不影响翻译结果返回
        try:
            ip_address = request.remote_addr
            save_result = save_to_database(text, translated_text, source_lang, target_lang, ip_address)
            if save_result:
                print("翻译记录已成功保存到数据库")
            else:
                print("保存到数据库失败，但继续返回翻译结果")
        except Exception as e:
            print(f"保存到数据库过程中出错: {str(e)}")
        
        # 无论数据库保存成功与否，都返回翻译结果
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
    
    if API_KEY:
        return jsonify({
            "status": "ok", 
            "message": "API密钥已配置", 
            "model": MODEL,
            "offline_mode": False
        })
    else:
        return jsonify({"status": "error", "message": "API密钥未配置"}), 500

@app.route('/api/config', methods=['POST'])
def configure_api():
    """配置API密钥和模型"""
    # 声明全局变量 - 必须在函数开始处声明
    global API_KEY, MODEL, API_URL
    
    print("收到API配置请求")
    try:
        data = request.json
        print(f"配置数据: {data}")
        if not data:
            return jsonify({"error": "未收到有效的JSON数据"}), 400
        
        
        
        # 正常API模式，需要API密钥
        api_key = data.get('api_key')
        
        
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
        "model": MODEL,
    })

def save_to_database(original_text, translated_text, source_lang, target_lang, ip_address):
    """保存翻译记录到Java后端数据库"""
    java_backend_url = os.getenv('JAVA_BACKEND_URL', 'http://localhost:8080/api/translations')
    
    print(f"开始保存翻译记录到Java后端...")
    print(f"Java后端URL: {java_backend_url}")
    print(f"IP地址: {ip_address}")
    
    if not translated_text or len(translated_text.strip()) == 0:
        print("❌ 译文为空，拒绝保存到数据库")
        return False
    
    try:
        data = {
            "originalText": original_text,
            "translatedText": translated_text,
            "sourceLang": source_lang,
            "targetLang": target_lang,
            "ipAddress": ip_address,
            "model": MODEL
        }
        
        print(f"准备发送数据到Java后端，数据大小: {len(str(data))} 字节")
        
        # 发送POST请求到Java后端
        response = requests.post(
            java_backend_url,
            headers={"Content-Type": "application/json"},
            json=data,
            timeout=10  # 增加超时时间到10秒
        )
        
        print(f"Java后端响应状态码: {response.status_code}")
        response_text = response.text[:200] + "..." if len(response.text) > 200 else response.text
        print(f"Java后端响应内容: {response_text}")  
        
        if response.status_code == 201:
            print("✅ 翻译记录已成功保存到数据库")
            return True
        else:
            print(f"❌ 保存到数据库失败: HTTP {response.status_code}")
            print(f"错误详情: {response.text}")
            # 尝试保存到本地文件作为备份
            save_to_backup_file(data)
            return False
    
    except requests.exceptions.ConnectionError as e:
        print(f"❌ 连接Java后端失败 (连接错误): {str(e)}")
        print("请确保Java后端服务正在运行，可以使用 ./start-java-backend.sh 启动")
        # 保存到本地文件作为备份
        save_to_backup_file(data)
        return False
    except requests.exceptions.Timeout as e:
        print(f"❌ 连接Java后端超时: {str(e)}")
        print("Java后端响应时间过长，可能服务器负载过高")
        # 保存到本地文件作为备份
        save_to_backup_file(data)
        return False
    except Exception as e:
        print(f"❌ 保存到数据库时发生未知错误: {str(e)}")
        import traceback
        traceback.print_exc()
        # 保存到本地文件作为备份
        save_to_backup_file(data)
        return False

def save_to_backup_file(data):
    """当数据库保存失败时，将翻译记录保存到本地文件作为备份"""
    try:
        # 确保备份目录存在
        backup_dir = os.path.join(os.path.dirname(__file__), 'translation_backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # 创建带时间戳的文件名
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"translation_{timestamp}_{os.urandom(4).hex()}.json"
        filepath = os.path.join(backup_dir, filename)
        
        # 写入数据
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"✅ 翻译记录已备份到本地文件: {filepath}")
        return True
    except Exception as e:
        print(f"❌ 备份到本地文件时出错: {str(e)}")
        return False

def call_llm_api_streaming(messages, model):
    """调用llm API，包含错误处理"""
    try:
        print(f"调用llm API，模型: {model}")
        print(f"API基础URL: {API_URL}")
        print(f"请求URL: {API_URL}")
        
        # 检查API密钥
        if not API_KEY:
            raise ValueError("未配置API密钥")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 8192,
            "stream": True
        }
        
        print(f"发送请求到llm API，模型: {model}")      
        response = requests.post(
            f"{API_URL}",
            headers=headers,
            json=payload,
            timeout=300,
            stream=True
        )
        response.raise_for_status()
        return response
        
    except Exception as e:
        print(f"流式API请求错误: {str(e)}")
        raise

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
    if not API_KEY:
        return jsonify({"error": "未配置API密钥"}), 500
    try:
        data = request.json
        print(f"流式翻译请求数据: {data}")

        if not data:
            return jsonify({"error": "未收到有效的JSON数据"}), 400
            
        text = data.get('text', '')
        source_lang = data.get('source_lang', config.DEFAULT_SOURCE_LANG)
        target_lang = data.get('target_lang', config.DEFAULT_TARGET_LANG)
        
        # 重要：在请求上下文中获取IP地址，以便稍后在线程中使用
        client_ip = request.remote_addr
        
        if not text:
            return jsonify({"error": "文本不能为空"}), 400
            
        # 准备翻译提示
        if source_lang == 'auto':
            prompt = f"将以下文本翻译成{target_lang}语言:\n\n{text}"
        else:
            prompt = f"将以下{source_lang}机器味道不浓准确无误遇到人名或该语言固有名词也翻译成{target_lang}语言:\n\n{text}"
        
        messages = [
            {"role": "system", "content": "你是一个专业翻译助手，能够准确流畅地进行多语言翻译。"},
            {"role": "user", "content": prompt}
        ]
        
        model = os.getenv('CHATGLM_MODEL')
        print(f"使用模型: {model}")
        
        def buffered_streaming_generator():
            """带缓冲的流式生成器，捕获翻译结果并在翻译完成后一次性保存到数据库"""
            final_translation = ""
            
            # 调用原生的生成器函数
            api_response = call_llm_api_streaming(messages, model)
            
            # 首先发送一个初始化事件，让前端知道连接已建立
            yield f"data: {json.dumps({'type': 'start', 'source_lang': source_lang, 'target_lang': target_lang})}\n\n"
            
            # 逐行处理API返回的数据
            for line in api_response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]
                        if data_str != '[DONE]':
                            try:
                                data_json = json.loads(data_str)
                                if 'choices' in data_json:
                                    delta = data_json['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        content = delta['content']
                                        final_translation += content
                                        response_data = {
                                            'type': 'update',
                                            'delta': content,
                                            'text': final_translation
                                        }
                                        yield f"data: {json.dumps(response_data)}\n\n"
                            except json.JSONDecodeError:
                                print(f"无法解析JSON: {data_str}")
            
            # 整个翻译完成后，发送一次结束消息
            yield f"data: {json.dumps({'type': 'end', 'text': final_translation})}\n\n"
            
            # 翻译完成后一次性保存到数据库
            print(f"翻译完成，正在一次性保存到数据库，文本长度: {len(final_translation)}")
            print(f"翻译源语言: {source_lang}, 目标语言: {target_lang}")
            print(f"原文前30字符: {text[:30]}...")
            print(f"译文前30字符: {final_translation[:30]}...")
            
            # 使用独立线程保存，避免阻塞响应
            def save_task():
                try:
                    # 使用之前获取的IP地址，而不是从request中获取
                    result = save_to_database(text, final_translation, source_lang, target_lang, client_ip)
                    if result:
                        print(f"✅ 翻译结果已成功保存到数据库！")
                    else:
                        print(f"❌ 数据库保存失败，但不影响翻译结果")
                except Exception as e:
                    print(f"❌ 保存到数据库时出现异常: {str(e)}")
                    import traceback
                    traceback.print_exc()
            
            # 启动保存线程
            save_thread = threading.Thread(target=save_task)
            save_thread.daemon = True  # 设置为守护线程，不阻止主程序退出
            save_thread.start()
            print(f"数据库保存线程已启动 (ID: {save_thread.ident})")
        
        # 使用缓冲生成器创建流式响应
        return app.response_class(
            buffered_streaming_generator(),
            mimetype='text/event-stream'
        )
        
    except Exception as e:
        print(f"流式翻译过程中出错: {str(e)}")
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
