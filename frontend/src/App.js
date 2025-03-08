import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Translator from './components/Translator';
import ApiKeyForm from './components/ApiKeyForm';
import TranslationHistory from './components/TranslationHistory';
import './styles/App.css';

// 配置axios的默认URL和超时 - 指定完整的协议和端口
const API_BASE_URL = window.location.hostname === 'localhost' 
  ? 'http://localhost:5000' 
  : `http://${window.location.hostname}:5000`;

// 不设置默认baseURL，在每个请求中明确指定完整URL
axios.defaults.timeout = 300000; // 设置全局超时为300秒（5分钟），与后端保持一致

// 添加调试信息
console.log(`应用启动，API地址: ${API_BASE_URL}`);
console.log(`全局请求超时设置: ${axios.defaults.timeout/1000}秒`);

function App() {
  const [isApiConfigured, setIsApiConfigured] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [languages, setLanguages] = useState({});
  const [backendStatus, setBackendStatus] = useState('检查中...');
  const [activeView, setActiveView] = useState('translator'); // 'translator' 或 'history'

  useEffect(() => {
    // 首先检查后端服务是否可用
    checkBackendHealth();
  }, []);

  const checkBackendHealth = async () => {
    try {
      setIsLoading(true);
      setBackendStatus('尝试连接后端...');
      console.log(`尝试连接后端健康检查: ${API_BASE_URL}/api/health`);
      
      // 先检查健康状态
      const healthResponse = await axios.get(`${API_BASE_URL}/api/health`, {
        timeout: 5000 // 缩短超时时间以快速检测问题
      });
      console.log('后端健康检查响应:', healthResponse.data);
      
      setBackendStatus('后端连接成功');
      // 然后检查API密钥
      checkApiConfiguration();
      // 获取支持的语言列表
      fetchLanguages();
    } catch (err) {
      console.error('无法连接到后端服务:', err);
      
      // 尝试不同端点
      try {
        console.log('尝试连接另一个端点...');
        const response = await axios.get(`${API_BASE_URL}/api/languages`, {
          timeout: 5000
        });
        console.log('语言列表响应:', response.data);
        setBackendStatus('后端连接成功(语言列表)');
        setLanguages(response.data);
        checkApiConfiguration();
      } catch (innerErr) {
        console.error('所有端点连接失败:', innerErr);
        setBackendStatus('后端连接失败');
        setError(
          <div>
            <p>无法连接到后端服务 ({API_BASE_URL})</p>
            <p>错误: {innerErr.message}</p>
            <p>请确保后端服务已启动，并且端口5000可访问</p>
            <p><strong>提示:</strong> 请在后端目录运行: <code>python3 app.py</code></p>
          </div>
        );
        setIsApiConfigured(false);
        setIsLoading(false);
      }
    }
  };

  const checkApiConfiguration = async () => {
    try {
      console.log(`检查API配置: ${API_BASE_URL}/api/check`);
      const response = await axios.get(`${API_BASE_URL}/api/check`);
      console.log('API配置结果:', response.data);
      setIsApiConfigured(response.data.status === 'ok');
      setError(null);
    } catch (err) {
      console.error('API配置检查失败:', err);
      if (err.response) {
        // 后端返回的错误
        setError(err.response.data.error || '后端服务响应错误');
      } else if (err.request) {
        // 请求发送成功，但没有收到响应
        setError('后端服务无响应，请确保服务正在运行');
      } else {
        // 请求设置有问题
        setError('请求失败: ' + err.message);
      }
      setIsApiConfigured(false);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchLanguages = async () => {
    try {
      console.log(`获取语言列表: ${API_BASE_URL}/api/languages`);
      const response = await axios.get(`${API_BASE_URL}/api/languages`);
      console.log('语言列表:', response.data);
      setLanguages(response.data);
    } catch (err) {
      console.error('获取语言列表失败:', err);
    }
  };

  const handleApiConfigured = () => {
    setIsApiConfigured(true);
    checkApiConfiguration(); // 重新验证
  };

  // 切换到翻译视图
  const showTranslator = () => {
    setActiveView('translator');
  };

  // 切换到历史记录视图
  const showHistory = () => {
    setActiveView('history');
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1>智能翻译助手</h1>
        <p>基于LLM API的本地翻译工具</p>
        
        {isApiConfigured && (
          <div className="nav-buttons">
            <button 
              className={activeView === 'translator' ? 'active' : ''} 
              onClick={showTranslator}
            >
              翻译
            </button>
            <button 
              className={activeView === 'history' ? 'active' : ''} 
              onClick={showHistory}
            >
              历史记录
            </button>
          </div>
        )}
      </header>

      {backendStatus !== '后端连接成功' && backendStatus !== '后端连接成功(语言列表)' && (
        <div className="status" style={{ marginBottom: '1rem', padding: '0.5rem', background: '#f8f9fa', textAlign: 'center' }}>
          <p>后端状态: {backendStatus}</p>
          <p style={{fontSize: '0.8rem', color: '#666'}}>API地址: {API_BASE_URL}</p>
        </div>
      )}

      {isLoading ? (
        <div className="status">
          <div className="loading"></div>
          <span>正在连接后端服务...</span>
        </div>
      ) : error ? (
        <div className="status error">
          {error}
        </div>
      ) : isApiConfigured ? (
        activeView === 'translator' ? (
          <Translator languages={languages} apiBaseUrl={API_BASE_URL} onViewHistory={showHistory} />
        ) : (
          <TranslationHistory onBack={showTranslator} />
        )
      ) : (
        <ApiKeyForm onApiConfigured={handleApiConfigured} apiBaseUrl={API_BASE_URL} />
      )}
    </div>
  );
}

export default App; 