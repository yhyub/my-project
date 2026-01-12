# DeepSeek Ollama本地部署指南

## 简介

本指南介绍如何在本地环境中使用Ollama安全部署DeepSeek私有模型，包括DeepSeek-V3.2和DeepSeek-R1。

## 环境要求

- Windows 10/11、Linux或macOS
- 至少16GB内存（推荐32GB+）
- GPU（可选，推荐NVIDIA GPU）
- Ollama 0.1.10+（自动安装）

## 部署流程

### 1. 安装Ollama

Ollama是一个轻量级的本地LLM模型管理工具，支持多种模型格式。

#### Windows安装

```powershell
winget install Ollama.Ollama
```

#### Linux安装

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### macOS安装

```bash
brew install ollama
```

### 2. 启动Ollama服务

安装完成后，Ollama服务会自动启动。你可以通过以下命令检查服务状态：

```bash
ollama --version
```

### 3. 运行部署脚本

使用提供的自动化部署脚本，一键部署DeepSeek模型：

```bash
cd deepseek-local-deployment
python ollama_deepseek_deploy.py
```

## 模型信息

### DeepSeek-V3.2

- **模型名称**: `deepseek-v3.2`
- **主要用途**: 通用AI助手，支持多轮对话、代码生成、内容创作等
- **模型大小**: 约10GB
- **上下文长度**: 4096 tokens

### DeepSeek-R1

- **模型名称**: `deepseek-r1`
- **主要用途**: 推理和分析任务，支持复杂逻辑推理
- **模型大小**: 约10GB
- **上下文长度**: 4096 tokens

## 安全最佳实践

本部署遵循Ollama官方安全最佳实践：

### 1. 网络安全

- **仅本地访问**: 模型服务仅监听本地地址（127.0.0.1:11434），禁止外部访问
- **CORS限制**: 仅允许本地域名访问API
- **连接超时**: 设置合理的连接超时时间（300秒）

### 2. 资源限制

- **最大加载模型数**: 限制同时加载10个模型
- **并行请求数**: 限制并行请求数为2个
- **线程控制**: 每个模型最多使用4个线程

### 3. 模型安全

- **安全系统提示词**: 所有模型配置了安全的系统提示词，拒绝生成有害内容
- **合理的生成参数**: 设置适当的温度参数（0.7），平衡多样性和安全性
- **重复惩罚**: 启用重复惩罚（1.1），减少无意义重复内容

### 4. 日志管理

- **日志级别**: 设置为info级别，记录关键操作
- **不记录敏感信息**: 不记录模型输入输出内容

## 使用方法

### 1. 直接运行模型

```bash
# 运行DeepSeek-V3.2（默认模型）
ollama run deepseek-v3.2

# 或使用默认别名
ollama run default

# 运行DeepSeek-R1
ollama run deepseek-r1
```

### 2. 使用API访问

```bash
# 使用curl访问API
curl http://localhost:11434/api/generate -d '{"model": "deepseek-v3.2", "prompt": "你好"}'

# 使用Python访问API
import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "deepseek-v3.2",
        "prompt": "你好",
        "stream": False
    }
)

print(response.json()["response"])
```

### 3. 使用安全配置的模型

```bash
# 运行安全配置的DeepSeek-V3.2
ollama run deepseek-v3.2-secure

# 运行安全配置的DeepSeek-R1
ollama run deepseek-r1-secure
```

## 管理命令

### 查看模型列表

```bash
ollama list
```

### 查看模型信息

```bash
# 查看DeepSeek-V3.2信息
ollama show deepseek-v3.2

# 查看模型参数
ollama show deepseek-v3.2 --modelfile
```

### 删除模型

```bash
# 删除DeepSeek-R1模型
ollama rm deepseek-r1
```

### 更新模型

```bash
# 更新DeepSeek-V3.2模型
ollama pull deepseek-v3.2
```

### 复制模型（创建别名）

```bash
# 创建模型别名
ollama cp deepseek-v3.2 my-deepseek
```

## 高级配置

### 自定义模型参数

1. 创建模型配置文件（Modelfile）：

```bash
echo 'FROM deepseek-v3.2
PARAMETER num_ctx 8192
PARAMETER temperature 0.8
SYSTEM "你是一个专业的代码生成助手。"' > modelfile_custom
```

2. 创建自定义模型：

```bash
ollama create deepseek-v3.2-code -f modelfile_custom
```

3. 使用自定义模型：

```bash
ollama run deepseek-v3.2-code
```

### 调整GPU使用

```bash
# 修改模型配置，调整GPU使用
ollama create deepseek-v3.2-gpu -f - <<EOF
FROM deepseek-v3.2
PARAMETER num_gpu 2
EOF
```

## 常见问题

### Q: 模型下载速度慢

A: 可以尝试使用代理，或者手动下载模型文件后导入：

```bash
# 手动下载模型后，使用以下命令导入
ollama create deepseek-v3.2 -f - <<EOF
FROM ./deepseek-v3.2.gguf
EOF
```

### Q: 内存不足

A: 尝试使用较小的模型，或者调整模型参数：

```bash
# 创建低内存版本模型
ollama create deepseek-v3.2-light -f - <<EOF
FROM deepseek-v3.2
PARAMETER num_thread 2
PARAMETER num_gpu 0
EOF
```

### Q: 服务无法启动

A: 检查Ollama服务状态：

```bash
# Windows
et start ollama

# Linux
systemctl status ollama

# macOS
launchctl list | grep ollama
```

## 监控与维护

### 查看Ollama日志

```bash
# Windows
get-eventlog -LogName Application -Source Ollama

# Linux
journalctl -u ollama

# macOS
log show --predicate 'process == "ollama"'
```

### 重启Ollama服务

```bash
# Windows
net stop ollama && net start ollama

# Linux
sudo systemctl restart ollama

# macOS
launchctl kickstart -k gui/$(id -u)/com.ollama.ollama
```

## API参考

### 生成文本

```bash
POST /api/generate
```

**请求参数**：
- `model`: 模型名称（必填）
- `prompt`: 输入提示（必填）
- `stream`: 是否流式输出（可选，默认true）
- `temperature`: 生成温度（可选，默认0.7）
- `max_new_tokens`: 最大生成token数（可选，默认512）

**响应**：
```json
{
  "model": "deepseek-v3.2",
  "created_at": "2024-01-01T00:00:00Z",
  "response": "你好！我是DeepSeek-V3.2，很高兴为您服务。",
  "done": true
}
```

### 聊天对话

```bash
POST /api/chat
```

**请求参数**：
- `model`: 模型名称（必填）
- `messages`: 对话历史（必填）
- `stream`: 是否流式输出（可选，默认true）

**响应**：
```json
{
  "model": "deepseek-v3.2",
  "created_at": "2024-01-01T00:00:00Z",
  "message": {
    "role": "assistant",
    "content": "你好！我是DeepSeek-V3.2，很高兴为您服务。"
  },
  "done": true
}
```

## 许可证

- **Ollama**: Apache License 2.0
- **DeepSeek模型**: 请参考DeepSeek官方许可证

## 参考链接

- [Ollama官方文档](https://ollama.com/docs)
- [DeepSeek官方GitHub](https://github.com/deepseek-ai/)
- [DeepSeek-V3模型](https://huggingface.co/deepseek-ai/deepseek-v3)
- [DeepSeek-R1模型](https://huggingface.co/deepseek-ai/deepseek-r1)

## 联系方式

如有问题或建议，请联系：
- 项目地址：https://github.com/deepseek-ai/awesome-deepseek-integration
- 官方文档：https://deepseek-ai.github.io/ 
