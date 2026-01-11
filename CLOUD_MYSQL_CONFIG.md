# 云端MySQL配置指南

## 配置说明

本项目已将本地MySQL数据库替换为云端MySQL配置，以减少本地资源占用。通过云端MySQL，您可以：

- 无限存储数据，不受本地存储空间限制
- 不占用本地CPU和内存资源
- 支持任意大小和类型的文件存储
- 提高数据安全性和可靠性

## 配置步骤

### 1. 获取云端MySQL信息

请准备好您的云端MySQL数据库信息：
- 数据库主机地址 (DB_HOST)
- 数据库端口 (DB_PORT，默认为3306)
- 数据库用户名 (DB_USER)
- 数据库密码 (DB_PASSWORD)
- 数据库名称 (DB_NAME)

### 2. 配置环境变量

编辑项目根目录下的 `.env` 文件，将云端MySQL信息填入对应的配置项：

```bash
# 云端MySQL配置
DB_HOST=your_cloud_mysql_host
DB_PORT=3306
DB_USER=coze_user
DB_PASSWORD=coze_password
DB_NAME=coze_db
```

### 3. 初始化云端数据库

在使用项目前，您需要在云端MySQL数据库中执行初始化操作：

#### 3.1 创建数据库

如果您的云端MySQL中还没有创建 `coze_db` 数据库，请先创建：

```sql
CREATE DATABASE coze_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 3.2 导入数据库架构

使用您的云端数据库管理工具（如phpMyAdmin、Navicat等）执行 `schema.hcl` 文件中的数据库架构定义。

或者，您可以使用Atlas工具在本地执行：

```bash
atlas schema apply -u 'mysql://DB_USER:DB_PASSWORD@DB_HOST:DB_PORT/DB_NAME' -f ./schema.hcl --auto-approve
```

#### 3.3 导入初始数据

使用您的云端数据库管理工具执行 `init.sql` 文件，导入初始数据：

```bash
mysql -h DB_HOST -u DB_USER -p DB_NAME < ./init.sql
```

### 4. 启动项目

完成上述配置后，您可以使用以下命令启动项目：

```bash
docker-compose up -d
```

## 注意事项

1. 请确保您的云端MySQL数据库允许外部连接，或者将项目服务器的IP地址添加到云端数据库的白名单中
2. 建议使用SSL连接以提高数据传输安全性
3. 定期备份云端数据库，以防止数据丢失
4. 监控云端数据库的性能和资源使用情况
5. 根据实际需求调整云端数据库的配置和规格

## 常见问题

### Q: 如何验证云端MySQL连接是否成功？

A: 您可以使用以下命令测试连接：

```bash
mysql -h DB_HOST -u DB_USER -p
```

### Q: 云端MySQL连接失败怎么办？

A: 请检查以下几点：
- 确认 `.env` 文件中的配置信息正确
- 确认云端MySQL服务正在运行
- 确认您的网络可以访问云端MySQL主机
- 确认云端MySQL允许外部连接
- 确认数据库用户名和密码正确

### Q: 如何查看项目日志？

A: 您可以使用以下命令查看项目日志：

```bash
docker-compose logs -f coze-server
```

## 性能优化建议

1. 根据业务需求选择合适的云端MySQL实例规格
2. 合理设计数据库索引，提高查询效率
3. 定期优化和清理数据库
4. 考虑使用读写分离架构，提高系统性能
5. 监控数据库慢查询日志，优化查询语句

## 安全建议

1. 不要将数据库密码直接写入代码中，使用环境变量或配置文件管理
2. 定期更换数据库密码
3. 限制数据库用户的权限，遵循最小权限原则
4. 启用数据库审计功能，监控数据库操作
5. 使用SSL加密连接，保护数据传输安全
