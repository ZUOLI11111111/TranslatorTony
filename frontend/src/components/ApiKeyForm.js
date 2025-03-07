import React, { useState } from 'react';
import axios from 'axios';

function ApiKeyForm({ onApiConfigured, apiBaseUrl }) {
  const [apiKey, setApiKey] = useState('');
  const [model, setModel] = useState('deepseek-chat');
  const [apiUrl, setApiUrl] = useState('https://api.deepseek.com');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!apiKey.trim()) {
      setError('请输入API密钥');
      return;
    }
    
    try {
      setIsSubmitting(true);
      setError(null);
      setSuccess(null);
      
      console.log(`发送API配置请求到: ${apiBaseUrl}/api/config`);
      // 向后端发送API密钥
      const response = await axios.post(`${apiBaseUrl}/api/config`, {
        api_key: apiKey,
        model: model,
        api_url: apiUrl
      });
      
      console.log("API配置响应:", response.data);
      
      if (response.data.status === 'ok') {
        setSuccess('API密钥设置成功！');
        setTimeout(() => {
          onApiConfigured();
        }, 1500);
      } else {
        setError(response.data.message || '配置失败');
      }
    } catch (err) {
      console.error("API配置错误:", err);
      if (err.response) {
        // 服务器返回了错误
        setError(err.response.data.error || '服务器错误');
      } else if (err.request) {
        // 请求发送了但没有收到响应
        setError('服务器无响应，请确保后端服务正在运行');
      } else {
        // 请求出错
        setError('请求错误: ' + err.message);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="api-key-form">
      <h2>配置DeepSeek API</h2>
      <p>请提供您的DeepSeek API密钥以使用翻译功能。您的密钥将安全存储在本地，仅用于处理翻译请求。</p>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="apiKey">DeepSeek API密钥</label>
          <input
            type="password"
            id="apiKey"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="sk-..."
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="model">模型选择</label>
          <select 
            id="model" 
            value={model} 
            onChange={(e) => setModel(e.target.value)}
          >
            <option value="deepseek-r1">DeepSeek R1 (最新版本)</option>
            <option value="deepseek-chat">DeepSeek Chat (通用对话)</option>
            <option value="deepseek-coder">DeepSeek Coder (代码生成)</option>
            <option value="deepseek-lite">DeepSeek Lite (轻量版)</option>
          </select>
        </div>
        
        <div className="advanced-toggle" style={{margin: '1rem 0', textAlign: 'right'}}>
          <button 
            type="button" 
            onClick={() => setShowAdvanced(!showAdvanced)} 
            style={{background: 'transparent', border: 'none', color: '#1a73e8', cursor: 'pointer'}}
          >
            {showAdvanced ? '隐藏高级选项 ▲' : '显示高级选项 ▼'}
          </button>
        </div>
        
        {showAdvanced && (
          <div className="form-group">
            <label htmlFor="apiUrl">API端点URL</label>
            <input
              type="text"
              id="apiUrl"
              value={apiUrl}
              onChange={(e) => setApiUrl(e.target.value)}
              placeholder="https://api.deepseek.com"
            />
            <p style={{fontSize: '0.8rem', color: '#666', marginTop: '0.5rem'}}>
              仅设置API的基础URL（如https://api.deepseek.com），系统会自动添加必要的路径
            </p>
          </div>
        )}
        
        <button 
          type="submit" 
          className="translate-button"
          disabled={isSubmitting}
        >
          {isSubmitting ? (
            <>
              <div className="loading"></div>
              保存中...
            </>
          ) : '保存配置'}
        </button>
        
        {error && (
          <div className="status error">
            {error}
          </div>
        )}
        
        {success && (
          <div className="status success">
            {success}
          </div>
        )}
      </form>
    </div>
  );
}

export default ApiKeyForm; 