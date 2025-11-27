-- =====================================================
-- GLPI ASSISTANT - COMPLETE DATABASE SCHEMA
-- Optimized architecture for all features
-- =====================================================

-- Drop existing database and create fresh
DROP DATABASE IF EXISTS glpi_sso;
CREATE DATABASE glpi_sso CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE glpi_sso;

-- =====================================================
-- 1. AUTHENTICATION & USERS
-- =====================================================

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB;

CREATE TABLE sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token_jti VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    is_revoked BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_token_jti (token_jti),
    INDEX idx_user_id (user_id),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB;

CREATE TABLE refresh_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_revoked BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_token_hash (token_hash)
) ENGINE=InnoDB;

-- =====================================================
-- 2. CONVERSATIONS & MESSAGES
-- =====================================================

CREATE TABLE conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL DEFAULT 'New Conversation',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_archived BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_is_archived (is_archived)
) ENGINE=InnoDB;

CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT NOT NULL,
    role ENUM('user', 'assistant', 'system') NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tokens_used INT DEFAULT 0,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    INDEX idx_conversation_id (conversation_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB;

-- =====================================================
-- 3. USER SETTINGS & PREFERENCES
-- =====================================================

CREATE TABLE user_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    theme VARCHAR(20) DEFAULT 'light',
    language VARCHAR(10) DEFAULT 'es',
    notifications_enabled BOOLEAN DEFAULT TRUE,
    email_notifications BOOLEAN DEFAULT TRUE,
    default_view VARCHAR(50) DEFAULT 'new_conversation',
    items_per_page INT DEFAULT 20,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB;

-- =====================================================
-- 4. AUDIT LOG (for tracking user actions)
-- =====================================================

CREATE TABLE audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INT,
    details TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB;

-- =====================================================
-- 5. USER FAVORITES (for quick access)
-- =====================================================

CREATE TABLE favorites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(100) NOT NULL,
    label VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_favorite (user_id, entity_type, entity_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB;

-- =====================================================
-- 6. STATISTICS CACHE (for dashboard performance)
-- =====================================================

CREATE TABLE statistics_cache (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    stat_key VARCHAR(100) NOT NULL,
    stat_value JSON NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_stat (user_id, stat_key),
    INDEX idx_user_id (user_id),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB;

-- =====================================================
-- INITIAL DATA
-- =====================================================

-- Create admin user (password: Admin123!)
INSERT INTO users (username, email, password_hash, full_name, is_admin, is_active)
VALUES (
    'admin',
    'admin@glpi.local',
    '$2b$12$PLACEHOLDER_HASH',
    'System Administrator',
    TRUE,
    TRUE
);

-- Create default settings for admin
INSERT INTO user_settings (user_id, theme, language, default_view)
VALUES (1, 'light', 'es', 'new_conversation');

-- =====================================================
-- USEFUL VIEWS
-- =====================================================

-- View: User with settings
CREATE VIEW v_users_full AS
SELECT 
    u.id,
    u.username,
    u.email,
    u.full_name,
    u.is_active,
    u.is_admin,
    u.created_at,
    u.last_login,
    s.theme,
    s.language,
    s.notifications_enabled,
    s.default_view
FROM users u
LEFT JOIN user_settings s ON u.id = s.user_id;

-- View: Conversation with message count
CREATE VIEW v_conversations_summary AS
SELECT 
    c.id,
    c.user_id,
    c.title,
    c.created_at,
    c.updated_at,
    c.is_archived,
    COUNT(m.id) as message_count,
    MAX(m.created_at) as last_message_at
FROM conversations c
LEFT JOIN messages m ON c.id = m.conversation_id
GROUP BY c.id;

-- View: User statistics
CREATE VIEW v_user_statistics AS
SELECT 
    u.id as user_id,
    u.username,
    COUNT(DISTINCT c.id) as total_conversations,
    COUNT(m.id) as total_messages,
    SUM(CASE WHEN m.role = 'user' THEN 1 ELSE 0 END) as user_messages,
    SUM(CASE WHEN m.role = 'assistant' THEN 1 ELSE 0 END) as assistant_messages,
    SUM(m.tokens_used) as total_tokens_used
FROM users u
LEFT JOIN conversations c ON u.id = c.user_id
LEFT JOIN messages m ON c.id = m.conversation_id
GROUP BY u.id;

-- =====================================================
-- STORED PROCEDURES
-- =====================================================

DELIMITER //

-- Procedure: Create new conversation
CREATE PROCEDURE sp_create_conversation(
    IN p_user_id INT,
    IN p_title VARCHAR(255)
)
BEGIN
    INSERT INTO conversations (user_id, title)
    VALUES (p_user_id, p_title);
    
    INSERT INTO audit_log (user_id, action, entity_type, entity_id)
    VALUES (p_user_id, 'create_conversation', 'conversation', LAST_INSERT_ID());
    
    SELECT LAST_INSERT_ID() as conversation_id;
END //

-- Procedure: Archive old conversations
CREATE PROCEDURE sp_archive_old_conversations(
    IN p_days_old INT
)
BEGIN
    UPDATE conversations
    SET is_archived = TRUE
    WHERE updated_at < DATE_SUB(NOW(), INTERVAL p_days_old DAY)
    AND is_archived = FALSE;
    
    SELECT ROW_COUNT() as archived_count;
END //

-- Procedure: Clean expired sessions
CREATE PROCEDURE sp_cleanup_expired_sessions()
BEGIN
    DELETE FROM sessions WHERE expires_at < NOW();
    DELETE FROM refresh_tokens WHERE expires_at < NOW();
    DELETE FROM statistics_cache WHERE expires_at < NOW();
END //

-- Procedure: Get user dashboard stats
CREATE PROCEDURE sp_get_user_dashboard(
    IN p_user_id INT
)
BEGIN
    SELECT 
        (SELECT COUNT(*) FROM conversations WHERE user_id = p_user_id) as total_conversations,
        (SELECT COUNT(*) FROM conversations WHERE user_id = p_user_id AND DATE(created_at) = CURDATE()) as today_conversations,
        (SELECT COUNT(*) FROM messages WHERE conversation_id IN (SELECT id FROM conversations WHERE user_id = p_user_id)) as total_messages,
        (SELECT SUM(tokens_used) FROM messages WHERE conversation_id IN (SELECT id FROM conversations WHERE user_id = p_user_id)) as total_tokens;
END //

DELIMITER ;

-- =====================================================
-- EVENTS (Automatic maintenance)
-- =====================================================

SET GLOBAL event_scheduler = ON;

-- Clean expired sessions daily
CREATE EVENT IF NOT EXISTS evt_cleanup_sessions
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_TIMESTAMP
DO CALL sp_cleanup_expired_sessions();

-- Auto-archive old conversations monthly
CREATE EVENT IF NOT EXISTS evt_archive_old_conversations
ON SCHEDULE EVERY 1 MONTH
STARTS CURRENT_TIMESTAMP
DO CALL sp_archive_old_conversations(90);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Additional composite indexes for common queries
CREATE INDEX idx_conversations_user_updated ON conversations(user_id, updated_at DESC);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at);
CREATE INDEX idx_audit_user_created ON audit_log(user_id, created_at DESC);

-- =====================================================
-- GRANTS (to be set after user creation)
-- =====================================================

-- Note: Execute this after creating sso_user:
-- GRANT ALL PRIVILEGES ON glpi_sso.* TO 'sso_user'@'%';
-- FLUSH PRIVILEGES;
