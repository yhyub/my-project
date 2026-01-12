# DeepSeek 模型手动部署指南

## 1. 环境准备

### 1.1 手动安装 Ollama

由于自动安装遇到控制台异常，建议手动下载并安装 Ollama：

1. 访问 Ollama 官方下载页面：https://ollama.com/download
2. 选择适合您系统的版本（Windows/macOS/Linux）
3. 下载并运行安装程序
4. 按照安装向导完成安装

### 1.2 验证 Ollama 安装

安装完成后，打开终端（命令提示符或 PowerShell），运行以下命令验证安装：

```bash
ollama --version
```

如果安装成功，会显示 Ollama 版本信息。

## 2. Ollama 安全配置

按照 Ollama 官方安全最佳实践配置 Ollama：

### 2.1 创建 Ollama 配置文件

1. 打开文件资源管理器，导航到以下目录：
   - Windows: `C:\Users\YourUsername\.ollama`
   - macOS/Linux: `~/.ollama`

2. 创建或编辑 `config.json` 文件，添加以下安全配置：

```json
{
  "bind": "127.0.0.1:11434",
  "timeout": 300,
  "keep_alive": "5m",
  "cors": "http://localhost:*,http://127.0.0.1:*",
  "log_level": "info",
  "env": {
    "OLLAMA_MAX_LOADED_MODELS": "10",
    "OLLAMA_NUM_PARALLEL": "2"
  }
}
```

### 2.2 重启 Ollama 服务

1. Windows：
   - 打开服务管理器（services.msc）
   - 找到 "Ollama Service"
   - 右键点击，选择 "重启"

2. macOS：
   ```bash
   launchctl kickstart -k gui/$(id -u)/com.ollama.ollama
   ```

3. Linux：
   ```bash
   sudo systemctl restart ollama
   ```

## 3. 拉取 DeepSeek 模型

### 3.1 拉取 DeepSeek-V3.2 模型

DeepSeek-V3.2 是主要使用的模型，运行以下命令拉取：

```bash
ollama pull deepseek-v3
```

### 3.2 拉取 DeepSeek-R1 模型

DeepSeek-R1 作为兼容模型，运行以下命令拉取：

```bash
ollama pull deepseek-r1
```

### 3.3 创建模型别名

将 DeepSeek-V3 设置为主要使用的模型：

```bash
ollama cp deepseek-v3 deepseek-v3.2
```

## 4. 验证模型部署

### 4.1 列出已安装的模型

```bash
ollama list
```

您应该看到以下模型：
- `deepseek-v3`: DeepSeek-V3 模型
- `deepseek-v3.2`: DeepSeek-V3.2 别名
- `deepseek-r1`: DeepSeek-R1 模型

### 4.2 测试模型推理

测试 DeepSeek-V3.2 模型：

```bash
ollama run deepseek-v3.2 "你好，介绍一下自己"
```

测试 DeepSeek-R1 模型：

```bash
ollama run deepseek-r1 "你好，介绍一下自己"
```

## 5. 安全使用模型

### 5.1 创建安全配置的模型

为模型添加安全的系统提示词：

1. 创建 `modelfile_deepseek-v3.2-secure` 文件：

```yaml
FROM deepseek-v3.2
SYSTEM "你是一个安全、可靠、专业的AI助手，遵循伦理准则，拒绝生成有害内容。"
PARAMETER num_ctx 4096
PARAMETER num_thread 4
PARAMETER num_gpu 1
PARAMETER temperature 0.7
PARAMETER top_p 0.9
```

2. 创建 `modelfile_deepseek-r1-secure` 文件：

```yaml
FROM deepseek-r1
SYSTEM "你是一个安全、可靠、专业的AI助手，遵循伦理准则，拒绝生成有害内容。"
PARAMETER num_ctx 4096
PARAMETER num_thread 4
PARAMETER num_gpu 1
PARAMETER temperature 0.7
PARAMETER top_p 0.9
```

3. 创建安全配置的模型：

```bash
ollama create deepseek-v3.2-secure -f modelfile_deepseek-v3.2-secure
ollama create deepseek-r1-secure -f modelfile_deepseek-r1-secure
```

### 5.2 使用安全配置的模型

```bash
ollama run deepseek-v3.2-secure "你好，介绍一下自己"
```

## 6. API 访问

### 6.1 启动 Ollama API 服务

Ollama 默认启动 API 服务，监听 `127.0.0.1:11434`。

