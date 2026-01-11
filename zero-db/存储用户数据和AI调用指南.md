# ZeroDB 存储用户数据和AI调用指南

## 📊 数据结构设计

### 1. 用户数据表

```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    status INTEGER DEFAULT 1
);
```

### 2. AI调用记录表

```sql
CREATE TABLE ai_calls (
    call_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    model VARCHAR(50) NOT NULL,
    tokens_used INTEGER,
    cost REAL,
    duration_ms INTEGER,
    status INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### 3. AI调用参数表

```sql
CREATE TABLE ai_call_params (
    param_id INTEGER PRIMARY KEY AUTOINCREMENT,
    call_id INTEGER,
    param_name VARCHAR(50) NOT NULL,
    param_value TEXT,
    FOREIGN KEY (call_id) REFERENCES ai_calls(call_id)
);
```

## 💾 数据存储示例

### 1. 插入用户数据

```sql
-- 插入新用户
INSERT INTO users (username, email, password_hash) 
VALUES ('user1', 'user1@example.com', 'hashed_password');

-- 记录用户登录
UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = 1;
```

### 2. 插入AI调用记录

```sql
-- 插入AI调用记录
INSERT INTO ai_calls (user_id, prompt, response, model, tokens_used, cost, duration_ms)
VALUES (
    1,
    '请解释什么是ZeroDB',
    'ZeroDB是一个零占用的本地数据库...',
    'gpt-3.5-turbo',
    150,
    0.003,
    1200
);

-- 获取刚插入的call_id
SELECT last_insert_rowid() AS call_id;

-- 插入调用参数
INSERT INTO ai_call_params (call_id, param_name, param_value)
VALUES (1, 'temperature', '0.7'),
       (1, 'max_tokens', '500'),
       (1, 'top_p', '0.9');
```

## 🔍 数据查询示例

### 1. 查询用户信息

```sql
-- 查询单个用户
SELECT * FROM users WHERE user_id = 1;

-- 查询所有活跃用户
SELECT user_id, username, email, created_at FROM users WHERE status = 1;

-- 按创建时间排序
SELECT * FROM users ORDER BY created_at DESC;
```

### 2. 查询AI调用记录

```sql
-- 查询用户的所有AI调用
SELECT * FROM ai_calls WHERE user_id = 1 ORDER BY created_at DESC;

-- 查询最近10条调用记录
SELECT * FROM ai_calls ORDER BY created_at DESC LIMIT 10;

-- 统计用户调用次数
SELECT COUNT(*) AS call_count FROM ai_calls WHERE user_id = 1;

-- 计算总花费
SELECT SUM(cost) AS total_cost FROM ai_calls WHERE user_id = 1;

-- 按模型分组统计
SELECT model, COUNT(*) AS call_count, SUM(cost) AS total_cost 
FROM ai_calls 
GROUP BY model;
```

### 3. 关联查询

```sql
-- 查询用户及其最近的AI调用
SELECT u.username, a.prompt, a.response, a.created_at
FROM users u
JOIN ai_calls a ON u.user_id = a.user_id
WHERE u.user_id = 1
ORDER BY a.created_at DESC
LIMIT 5;

-- 查询调用记录及其参数
SELECT a.call_id, a.prompt, a.response, p.param_name, p.param_value
FROM ai_calls a
JOIN ai_call_params p ON a.call_id = p.call_id
WHERE a.call_id = 1;
```

## 🐍 Python应用集成

### 1. 安装依赖

```bash
pip install mysql-connector-python
```

### 2. 连接数据库

```python
import mysql.connector

# 连接ZeroDB
cnx = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",  # 任意用户名
    password="",   # 任意密码
    database="test"  # 任意数据库名
)

cursor = cnx.cursor()
```

### 3. 存储用户数据

```python
def create_user(username, email, password_hash):
    """创建新用户"""
    query = """
    INSERT INTO users (username, email, password_hash)
    VALUES (%s, %s, %s)
    """
    cursor.execute(query, (username, email, password_hash))
    cnx.commit()
    return cursor.lastrowid

# 使用示例
user_id = create_user("user2", "user2@example.com", "hashed_password2")
print(f"创建用户成功，ID: {user_id}")
```

### 4. 存储AI调用记录

```python
def log_ai_call(user_id, prompt, response, model, tokens_used, cost, duration_ms, params=None):
    """记录AI调用"""
    # 开始事务
    cnx.start_transaction()
    
    try:
        # 插入调用记录
        call_query = """
        INSERT INTO ai_calls (user_id, prompt, response, model, tokens_used, cost, duration_ms)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(call_query, (user_id, prompt, response, model, tokens_used, cost, duration_ms))
        call_id = cursor.lastrowid
        
        # 插入调用参数
        if params:
            param_query = """
            INSERT INTO ai_call_params (call_id, param_name, param_value)
            VALUES (%s, %s, %s)
            """
            param_values = [(call_id, k, str(v)) for k, v in params.items()]
            cursor.executemany(param_query, param_values)
        
        # 提交事务
        cnx.commit()
        return call_id
    except Exception as e:
        # 回滚事务
        cnx.rollback()
        raise e

# 使用示例
aicall_params = {
    "temperature": 0.7,
    "max_tokens": 500,
    "top_p": 0.9
}

call_id = log_ai_call(
    user_id=1,
    prompt="请解释什么是ZeroDB",
    response="ZeroDB是一个零占用的本地数据库...",
    model="gpt-3.5-turbo",
    tokens_used=150,
    cost=0.003,
    duration_ms=1200,
    params=aicall_params
)
print(f"AI调用记录成功，ID: {call_id}")
```

### 5. 查询数据

```python
def get_user_ai_calls(user_id, limit=10):
    """获取用户的AI调用记录"""
    query = """
    SELECT a.call_id, a.prompt, a.response, a.model, a.created_at
    FROM ai_calls a
    WHERE a.user_id = %s
    ORDER BY a.created_at DESC
    LIMIT %s
    """
    cursor.execute(query, (user_id, limit))
    return cursor.fetchall()

# 使用示例
calls = get_user_ai_calls(user_id=1, limit=5)
for call in calls:
    print(f"调用ID: {call[0]}, 模型: {call[3]}, 时间: {call[4]}")
    print(f"提示: {call[1][:50]}...")
    print(f"响应: {call[2][:50]}...")
    print("-" * 50)
```

### 6. 关闭连接

```python
cursor.close()
cnx.close()
```

## ⚡ 性能优化

### 1. 创建索引

```sql
-- 为频繁查询的字段创建索引
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_ai_calls_user_id ON ai_calls(user_id);
CREATE INDEX idx_ai_calls_created_at ON ai_calls(created_at);
CREATE INDEX idx_ai_call_params_call_id ON ai_call_params(call_id);
```

### 2. 批量操作

```python
# 批量插入AI调用记录
def batch_log_ai_calls(calls):
    """批量记录AI调用"""
    call_query = """
    INSERT INTO ai_calls (user_id, prompt, response, model, tokens_used, cost, duration_ms)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    # 提取调用记录值
    call_values = [(call['user_id'], call['prompt'], call['response'], 
                   call['model'], call['tokens_used'], call['cost'], call['duration_ms'])
                   for call in calls]
    
    # 批量执行
    cursor.executemany(call_query, call_values)
    cnx.commit()
```

### 3. 数据归档

```sql