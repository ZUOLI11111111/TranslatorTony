package com.translator.backend.service.impl;

import com.translator.backend.model.TranslationRecord;
import com.translator.backend.repository.TranslationRecordRepository;
import com.translator.backend.service.TranslationService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * 翻译服务实现类
 */
@Service
@RequiredArgsConstructor
public class TranslationServiceImpl implements TranslationService {

    private final TranslationRecordRepository translationRecordRepository;

    @Override
    public TranslationRecord saveTranslation(TranslationRecord translationRecord) {
        return translationRecordRepository.save(translationRecord);
    }

    @Override
    public Optional<TranslationRecord> findById(Long id) {
        return translationRecordRepository.findById(id);
    }

    @Override
    public List<TranslationRecord> findByUserId(String userId) {
        return translationRecordRepository.findByUserIdOrderByCreatedAtDesc(userId);
    }

    @Override
    public Page<TranslationRecord> findByUserId(String userId, Pageable pageable) {
        return translationRecordRepository.findByUserId(userId, pageable);
    }

    @Override
    public List<TranslationRecord> findBySourceLangAndTargetLang(String sourceLang, String targetLang) {
        return translationRecordRepository.findBySourceLangAndTargetLang(sourceLang, targetLang);
    }

    @Override
    public List<TranslationRecord> findByCreatedAtBetween(LocalDateTime start, LocalDateTime end) {
        return translationRecordRepository.findByCreatedAtBetween(start, end);
    }

    @Override
    public Page<TranslationRecord> searchTranslations(String text, String userId, Pageable pageable) {
        return translationRecordRepository.searchTranslations(text, userId, pageable);
    }

    @Override
    public void deleteTranslation(Long id) {
        translationRecordRepository.deleteById(id);
    }

    @Override
    public List<TranslationRecord> findAll() {
        return translationRecordRepository.findAll();
    }

    @Override
    public Page<TranslationRecord> findAll(Pageable pageable) {
        return translationRecordRepository.findAll(pageable);
    }
} 