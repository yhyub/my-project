# ZeroDB - 零占用本地数据库

## 项目概述

ZeroDB是一个极致轻量级的本地数据库服务，旨在提供几乎零资源占用的数据库解决方案。它结合了SQLite的轻量级特性和MySQL的兼容性，同时实现了智能的资源管理，确保在空闲时几乎不占用系统资源。

### 核心特性

- **零占用设计**：空闲时内存占用低于10MB，CPU使用率接近0%
- **MySQL兼容**：支持MySQL客户端连接，无需修改现有代码
- **动态资源管理**：根据使用情况自动调整资源分配
- **按需加载**：仅在有请求时才分配资源
- **内存存储**：默认使用内存存储，不占用磁盘空间
- **轻量级架构**：整个项目代码量不到2000行

## 快速开始

### 环境要求

- Python 3.6+ 
- psutil库（用于资源监控）

### 启动服务

#### Windows

1. 双击 `start.bat` 脚本
2. 脚本会自动检查并安装依赖
3. 等待服务器启动完成

#### 命令行

```bash
# 安装依赖
pip install psutil

# 启动服务器
python server.py
```

### 连接数据库

使用任何MySQL客户端连接到 `127.0.0.1:3306`，用户名和密码可以是任意值（ZeroDB默认接受所有认证）。

示例：
```bash
mysql -h 127.0.0.1 -P 3306 -u root -p
```

## 配置说明

ZeroDB使用JSON配置文件 `config.json` 进行配置，主要配置项如下：

### 服务器配置

```json
"server": {
    "port": 3306,          // 监听端口
    "host": "127.0.0.1",   // 监听地址
    "max_connections": 10,  // 最大连接数
    "idle_timeout": 300,    // 连接空闲超时时间（秒）
    "thread_pool_size": 1   // 线程池大小
}
```

### 存储配置

```json
"storage": {
    "engine": "sqlite",     // 存储引擎
    "path": ":memory:",    // 存储路径（:memory:表示内存存储）
    "sync_interval": 3600,   // 同步间隔（秒）
    "cache_size": 100,       // 缓存大小
    "journal_mode": "WAL",  // 日志模式
    "synchronous": "OFF"    // 同步模式
}
```

### 资源配置

```json
"resource": {
    "max_memory_mb": 10,         // 最大内存占用（MB）
    "max_cpu_percent": 5,        // 最大CPU使用率（%）
    "dynamic_allocation": true,  // 是否启用动态资源分配
    "idle_resource_release": true, // 是否在空闲时释放资源
    "release_delay_seconds": 30  // 空闲后释放资源的延迟时间（秒）
}
```

### 图形化配置

运行 `configure.py` 可以打开图形化配置工具，方便调整各项参数：

```bash
python configure.py
```

## 资源优化策略

### 1. 使用内存存储

将 `storage.path` 设置为 `:memory:`，这样数据将完全存储在内存中，不占用磁盘空间。

### 2. 降低缓存大小

减少 `storage.cache_size` 的值，可以进一步降低内存占用。

### 3. 关闭同步模式

将 `storage.synchronous` 设置为 `OFF`，可以减少磁盘I/O操作，降低CPU和磁盘占用。

### 4. 启用空闲资源释放

确保 `resource.idle_resource_release` 设置为 `true`，这样在空闲时会自动释放资源。

### 5. 降低最大连接数

减少 `server.max_connections` 的值，可以减少内存占用。

### 6. 缩短空闲超时时间

减少 `server.idle_timeout` 的值，可以更快地释放空闲连接。

## 使用示例

### 创建表

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50),
    email VARCHAR(100)
);
```

### 插入数据

```sql
INSERT INTO users (name, email) VALUES ('张三', 'zhangsan@example.com');
INSERT INTO users (name, email) VALUES ('李四', 'lisi@example.com');
```

### 查询数据

```sql
SELECT * FROM users;
```

### 更新数据

```sql
UPDATE users SET email = 'new_email@example.com' WHERE id = 1;
```

### 删除数据

```sql
DELETE FROM users WHERE id = 2;
```

## 项目结构

```
zero-db/
├── config.json          # 配置文件
├── server.py            # 主服务文件
├── sqlite_engine.py     # SQLite存储引擎
├── mysql_protocol.py    # MySQL协议处理
├── resource_manager.py  # 资源管理器
├── start.bat            # Windows启动脚本
├── configure.py         # 图形化配置工具
└── README.md            # 文档
```

## 技术原理

### 1. 轻量级存储引擎

ZeroDB使用SQLite作为底层存储引擎，SQLite是一个嵌入式数据库，不需要独立的服务器进程，资源占用非常低。

### 2. MySQL协议兼容

ZeroDB实现了基本的MySQL协议，可以接受MySQL客户端的连接和查询，将MySQL查询转换为SQLite查询执行。

### 3. 动态资源管理

ZeroDB内置了资源管理器，会定期检查系统资源使用情况：

- 当内存占用超过限制时，会自动触发垃圾回收
- 当CPU使用率超过限制时，会自动调整处理速度
- 当空闲时间超过阈值时，会释放所有不必要的资源

### 4. 按需加载

ZeroDB的各个组件都是按需加载的，只有在需要时才会初始化和分配资源。

## 性能特点

- **启动时间**：< 1秒
- **内存占用**：空闲时 < 10MB
- **CPU使用率**：空闲时 < 0.1%
- **连接延迟**：< 1ms
- **查询性能**：取决于SQLite的性能，适合小型数据集

## 适用场景

- **开发测试**：快速搭建本地数据库环境
- **嵌入式系统**：资源受限的设备
- **轻量级应用**：不需要大型数据库的小型应用
- **临时数据存储**：临时需要数据库功能的场景
- **教育学习**：学习数据库原理和SQL

## 限制

- 只支持基本的SQL语法
- 不支持存储过程、触发器等高级功能
- 不适合大型数据集（建议数据量 < 1GB）
- 并发性能有限，适合低并发场景

## 故障排除

### 无法启动服务器

- 检查Python是否正确安装
- 检查端口是否被占用（默认3306）
- 检查依赖是否正确安装

### 无法连接数据库

- 检查服务器是否正在运行
- 检查防火墙设置
- 检查连接参数是否正确

### 性能问题

- 减少并发连接数
- 优化SQL查询
- 增加缓存大小

## 未来规划

- 支持更多的SQL语法
- 支持数据持久化
- 支持复制和备份
- 支持更多的存储引擎
- 进一步降低资源占用

## 许可证

ZeroDB采用MIT许可证，您可以自由使用、修改和分发。

## 贡献

欢迎提交Issue和Pull Request，一起改进ZeroDB！

## 联系方式

如有问题或建议，请通过以下方式联系：

- GitHub: https://github.com/zerodb/zerodb
- Email: contact@zerodb.org

---

ZeroDB - 让数据库回归本质，几乎零占用的本地数据库解决方案！
