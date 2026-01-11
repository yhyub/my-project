# 统一MCP工具 - 完整文档

## 1. 概述

统一MCP工具是一个完全融合的MCP服务器，整合了所有DeepSeek相关功能和资源转换功能，支持自动化安全调用，符合Trae CN安全标准。

## 2. 功能特性

### 2.1 核心功能

- **DeepSeek数据管理**：对话、备份、样本、完整对话、报告等
- **资源转换**：项目/文件夹、URL、API、网站、帖子等
- **安全调用**：速率限制、命令白名单、缓存等
- **自动化执行**：支持Coze、DeepSeek、百度浏览器等
- **标准MCP协议支持**：持续运行响应Trae IDE请求

### 2.2 安全特性

- 内容过滤
- 敏感数据检测
- 恶意代码扫描
- URL安全检查
- 速率限制
- 命令白名单

## 3. 快速开始

### 3.1 安装依赖

```bash
pip install -r requirements.txt
```

### 3.2 启动服务器

```bash
python unified_all_in_one.py --host localhost --port 5000
```

或者使用配置文件启动：

```bash
python unified_all_in_one.py --config unified_all_in_one_config.json
```

## 4. 配置说明

### 4.1 核心配置

```json
{
  "core": {
    "server": {
      "host": "localhost",
      "port": 5000,
      "timeout": 600
    }
  }
}
```

### 4.2 安全配置

```json
{
  "security": {
    "enabled": true,
    "rateLimiting": 30,
    "command_whitelist": []
  }
}
```

## 5. 使用指南

### 5.1 DeepSeek MCP使用

1. 配置DeepSeek API密钥
2. 启动MCP服务器
3. 在Trae IDE中配置MCP连接
4. 开始使用DeepSeek功能

### 5.2 Coze集成

- Coze-Doubao集成
- Coze插件管理
- Coze API文档使用

## 6. 优化建议

- 启用内存优化
- 启用存储优化
- 配置适当的速率限制
- 定期清理缓存

## 7. 故障排除

### 7.1 常见错误

- **端口被占用**：修改配置文件中的端口号
- **API密钥错误**：检查配置文件中的API密钥
- **连接超时**：增加timeout配置

### 7.2 日志查看

查看控制台输出的日志信息，定位问题所在。

## 8. 更新日志

### v2.0
- 完全融合所有MCP功能
- 统一配置文件
- 增强安全性
- 优化性能

## 9. 许可证

本项目采用MIT许可证。

## 10. 联系信息

如有问题或建议，请联系项目维护者。
