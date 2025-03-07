import React, { useState } from 'react';
import axios from 'axios';

function Translator({ languages, apiBaseUrl }) {
  const [sourceLang, setSourceLang] = useState('auto');
  const [targetLang, setTargetLang] = useState('en');
  const [sourceText, setSourceText] = useState('');
  const [translatedText, setTranslatedText] = useState('');
  const [isTranslating, setIsTranslating] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleTranslate = async () => {
    if (!sourceText.trim()) {
      setError('请输入需要翻译的文本');
      return;
    }

    try {
      setIsTranslating(true);
      setError(null);
      setSuccess(null);
      
      console.log(`发送翻译请求到: ${apiBaseUrl}/api/translate`);
      console.log(`从 ${sourceLang} 翻译到 ${targetLang}: ${sourceText.substring(0, 30)}...`);

      const response = await axios.post(`${apiBaseUrl}/api/translate`, {
        text: sourceText,
        source_lang: sourceLang,
        target_lang: targetLang
      }, {
        timeout: 120000 // 120秒超时，与后端一致
      });

      console.log('翻译完成');
      setTranslatedText(response.data.translated_text);
      setSuccess('翻译成功！');
      
      // 3秒后清除成功消息
      setTimeout(() => {
        setSuccess(null);
      }, 3000);
    } catch (err) {
      console.error('翻译错误:', err);
      if (err.response) {
        // 服务器返回了错误响应
        const errorMsg = err.response.data.error || '翻译服务出错';
        setError(errorMsg);
      } else if (err.request) {
        // 请求发送了但是没有收到响应
        setError(
          <div>
            <p>服务器无响应或请求超时</p>
            <p style={{marginTop: '0.5rem'}}>当前超时设置：120秒</p>
          </div>
        );
      } else {
        // 请求设置本身出了问题
        setError('请求错误: ' + err.message);
      }
    } finally {
      setIsTranslating(false);
    }
  };

  const handleClear = () => {
    setSourceText('');
    setTranslatedText('');
    setError(null);
    setSuccess(null);
  };

  const handleSwapLanguages = () => {
    // 不交换自动检测语言
    if (sourceLang === 'auto') return;
    
    const temp = sourceLang;
    setSourceLang(targetLang);
    setTargetLang(temp);
    
    // 如果已经有翻译结果，也交换文本
    if (translatedText) {
      setSourceText(translatedText);
      setTranslatedText(sourceText);
    }
  };

  // 处理按Enter键翻译
  const handleKeyDown = (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
      handleTranslate();
    }
  };

  return (
    <div className="translator">
      <div className="language-controls">
        <div className="language-select">
          <select 
            value={sourceLang} 
            onChange={(e) => setSourceLang(e.target.value)}
          >
            <option value="auto">自动检测</option>
            {Object.entries(languages).map(([code, name]) => (
              <option key={`source-${code}`} value={code}>
                {name}
              </option>
            ))}
          </select>
        </div>
        
        <button 
          className="swap-languages" 
          onClick={handleSwapLanguages}
          disabled={sourceLang === 'auto'}
          title={sourceLang === 'auto' ? '自动检测语言不能交换' : '交换语言'}
        >
          ⇄
        </button>
        
        <div className="language-select">
          <select 
            value={targetLang} 
            onChange={(e) => setTargetLang(e.target.value)}
          >
            {Object.entries(languages).map(([code, name]) => (
              <option key={`target-${code}`} value={code}>
                {name}
              </option>
            ))}
          </select>
        </div>
      </div>
      
      <div className="text-areas">
        <div className="text-area">
          <textarea
            value={sourceText}
            onChange={(e) => setSourceText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入要翻译的文本，然后点击'翻译'按钮或按Ctrl+Enter"
          />
          <div className="text-counter" style={{textAlign: 'right', fontSize: '0.8rem', color: '#666'}}>
            {sourceText.length} 字符
          </div>
        </div>
        <div className="text-area">
          <textarea
            value={translatedText}
            readOnly
            placeholder="翻译结果将显示在这里"
          />
        </div>
      </div>
      
      <div className="controls">
        <button 
          className="translate-button" 
          onClick={handleTranslate}
          disabled={isTranslating || !sourceText.trim()}
        >
          {isTranslating ? (
            <>
              <div className="loading"></div>
              翻译中...
            </>
          ) : '翻译'}
        </button>
        <button className="clear-button" onClick={handleClear}>
          清空
        </button>
      </div>
      
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
      
      <div className="keyboard-shortcuts" style={{textAlign: 'center', marginTop: '10px', fontSize: '0.8rem', color: '#666'}}>
        <p>快捷键: Ctrl+Enter - 翻译</p>
      </div>
    </div>
  );
}

export default Translator; 