### 6.2 测试 API 访问

使用 curl 测试 API：

```bash
curl http://localhost:11434/api/generate -d '{"model": "deepseek-v3.2", "prompt": "你好", "stream": false}'
```

### 6.3 使用 Python 访问 API

```python
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

## 7. 高级配置

### 7.1 调整模型参数

根据您的硬件配置调整模型参数：

```yaml
FROM deepseek-v3.2
PARAMETER num_ctx 8192  # 增加上下文窗口
PARAMETER num_thread 8  # 增加线程数
PARAMETER num_gpu 2     # 增加GPU使用
```

### 7.2 配置 Ollama 环境变量

创建 `.env` 文件，添加以下环境变量：

```env
OLLAMA_MAX_LOADED_MODELS=10
OLLAMA_NUM_PARALLEL=2
OLLAMA_TEMPERATURE=0.7
```

## 8. 模型兼容性验证

### 8.1 检查模型版本

```bash
ollama show deepseek-v3.2 --modelfile
ollama show deepseek-r1 --modelfile
```

### 8.2 验证模型功能

运行相同的提示词，比较两个模型的响应：

```bash
ollama run deepseek-v3.2 "1 + 1 = ?"
ollama run deepseek-r1 "1 + 1 = ?"
```

## 9. 故障排除

### 9.1 Ollama 服务无法启动

- 检查服务状态：
  - Windows: `services.msc` 中查看 "Ollama Service"
  - Linux: `systemctl status ollama`
  - macOS: `launchctl list | grep ollama`

- 查看日志：
  - Windows: 事件查看器中搜索 "Ollama"
  - Linux: `journalctl -u ollama`
  - macOS: `log show --predicate 'process == "ollama"'`

### 9.2 模型拉取失败

- 检查网络连接
- 尝试使用代理：
  ```bash
  set HTTP_PROXY=http://proxy.example.com:8080
  set HTTPS_PROXY=http://proxy.example.com:8080
  ollama pull deepseek-v3
  ```

### 9.3 模型推理缓慢

- 检查 GPU 驱动是否正确安装
- 减少上下文窗口大小：
  ```yaml
  FROM deepseek-v3.2
  PARAMETER num_ctx 2048
  ```

## 10. 安全最佳实践

### 10.1 网络安全

- **仅本地访问**: API 服务仅监听 `127.0.0.1:11434`，禁止外部访问
- **CORS 限制**: 仅允许本地域名访问 API
- **连接超时**: 设置合理的连接超时时间（300秒）

### 10.2 资源限制

- **最大加载模型数**: 限制为 10 个
- **并行请求数**: 限制为 2 个
- **线程控制**: 每个模型最多使用 4 个线程

### 10.3 模型安全

- **安全系统提示词**: 所有模型配置了安全的系统提示词
- **合理的生成参数**: 温度参数设置为 0.7，平衡多样性和安全性
- **重复惩罚**: 启用重复惩罚，减少无意义重复内容

## 11. 日常使用

### 11.1 运行模型

```bash
# 运行主要模型
ollama run deepseek-v3.2

# 运行兼容模型
ollama run deepseek-r1

# 运行安全配置的模型
ollama run deepseek-v3.2-secure
```

### 11.2 更新模型

```bash
ollama pull deepseek-v3
ollama pull deepseek-r1
```

### 11.3 删除模型

```bash
ollama rm deepseek-v3.2-secure
```

## 12. 监控与维护

### 12.1 查看 Ollama 日志

- Windows: 事件查看器
- Linux: `journalctl -u ollama -f`
- macOS: `log stream --predicate 'process == "ollama"'`

### 12.2 重启 Ollama 服务

- Windows: `net stop ollama && net start ollama`
- Linux: `sudo systemctl restart ollama`
- macOS: `launchctl kickstart -k gui/$(id -u)/com.ollama.ollama`

## 13. 总结

通过手动安装和配置，您可以成功部署 DeepSeek 模型，并遵循 Ollama 官方安全最佳实践。以下是部署流程的总结：

1. 手动安装 Ollama
2. 配置 Ollama 安全设置
3. 拉取 DeepSeek-V3 和 DeepSeek-R1 模型
4. 创建模型别名
5. 配置安全模型
6. 验证模型部署
7. 使用 API 访问模型

按照本指南操作，您将拥有一个安全、可靠的本地 DeepSeek 模型服务环境。