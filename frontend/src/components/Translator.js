import React, { useState } from 'react';
import axios from 'axios';

function Translator({ languages, apiBaseUrl, onViewHistory }) {
  const [sourceLang, setSourceLang] = useState('auto');
  const [targetLang, setTargetLang] = useState('en');
  const [sourceText, setSourceText] = useState('');
  const [translatedText, setTranslatedText] = useState('');
  const [isTranslating, setIsTranslating] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [useStreaming, setUseStreaming] = useState(true);

  const handleTranslate = async () => {
    if (!sourceText.trim()) {
      setError('请输入需要翻译的文本');
      return;
    }

    try {
      setIsTranslating(true);
      setError(null);
      setSuccess(null);
      
      if (useStreaming) {
        await handleStreamingTranslate();
      } else {
        await handleRegularTranslate();
      }
    } catch (err) {
      console.error('翻译错误:', err);
      if (err.response) {
        const errorMsg = err.response.data.error || '翻译服务出错';
        setError(errorMsg);
      } else if (err.request) {
        setError(
          <div>
            <p>服务器无响应或请求超时</p>
            <p style={{marginTop: '0.5rem'}}>当前超时设置：300秒</p>
          </div>
        );
      } else {
        setError('请求错误: ' + err.message);
      }
    } finally {
      setIsTranslating(false);
    }
  };

  const handleRegularTranslate = async () => {
    console.log(`发送翻译请求到: ${apiBaseUrl}/api/translate`);
    console.log(`从 ${sourceLang} 翻译到 ${targetLang}: ${sourceText.substring(0, 30)}...`);

    const response = await axios.post(`${apiBaseUrl}/api/translate`, {
      text: sourceText,
      source_lang: sourceLang,
      target_lang: targetLang
    }, {
      timeout: 300000
    });

    console.log('翻译完成');
    setTranslatedText(response.data.translated_text);
    setSuccess('翻译成功！');
    
    setTimeout(() => {
      setSuccess(null);
    }, 3000);
  };

  const handleStreamingTranslate = async () => {
    console.log(`发送流式翻译请求到: ${apiBaseUrl}/api/translate/stream`);
    console.log(`从 ${sourceLang} 翻译到 ${targetLang}: ${sourceText.substring(0, 30)}...`);
    
    setTranslatedText('');
    
    try {
      const url = new URL(`${apiBaseUrl}/api/translate/stream`);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: sourceText,
          source_lang: sourceLang,
          target_lang: targetLang
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || '流式翻译请求失败');
      }
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let translationCompleted = false;
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const text = decoder.decode(value, { stream: true });
        
        const lines = text.split('\n\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.substring(6));
              
              if (data.type === 'update') {
                setTranslatedText(data.text);
              } else if (data.type === 'end') {
                if (!translationCompleted) {
                  translationCompleted = true;
                  setSuccess('翻译成功！');
                  setTimeout(() => {
                    setSuccess(null);
                  }, 3000);
                }
              } else if (data.type === 'error') {
                setError(data.message || '翻译过程中出错');
              }
            } catch (err) {
              console.error('解析流数据失败:', err, line);
            }
          }
        }
      }
    } catch (err) {
      console.error('流式翻译错误:', err);
      throw err;
    }
  };

  const handleClear = () => {
    setSourceText('');
    setTranslatedText('');
    setError(null);
    setSuccess(null);
  };

  const handleSwapLanguages = () => {
    if (sourceLang === 'auto') return;
    
    const temp = sourceLang;
    setSourceLang(targetLang);
    setTargetLang(temp);
    
    if (translatedText) {
      setSourceText(translatedText);
      setTranslatedText(sourceText);
    }
  };

  const handleKeyDown = (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
      handleTranslate();
    }
  };

  const handleViewHistory = () => {
    if (typeof onViewHistory === 'function') {
      onViewHistory();
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
            style={{minHeight: '200px'}}
          />
          <div className="text-counter" style={{textAlign: 'right', fontSize: '0.8rem', color: '#666'}}>
            {translatedText.length} 字符
          </div>
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
        <button className="history-button" onClick={handleViewHistory}>
          查看历史记录
        </button>
        <label className="stream-toggle">
          <input
            type="checkbox"
            checked={useStreaming}
            onChange={(e) => setUseStreaming(e.target.checked)}
          />
          实时翻译
        </label>
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