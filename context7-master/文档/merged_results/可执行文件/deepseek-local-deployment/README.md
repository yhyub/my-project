# DeepSeek本地部署工具

一个全自动化的DeepSeek模型本地部署工具，支持多种部署方式，包括Transformers直接部署和Ollama部署。

## 功能特性

- ✅ 自动检查和安装Git
- ✅ 克隆DeepSeek核心仓库
- ✅ 安装所有必要依赖
- ✅ 支持多种模型大小（1.5B、7B、8B、14B、32B、70B）
- ✅ 支持两种部署方式：
  - Transformers直接部署
  - Ollama部署
- ✅ 生成可直接使用的API服务器
- ✅ 提供详细的使用说明

## 项目结构

```
deepseek-local-deployment/
├── main.py              # 主部署脚本
├── requirements.txt     # 项目依赖
├── api_server.py        # 生成的API服务器（运行后生成）
├── DeepSeek-R1/         # DeepSeek-R1模型仓库
├── awesome-deepseek-integration/  # DeepSeek集成工具集
└── models/              # 下载的模型文件
```

## 快速开始

### 1. 环境要求

- Python 3.8+
- Git
- 至少16GB内存（推荐32GB+）
- GPU（可选，推荐NVIDIA GPU）

### 2. 安装依赖

```bash
cd deepseek-local-deployment
pip install -r requirements.txt
```

### 3. 运行部署脚本

```bash
python main.py
```

### 4. 选择部署方式

运行脚本后，会出现以下选项：

```
模型部署选项：
1. 使用Transformers直接下载DeepSeek模型
2. 使用Ollama部署DeepSeek模型
3. 跳过模型下载（手动部署）
```

#### 选项1：Transformers直接部署

- 选择模型大小（1.5b/7b/8b/14b/32b/70b）
- 自动下载模型到本地
- 生成API服务器文件

#### 选项2：Ollama部署

- 检查Ollama是否已安装
- 自动拉取DeepSeek-R1模型
- 可直接通过`ollama run deepseek-r1`使用

#### 选项3：手动部署

- 跳过模型下载
- 可自行部署模型

## 使用指南

### 1. 直接使用Transformers

```bash
python -c "from transformers import AutoModelForCausalLM, AutoTokenizer; tokenizer = AutoTokenizer.from_pretrained('./models'); model = AutoModelForCausalLM.from_pretrained('./models'); print(tokenizer.decode(model.generate(**tokenizer('你好', return_tensors='pt'))[0]))"
```

### 2. 使用Ollama

```bash
ollama run deepseek-r1 "你好"
```

### 3. 启动API服务

```bash
python api_server.py
```

API服务启动后，可访问：
- API文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health
- 完成API：POST http://localhost:8000/v1/completions

### 4. 使用API示例

```bash
curl -X POST http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"prompt": "你好", "max_new_tokens": 100}'
```

## 模型参数规模

| 模型大小 | 参数规模 | 推荐内存 |
|---------|---------|---------|
| 1.5B    | 15亿    | 8GB+    |
| 7B      | 70亿    | 16GB+   |
| 8B      | 80亿    | 20GB+   |
| 14B     | 140亿   | 32GB+   |
| 32B     | 320亿   | 64GB+   |
| 70B     | 700亿   | 128GB+  |
| 671B    | 6710亿  | 多卡GPU |

## 集成工具

部署完成后，可在`awesome-deepseek-integration`目录中找到80+个DeepSeek集成工具，包括：

- 代码生成工具
- 自动化办公工具
- AI助理
- 跨平台开发工具
- 等等

## 常见问题

### Q: Git安装失败

A: 请手动下载并安装Git：https://git-scm.com/download

### Q: 模型下载速度慢

A: 可以使用国内镜像源，或考虑使用Ollama部署方式

### Q: GPU内存不足

A: 尝试使用较小的模型，或使用CPU部署（速度会较慢）

### Q: Ollama未找到

A: 请先安装Ollama：https://ollama.com/download

## 许可证

MIT License

## 参考链接

- [DeepSeek官方GitHub](https://github.com/deepseek-ai/)
- [DeepSeek-R1模型](https://github.com/deepseek-ai/DeepSeek-R1)
- [Awesome DeepSeek Integration](https://github.com/deepseek-ai/awesome-deepseek-integration)
- [Ollama](https://ollama.com/)
