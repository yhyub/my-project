# DeepSeek-R1本地部署指南

## 部署方式

### 1. 使用API服务器（推荐）

我们已经配置了一个基于FastAPI的API服务器，可以直接运行：

```bash
python api_server.py
```

**注意**：首次运行会从Hugging Face下载模型文件，可能需要较长时间。如果遇到网络问题，可以尝试：

- 检查网络连接
- 配置Hugging Face代理
- 使用本地已有的模型文件

### 2. 使用DeepSeek-V3推理脚本

DeepSeek-R1基于DeepSeek-V3架构，你可以使用DeepSeek-V3的推理脚本运行：

```bash
cd DeepSeek-V3/inference
# 安装依赖
pip install -r requirements.txt
# 运行推理
python generate.py --help
```

### 3. 使用第三方框架

根据DeepSeek-R1 README，你还可以使用以下框架运行模型：

- **SGLang**：支持FP8和BF16推理
- **LMDeploy**：支持高效推理和部署
- **vLLM**：支持并行推理
- **LightLLM**：支持单节点或多节点部署

## 模型文件

DeepSeek-R1模型文件需要从Hugging Face下载：

- DeepSeek-R1: https://huggingface.co/deepseek-ai/DeepSeek-R1
- DeepSeek-R1-Distill-Qwen-32B: https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B

## 推荐配置

根据DeepSeek-R1 README，推荐使用以下配置：

- 温度：0.5-0.7（推荐0.6）
- 避免添加系统提示，所有指令都应包含在用户提示中
- 对于数学问题，建议在提示中添加："Please reason step by step, and put your final answer within \boxed{}"
- 确保模型以"<think>\n"开头输出

## 本地模型使用

如果你已经下载了模型文件，可以修改`api_server.py`中的`MODEL_CONFIG`配置，指向本地模型路径：

```python
MODEL_CONFIG = {
    "model_path": "/path/to/local/model",  # 本地模型路径
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "dtype": torch.float16,
    "trust_remote_code": True,
    "device_map": "auto"
}
```

## 常见问题

1. **模型下载慢**：可以使用Hugging Face代理，或者使用国内镜像源
2. **GPU内存不足**：尝试使用更小的模型版本，或者使用CPU部署
3. **推理速度慢**：考虑使用FP8推理，或者使用更高效的框架
4. **模型无法启动**：检查依赖是否安装正确，或者尝试使用不同的框架

## 技术支持

如果遇到问题，可以：

- 查看DeepSeek-R1官方README：https://github.com/deepseek-ai/DeepSeek-R1
- 查看DeepSeek-V3官方README：https://github.com/deepseek-ai/DeepSeek-V3
- 联系DeepSeek官方支持：service@deepseek.com

## 下一步

1. 确保网络连接正常，重新尝试运行API服务器
2. 或者下载模型文件到本地，修改配置后使用本地模型
3. 或者尝试使用其他部署方式

祝你使用愉快！