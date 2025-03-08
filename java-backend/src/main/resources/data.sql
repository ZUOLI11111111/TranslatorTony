-- 使用数据库
USE translator_db;

-- 插入示例用户（密码为 'password' 的哈希值）
INSERT INTO users (username, password, email, full_name, role, active, api_key) 
VALUES ('admin', '$2a$10$EblZqNptyYvcLm/VwDCVAuBjzZOI7khzdyGPBr08PpIi0na624b8.', 'admin@example.com', '管理员', 'ADMIN', true, NULL)
ON DUPLICATE KEY UPDATE username=username;

INSERT INTO users (username, password, email, full_name, role, active, api_key) 
VALUES ('user', '$2a$10$EblZqNptyYvcLm/VwDCVAuBjzZOI7khzdyGPBr08PpIi0na624b8.', 'user@example.com', '普通用户', 'USER', true, NULL)
ON DUPLICATE KEY UPDATE username=username;

-- 插入示例翻译记录
INSERT INTO translation_records (original_text, translated_text, source_lang, target_lang, user_id, ip_address, model) 
VALUES ('Hello, World!', '你好，世界！', 'en', 'zh', 'user', '127.0.0.1', 'deepseek-chat')
ON DUPLICATE KEY UPDATE id=id;

INSERT INTO translation_records (original_text, translated_text, source_lang, target_lang, user_id, ip_address, model) 
VALUES ('人工智能', 'Artificial Intelligence', 'zh', 'en', 'user', '127.0.0.1', 'deepseek-chat')
ON DUPLICATE KEY UPDATE id=id; 