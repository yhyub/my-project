# ZeroDB 与 Trae CN 集成方案

## 🎯 核心需求

1. **零存储空间占用**：使用内存存储，不占用电脑磁盘空间
2. **Trae CN 调用支持**：提供完整的数据库服务，可被 Trae CN 软件调用
3. **完整的文件存储**：支持个人文件的完整信息存储
4. **数据完整性**：确保数据库信息完整正确

## 📋 集成方案

### 1. 配置 ZeroDB 为内存存储模式

**config.json**
```json
{
  "server": {
    "port": 3306,
    "host": "0.0.0.0",
    "max_connections": 20,
    "idle_timeout": 600,
    "thread_pool_size": 2
  },
  "storage": {
    "engine": "sqlite",
    "path": ":memory:",
    "sync_interval": 3600,
    "cache_size": 500,
    "journal_mode": "MEMORY",
    "synchronous": "OFF"
  },
  "mysql": {
    "version": "8.0.32",
    "charset": "utf8mb4",
    "collation": "utf8mb4_unicode_ci",
    "skip_networking": false
  },
  "resource": {
    "max_memory_mb": 20,
    "max_cpu_percent": 10,
    "dynamic_allocation": true,
    "idle_resource_release": true,
    "release_delay_seconds": 60
  },
  "logging": {
    "level": "info",
    "file": null,
    "console": true
  }
}
```

### 2. 创建完整的文件存储表结构

```sql
-- 用户表
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 文件表（内存存储）
CREATE TABLE IF NOT EXISTS personal_files (
    file_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(100) NOT NULL,
    file_size INTEGER NOT NULL,
    file_content BLOB NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tags TEXT,
    description TEXT,
    is_favorite BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 文件版本表
CREATE TABLE IF NOT EXISTS file_versions (
    version_id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    version_number INTEGER NOT NULL,
    file_content BLOB NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER NOT NULL,
    change_log TEXT,
    FOREIGN KEY (file_id) REFERENCES personal_files(file_id),
    FOREIGN KEY (updated_by) REFERENCES users(user_id)
);

-- 文件标签表
CREATE TABLE IF NOT EXISTS file_tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_name VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 文件标签关联表
CREATE TABLE IF NOT EXISTS file_tag_relations (
    relation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    FOREIGN KEY (file_id) REFERENCES personal_files(file_id),
    FOREIGN KEY (tag_id) REFERENCES file_tags(tag_id),
    UNIQUE(file_id, tag_id)
);

-- 文件访问记录表
CREATE TABLE IF NOT EXISTS file_access_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    access_type VARCHAR(20) NOT NULL,
    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES personal_files(file_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 索引优化
CREATE INDEX IF NOT EXISTS idx_personal_files_user_id ON personal_files(user_id);
CREATE INDEX IF NOT EXISTS idx_personal_files_filename ON personal_files(filename);
CREATE INDEX IF NOT EXISTS idx_file_versions_file_id ON file_versions(file_id);
CREATE INDEX IF NOT EXISTS idx_file_tag_relations_file_id ON file_tag_relations(file_id);
CREATE INDEX IF NOT EXISTS idx_file_access_logs_file_id ON file_access_logs(file_id);
```

### 3. Trae CN 连接配置

在 Trae CN 中配置 MySQL 连接：

| 配置项 | 值 |
|--------|-----|
| 主机 | 127.0.0.1 |
| 端口 | 3306 |
| 用户名 | 任意（如：trae_user） |
| 密码 | 任意（如：trae_pass） |
| 数据库名 | 任意（如：trae_db） |
| 字符集 | utf8mb4 |
| 连接方式 | TCP/IP |

### 4. Trae CN 调用示例

```python
# Trae CN 中调用 ZeroDB 的示例代码
import mysql.connector

# 连接 ZeroDB
db_config = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "trae_user",
    "password": "trae_pass",
    "database": "trae_db"
}

cnx = mysql.connector.connect(**db_config)
cursor = cnx.cursor()

# 示例1：存储个人文件
def store_personal_file(user_id, filename, file_content, file_type="text/plain", description=""):
    """存储个人文件到 ZeroDB"""
    import hashlib
    
    # 计算文件哈希
    file_hash = hashlib.sha256(file_content).hexdigest()
    file_size = len(file_content)
    
    # 插入文件记录
    query = """
    INSERT INTO personal_files (
        user_id, filename, file_type, file_size, file_content, file_hash, description
    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    cursor.execute(query, (
        user_id, filename, file_type, file_size, file_content, file_hash, description
    ))
    cnx.commit()
    
    return cursor.lastrowid

# 示例2：查询个人文件
def get_personal_files(user_id, limit=20):
    """获取用户的个人文件列表"""
    query = """
    SELECT file_id, filename, file_type, file_size, created_at, description, is_favorite
    FROM personal_files
    WHERE user_id = %s
    ORDER BY created_at DESC
    LIMIT %s
    """
    
    cursor.execute(query, (user_id, limit))
    return cursor.fetchall()

# 示例3：获取文件内容
def get_file_content(file_id):
    """获取文件内容"""
    query = """
    SELECT filename, file_content, file_type
    FROM personal_files
    WHERE file_id = %s
    """
    
    cursor.execute(query, (file_id,))
    return cursor.fetchone()

# 使用示例
if __name__ == "__main__":
    # 存储测试文件
    test_content = b"这是一个测试文件，用于Trae CN调用ZeroDB"
    file_id = store_personal_file(1, "test.txt", test_content, "text/plain", "测试文件")
    print(f"文件存储成功，ID: {file_id}")
    
    # 查询文件列表
    files = get_personal_files(1)
    for file in files:
        print(f"ID: {file[0]}, 名称: {file[1]}, 大小: {file[3]} bytes")
    
    # 获取文件内容
    file_info = get_file_content(file_id)
    if file_info:
        filename, content, file_type = file_info
        print(f"获取文件: {filename}, 类型: {file_type}")
        print(f"内容: {content.decode('utf-8')}")

# 关闭连接
cursor.close()
cnx.close()
```

