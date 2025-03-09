import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../styles/TranslationHistory.css';

// 定义Java后端API URL
const JAVA_API_BASE_URL = window.location.hostname === 'localhost' 
  ? 'http://localhost:8080/api' 
  : `http://${window.location.hostname}:8080/api`;

function TranslationHistory({ onBack }) {
  const [translations, setTranslations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [searchText, setSearchText] = useState('');
  const [stats, setStats] = useState({ total: 0, today: 0 });
  // 添加模态对话框状态
  const [modalVisible, setModalVisible] = useState(false);
  const [modalContent, setModalContent] = useState({ originalText: '', translatedText: '', sourceLang: '', targetLang: '' });

  // 每页显示的记录数
  const pageSize = 10;

  // 加载翻译历史记录
  const fetchTranslations = async (page = 0) => {
    try {
      setLoading(true);
      setError(null);

      let url = `${JAVA_API_BASE_URL}/translations/search?page=${page}&size=${pageSize}`;
      if (searchText) {
        url += `&text=${encodeURIComponent(searchText)}`;
      }

      console.log(`加载翻译历史记录: ${url}`);
      const response = await axios.get(url);
      
      console.log('翻译历史记录:', response.data);
      setTranslations(response.data.content || []);
      setTotalPages(response.data.totalPages || 0);
      setCurrentPage(page);
    } catch (err) {
      console.error('加载翻译历史记录失败:', err);
      setError('无法加载翻译历史记录，请确保Java后端服务正在运行');
    } finally {
      setLoading(false);
    }
  };

  // 加载统计数据
  const fetchStats = async () => {
    try {
      console.log(`加载统计数据: ${JAVA_API_BASE_URL}/translations/stats`);
      const response = await axios.get(`${JAVA_API_BASE_URL}/translations/stats`);
      
      setStats({
        total: response.data.totalTranslations || 0,
        today: response.data.todayTranslations || 0
      });
    } catch (err) {
      console.error('加载统计数据失败:', err);
    }
  };

  // 删除翻译记录
  const deleteTranslation = async (id) => {
    if (!window.confirm('确定要删除这条翻译记录吗？')) {
      return;
    }
    
    try {
      await axios.delete(`${JAVA_API_BASE_URL}/translations/${id}`);
      setTranslations(translations.filter(t => t.id !== id));
      fetchStats(); // 刷新统计数据
    } catch (err) {
      console.error('删除翻译记录失败:', err);
      alert('删除记录失败');
    }
  };

  // 初始加载
  useEffect(() => {
    fetchTranslations();
    fetchStats();
  }, []);

  // 执行搜索
  const handleSearch = (e) => {
    e.preventDefault();
    fetchTranslations(0); // 搜索时重置到第一页
  };

  // 切换页码
  const goToPage = (page) => {
    if (page >= 0 && page < totalPages) {
      fetchTranslations(page);
    }
  };

  // 格式化日期
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN');
  };

  // 返回翻译界面
  const handleBack = () => {
    if (typeof onBack === 'function') {
      onBack();
    }
  };

  // 显示完整翻译内容
  const showFullTranslation = (translation) => {
    setModalContent({
      originalText: translation.originalText,
      translatedText: translation.translatedText,
      sourceLang: translation.sourceLang,
      targetLang: translation.targetLang
    });
    setModalVisible(true);
  };

  // 关闭模态对话框
  const closeModal = () => {
    setModalVisible(false);
  };

  return (
    <div className="translation-history">
      {/* 模态对话框 */}
      {modalVisible && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>完整翻译内容</h3>
              <button className="close-button" onClick={closeModal}>&times;</button>
            </div>
            <div className="modal-body">
              <div className="translation-details">
                <div className="translation-section">
                  <h4>原文 ({modalContent.sourceLang}):</h4>
                  <div className="full-text">{modalContent.originalText}</div>
                </div>
                <div className="translation-section">
                  <h4>译文 ({modalContent.targetLang}):</h4>
                  <div className="full-text">{modalContent.translatedText}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="history-header">
        <h2>翻译历史记录</h2>
        <button className="back-button" onClick={handleBack}>返回翻译</button>
      </div>

      <div className="stats-container">
        <div className="stat-box">
          <h3>总翻译次数</h3>
          <p>{stats.total}</p>
        </div>
        <div className="stat-box">
          <h3>今日翻译</h3>
          <p>{stats.today}</p>
        </div>
      </div>

      <div className="search-container">
        <form onSubmit={handleSearch}>
          <input
            type="text"
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            placeholder="搜索翻译内容..."
          />
          <button type="submit">搜索</button>
        </form>
      </div>

      {loading ? (
        <div className="loading-indicator">加载中...</div>
      ) : error ? (
        <div className="error-message">{error}</div>
      ) : translations.length === 0 ? (
        <div className="no-records">没有找到翻译记录</div>
      ) : (
        <>
          <div className="translations-table">
            <table>
              <thead>
                <tr>
                  <th>原文</th>
                  <th>译文</th>
                  <th>语言</th>
                  <th>时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {translations.map(translation => (
                  <tr key={translation.id}>
                    <td className="text-cell">{translation.originalText}</td>
                    <td className="text-cell">{translation.translatedText}</td>
                    <td>{`${translation.sourceLang} → ${translation.targetLang}`}</td>
                    <td>{formatDate(translation.createdAt)}</td>
                    <td>
                      <div className="action-buttons">
                        <button 
                          className="view-button"
                          onClick={() => showFullTranslation(translation)}
                        >
                          查看完整
                        </button>
                        <button 
                          className="delete-button"
                          onClick={() => deleteTranslation(translation.id)}
                        >
                          删除
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <button 
                onClick={() => goToPage(currentPage - 1)} 
                disabled={currentPage === 0}
              >
                上一页
              </button>
              <span>第 {currentPage + 1} 页，共 {totalPages} 页</span>
              <button 
                onClick={() => goToPage(currentPage + 1)} 
                disabled={currentPage === totalPages - 1}
              >
                下一页
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default TranslationHistory; 