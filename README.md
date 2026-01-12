# 项目文件夹备份到PostgreSQL云端数据库

这个项目包含Python脚本，用于将C:\Users\Administrator\Desktop\项目文件夹的内容备份到PostgreSQL 17云端数据库。

## 目录结构

- `backup_to_postgres.py` - 主备份脚本，用于将项目文件夹内容上传到PostgreSQL数据库
- `test_postgres_connection.py` - 测试脚本，用于验证PostgreSQL数据库连接
- `postgres_config_example.json` - 示例配置文件，用于配置PostgreSQL数据库连接
- `README.md` - 本说明文件

## 安装依赖

```bash
pip install psycopg2-binary
```

## 配置PostgreSQL连接

### 方法1：使用配置文件

1. 复制示例配置文件并重命名：
   ```bash
   cp postgres_config_example.json postgres_config.json
   ```

2. 编辑配置文件，填入您的PostgreSQL连接信息：
   ```json
   {
     "host": "your-cloud-postgres-host.example.com",
     "port": 5432,
     "user": "your-username",
     "password": "your-secure-password",
     "database": "your-database-name"
   }
   ```

### 方法2：使用环境变量

设置以下环境变量：

```bash
export POSTGRES_HOST="your-cloud-postgres-host.example.com"
export POSTGRES_PORT=5432
export POSTGRES_USER="your-username"
export POSTGRES_PASSWORD="your-secure-password"
export POSTGRES_DATABASE="your-database-name"
```

### 方法3：使用命令行参数

在运行脚本时直接传递参数：

```bash
python backup_to_postgres.py --host your-cloud-postgres-host.example.com --port 5432 --user your-username --password your-secure-password --database your-database-name
```

## 使用方法

### 1. 测试数据库连接

```bash
python test_postgres_connection.py --config postgres_config.json
```

或使用环境变量：

```bash
python test_postgres_connection.py
```

或使用命令行参数：

```bash
python test_postgres_connection.py --host your-cloud-postgres-host.example.com --port 5432 --user your-username --password your-secure-password --database your-database-name
```

### 2. 备份项目文件夹

```bash
python backup_to_postgres.py --config postgres_config.json
```

或使用环境变量：

```bash
python backup_to_postgres.py
```

或使用命令行参数：

```bash
python backup_to_postgres.py --host your-cloud-postgres-host.example.com --port 5432 --user your-username --password your-secure-password --database your-database-name
```

## 安全删除C盘大文件

在备份完成后，可以安全删除以下C盘大文件以释放空间：

### 1. WSL相关文件（如果不使用WSL）
- C:\Program Files\WSL\system.vhd
- C:\Program Files\WSL\tools\modules.vhd

### 2. Docker相关文件（如果不使用Docker）
- docker-wsl-cli.iso
- docker-desktop.iso
- Docker Desktop安装程序

### 3. 其他大文件
- 大型文本文件（如merged_all_text.txt）
- 安装程序（如pgadmin4-9.11-x64.exe、Trae CN-Setup-x64.exe）
- 大型日志文件和合并文件

## 注意事项

1. 确保PostgreSQL数据库有足够的空间存储项目文件夹内容
2. 确保网络连接稳定，特别是在上传大量文件时
3. 备份过程可能需要较长时间，具体取决于项目文件夹大小和网络速度
4. 建议在备份前先运行测试脚本，确保数据库连接正常
5. 删除大文件前，请确保这些文件不再需要，或已做好备份

## 数据库表结构

### files表

| 字段名 | 数据类型 | 描述 |
|--------|----------|------|
| id | SERIAL | 主键ID |
| file_path | TEXT | 文件路径，唯一索引 |
| file_name | TEXT | 文件名 |
| file_size | BIGINT | 文件大小（字节） |
| file_type | TEXT | 文件类型（扩展名） |
| created_at | TIMESTAMP | 记录创建时间 |
| modified_at | TIMESTAMP | 文件修改时间 |
| file_hash | TEXT | 文件SHA256哈希值 |
| file_content | BYTEA | 文件内容（二进制） |

### folders表

| 字段名 | 数据类型 | 描述 |
|--------|----------|------|
| id | SERIAL | 主键ID |
| folder_path | TEXT | 文件夹路径，唯一索引 |
| folder_name | TEXT | 文件夹名 |
| created_at | TIMESTAMP | 记录创建时间 |
| modified_at | TIMESTAMP | 文件夹修改时间 |

## 技术细节

- 使用psycopg2-binary库连接PostgreSQL数据库
- 使用SHA256哈希值验证文件完整性
- 支持断点续传（如果文件路径相同但内容不同，会更新文件记录）
- 自动创建必要的数据库表
- 支持递归遍历文件夹结构

## 故障排除

### 连接失败

如果遇到连接失败，请检查：

1. PostgreSQL服务器是否正在运行
2. 连接信息是否正确
3. 网络连接是否正常
4. 防火墙是否允许访问PostgreSQL端口

### 备份失败

如果遇到备份失败，请检查：

1. PostgreSQL数据库是否有足够的空间
2. 数据库用户是否有创建表和插入数据的权限
3. 项目文件夹是否有读取权限
4. 网络连接是否稳定

## 版本要求

- Python 3.6+
- PostgreSQL 17+

## 许可证

MIT
