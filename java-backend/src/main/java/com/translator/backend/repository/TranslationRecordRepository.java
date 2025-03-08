package com.translator.backend.repository;

import com.translator.backend.model.TranslationRecord;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 翻译记录数据访问接口
 */
@Repository
public interface TranslationRecordRepository extends JpaRepository<TranslationRecord, Long> {

    /**
     * 根据用户ID查询翻译记录
     */
    List<TranslationRecord> findByUserIdOrderByCreatedAtDesc(String userId);
    
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
    @Query("SELECT t FROM TranslationRecord t WHERE " +
           "(:text IS NULL OR t.originalText LIKE %:text% OR t.translatedText LIKE %:text%) AND " +
           "(:userId IS NULL OR t.userId = :userId)")
    Page<TranslationRecord> searchTranslations(
            @Param("text") String text,
            @Param("userId") String userId,
            Pageable pageable);
} 