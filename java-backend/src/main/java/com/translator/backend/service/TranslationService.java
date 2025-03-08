package com.translator.backend.service;

import com.translator.backend.model.TranslationRecord;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * 翻译服务接口
 */
public interface TranslationService {

    /**
     * 保存翻译记录
     */
    TranslationRecord saveTranslation(TranslationRecord translationRecord);
    
    /**
     * 根据ID查询翻译记录
     */
    Optional<TranslationRecord> findById(Long id);
    
    /**
     * 根据用户ID查询翻译记录
     */
    List<TranslationRecord> findByUserId(String userId);
    
    /**
     * 根据用户ID分页查询翻译记录
     */
    Page<TranslationRecord> findByUserId(String userId, Pageable pageable);
    
    /**
     * 根据源语言和目标语言查询记录
     */
    List<TranslationRecord> findBySourceLangAndTargetLang(String sourceLang, String targetLang);
    
    /**
     * 根据创建时间查询记录
     */
    List<TranslationRecord> findByCreatedAtBetween(LocalDateTime start, LocalDateTime end);
    
    /**
     * 搜索翻译记录
     */
    Page<TranslationRecord> searchTranslations(String text, String userId, Pageable pageable);
    
    /**
     * 删除翻译记录
     */
    void deleteTranslation(Long id);
    
    /**
     * 获取所有翻译记录
     */
    List<TranslationRecord> findAll();
    
    /**
     * 分页获取所有翻译记录
     */
    Page<TranslationRecord> findAll(Pageable pageable);
} 