## 🔧 数据完整性保障

### 1. 事务管理

```sql
-- 使用事务确保数据完整性
BEGIN TRANSACTION;

-- 插入用户
INSERT INTO users (username, email) VALUES ('test_user', 'test@example.com');
SET @user_id = last_insert_rowid();

-- 插入文件
INSERT INTO personal_files (user_id, filename, file_type, file_size, file_content, file_hash)
VALUES (@user_id, 'test.txt', 'text/plain', 100, X'5465737420636f6e74656e74', 'hash_value');
SET @file_id = last_insert_rowid();

-- 插入标签
INSERT INTO file_tags (tag_name) VALUES ('personal');
SET @tag_id = last_insert_rowid();

-- 关联标签
INSERT INTO file_tag_relations (file_id, tag_id) VALUES (@file_id, @tag_id);

COMMIT;
```

### 2. 数据验证

```sql
-- 验证文件哈希完整性
DELIMITER //
CREATE TRIGGER validate_file_hash BEFORE INSERT ON personal_files
FOR EACH ROW
BEGIN
    DECLARE computed_hash VARCHAR(64);
    SET computed_hash = HEX(SHA256(NEW.file_content));
    IF computed_hash != NEW.file_hash THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'File hash validation failed';
    END IF;
END;//
DELIMITER ;
```

### 3. 自动维护

```sql
-- 自动更新时间戳
DELIMITER //
CREATE TRIGGER update_file_timestamp BEFORE UPDATE ON personal_files
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END;//
DELIMITER ;
```

## 🚀 快速启动

### 1. 启动 ZeroDB

```bash
# 进入 zero-db 目录
cd c:\Users\Administrator\Desktop\项目\zero-db

# 启动服务
python server.py
```

### 2. 初始化数据库结构

```bash
# 创建初始化脚本
cat > init_db.sql << 'EOF'
-- 创建所有表结构
CREATE TABLE IF NOT EXISTS users (...);
CREATE TABLE IF NOT EXISTS personal_files (...);
-- 其他表创建语句...
EOF

# 执行初始化
mysql -h 127.0.0.1 -P 3306 -u root -p < init_db.sql
```

### 3. Trae CN 连接测试

在 Trae CN 中使用上述配置连接 ZeroDB，执行简单查询测试：

```sql
-- 测试连接
SELECT 'ZeroDB 连接成功' AS message;

-- 创建测试用户
INSERT INTO users (username, email) VALUES ('trae_user', 'trae@example.com');

-- 验证插入
SELECT * FROM users;
```

## 💡 最佳实践

### 1. 定期备份内存数据

虽然使用内存存储，但可以定期将数据导出到文件，以便在需要时恢复：

```python
def backup_database(output_file):
    """备份数据库到文件"""
    import sqlite3
    import shutil
    
    # 连接内存数据库
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # 从ZeroDB同步数据
    # ... 同步逻辑 ...
    
    # 备份到文件
    backup_conn = sqlite3.connect(output_file)
    conn.backup(backup_conn)
    backup_conn.close()
    conn.close()
```

### 2. 优化查询性能

- 为频繁查询的字段创建索引
- 使用分页查询减少内存占用
- 定期清理过期数据

### 3. 安全配置

- 限制访问IP范围
- 使用强密码认证
- 定期审计访问日志
- 加密敏感数据

## 📊 数据结构说明

### 个人文件表（personal_files）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| file_id | INTEGER | 文件唯一ID |
| user_id | INTEGER | 用户ID |
| filename | VARCHAR(255) | 文件名 |
| file_type | VARCHAR(100) | 文件类型（MIME） |
| file_size | INTEGER | 文件大小（字节） |
| file_content | BLOB | 文件内容 |
| file_hash | VARCHAR(64) | 文件哈希值 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |
| tags | TEXT | 标签（JSON格式） |
| description | TEXT | 文件描述 |
| is_favorite | BOOLEAN | 是否收藏 |

### 文件版本表（file_versions）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| version_id | INTEGER | 版本ID |
| file_id | INTEGER | 关联文件ID |
| version_number | INTEGER | 版本号 |
| file_content | BLOB | 版本文件内容 |
| file_hash | VARCHAR(64) | 版本文件哈希 |
| created_at | TIMESTAMP | 创建时间 |
| updated_by | INTEGER | 更新用户ID |
| change_log | TEXT | 变更日志 |

## 🎯 集成优势

1. **零存储占用**：完全使用内存，不占用磁盘空间
2. **高性能**：内存访问速度快，响应时间短
3. **易集成**：MySQL兼容，Trae CN可直接调用
4. **完整功能**：支持文件存储、版本控制、标签管理等
5. **数据安全**：事务支持，数据完整性保障
6. **轻量级**：资源占用低，不影响系统性能

## 📞 技术支持

- 配置问题：检查 `config.json` 配置
- 连接问题：检查网络和防火墙设置
- 性能问题：优化索引和查询语句
- 数据问题：使用事务和触发器保障完整性

---

ZeroDB 与 Trae CN 完美集成，为您提供零存储占用的个人文件数据库解决方案！
