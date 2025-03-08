package com.translator.backend.controller;

import com.translator.backend.model.TranslationRecord;
import com.translator.backend.service.TranslationService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletRequest;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 翻译记录API控制器
 */
@RestController
@RequestMapping("/translations")
@CrossOrigin(origins = "*")
@RequiredArgsConstructor
public class TranslationController {

    private final TranslationService translationService;

    /**
     * 保存翻译记录
     */
    @PostMapping
    public ResponseEntity<TranslationRecord> saveTranslation(
            @RequestBody TranslationRecord translationRecord,
            HttpServletRequest request) {
        
        // 设置客户端IP地址
        translationRecord.setIpAddress(request.getRemoteAddr());
        
        TranslationRecord savedRecord = translationService.saveTranslation(translationRecord);
        return new ResponseEntity<>(savedRecord, HttpStatus.CREATED);
    }

    /**
     * 根据ID获取翻译记录
     */
    @GetMapping("/{id}")
    public ResponseEntity<TranslationRecord> getTranslationById(@PathVariable Long id) {
        return translationService.findById(id)
                .map(record -> new ResponseEntity<>(record, HttpStatus.OK))
                .orElse(new ResponseEntity<>(HttpStatus.NOT_FOUND));
    }

    /**
     * 获取用户的翻译记录
     */
    @GetMapping("/user/{userId}")
    public ResponseEntity<List<TranslationRecord>> getTranslationsByUserId(@PathVariable String userId) {
        List<TranslationRecord> records = translationService.findByUserId(userId);
        return new ResponseEntity<>(records, HttpStatus.OK);
    }

    /**
     * 分页获取用户的翻译记录
     */
    @GetMapping("/user/{userId}/page")
    public ResponseEntity<Page<TranslationRecord>> getTranslationsByUserIdPaged(
            @PathVariable String userId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(defaultValue = "createdAt") String sortBy,
            @RequestParam(defaultValue = "desc") String sortDir) {
        
        Sort sort = Sort.by(Sort.Direction.fromString(sortDir), sortBy);
        Pageable pageable = PageRequest.of(page, size, sort);
        
        Page<TranslationRecord> records = translationService.findByUserId(userId, pageable);
        return new ResponseEntity<>(records, HttpStatus.OK);
    }

    /**
     * 搜索翻译记录
     */
    @GetMapping("/search")
    public ResponseEntity<Page<TranslationRecord>> searchTranslations(
            @RequestParam(required = false) String text,
            @RequestParam(required = false) String userId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(defaultValue = "createdAt") String sortBy,
            @RequestParam(defaultValue = "desc") String sortDir) {
        
        Sort sort = Sort.by(Sort.Direction.fromString(sortDir), sortBy);
        Pageable pageable = PageRequest.of(page, size, sort);
        
        Page<TranslationRecord> records = translationService.searchTranslations(text, userId, pageable);
        return new ResponseEntity<>(records, HttpStatus.OK);
    }

    /**
     * 删除翻译记录
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Boolean>> deleteTranslation(@PathVariable Long id) {
        translationService.deleteTranslation(id);
        
        Map<String, Boolean> response = new HashMap<>();
        response.put("deleted", Boolean.TRUE);
        
        return new ResponseEntity<>(response, HttpStatus.OK);
    }

    /**
     * 获取翻译统计信息
     */
    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getTranslationStats() {
        long totalCount = translationService.findAll().size();
        
        Map<String, Object> stats = new HashMap<>();
        stats.put("totalTranslations", totalCount);
        
        // 今天的记录
        LocalDateTime startOfDay = LocalDateTime.now().withHour(0).withMinute(0).withSecond(0);
        List<TranslationRecord> todayRecords = translationService.findByCreatedAtBetween(
                startOfDay, LocalDateTime.now());
        stats.put("todayTranslations", todayRecords.size());
        
        return new ResponseEntity<>(stats, HttpStatus.OK);
    }
} 