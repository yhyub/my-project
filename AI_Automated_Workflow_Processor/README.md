# AI_Automated_Workflow_Processo - 完整的AI自动化工作流处理器

## 项目概述

AI_Automated_Workflow_Processo 是一个功能强大的AI自动化工作流处理器，集成了工作流修复、错误检测、人工智能代码分析、工作流生成、批量处理、画布自动化填写等核心功能。支持从URL获取资源，自动检测并修复工作流错误，分析代码质量，根据需求生成新工作流，实现工作流的批量修复和合并，以及自动化填写Coze画布。通过智能结果合并，返回统一的处理结果和类型，提升工作流开发和维护效率。

## 功能特性

- ✅ **工作流修复**: 自动检测并修复工作流中的错误
- ✅ **错误检测**: 全面检查工作流的结构和逻辑错误
- ✅ **代码质量分析**: 分析工作流中的代码质量
- ✅ **工作流生成**: 根据需求自动生成工作流
- ✅ **批量处理**: 支持批量处理多个工作流
- ✅ **画布自动化填写**: 自动填写Coze画布
- ✅ **智能结果合并**: 统一处理结果和类型
- ✅ **从URL获取资源**: 支持从远程URL获取工作流资源
- ✅ **HTTP服务器模式**: 支持以API方式提供服务
- ✅ **可配置**: 支持多种配置选项
- ✅ **支持多种工作流格式**: JSON、YAML等

## 安装说明

### 环境要求

- Python 3.7+
- pip 19.0+

### 安装依赖

```bash
# 安装基础依赖
pip install requests flask

# 安装可选依赖（用于更高级的代码分析）
pip install pylint flake8
```

### 克隆项目

```bash
git clone <repository_url>
cd AI_Automated_Workflow_Processor
```

## 快速开始

### 1. 运行测试

```bash
python ai_automated_workflow_processor.py --test
```

### 2. 启动HTTP服务器

```bash
python ai_automated_workflow_processor.py --server
```

服务器将在 `http://localhost:8080` 启动。

### 3. 健康检查

```bash
curl http://localhost:8080/health
```

## 命令行使用

### 运行测试

```bash
python ai_automated_workflow_processor.py --test
```

### 启动服务器

```bash
# 默认参数
python ai_automated_workflow_processor.py --server

# 自定义主机和端口
python ai_automated_workflow_processor.py --server --host 0.0.0.0 --port 8000
```

## API使用

### 处理工作流

```bash
curl -X POST http://localhost:8080/process \
  -H "Content-Type: application/json" \
  -d '{"type": "detect_errors", "workflow": {"name": "Test Workflow", "nodes": [{"type": "start", "data": {"label": "Start"}}]}}'
```

### 支持的处理类型

1. **fetch_resource**: 从URL获取资源
2. **detect_errors**: 检测工作流错误
3. **fix_errors**: 修复工作流错误
4. **analyze_code**: 分析代码质量
5. **generate_workflow**: 根据需求生成工作流
6. **auto_fill_canvas**: 自动化填写画布
7. **batch_process**: 批量处理工作流
8. **merge_results**: 合并处理结果

## 配置说明

### 配置文件示例

创建 `config.json` 文件，内容如下：

```json
{
    "deepseek_api_key": "your_deepseek_api_key_here",
    "deepseek_api_url": "https://api.deepseek.com",
    "model": "deepseek-chat",
    "timeout": 60,
    "output_dir": "./workflow_output",
    "log_level": "info"
}
```

### 配置选项

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| deepseek_api_key | string | "" | DeepSeek API 密钥 |
| deepseek_api_url | string | "https://api.deepseek.com" | DeepSeek API URL |
| model | string | "deepseek-chat" | 默认使用的模型 |
| timeout | integer | 60 | 请求超时时间（秒） |
| output_dir | string | "./workflow_output" | 输出目录 |
| log_level | string | "info" | 日志级别 |
| max_batch_size | integer | 100 | 批量处理的最大数量 |
| auto_save | boolean | true | 是否自动保存处理结果 |
| enable_code_analysis | boolean | true | 是否启用代码分析 |
| enable_workflow_generation | boolean | true | 是否启用工作流生成 |
| enable_auto_fix | boolean | true | 是否启用自动修复 |

## 核心功能说明

### 1. 工作流错误检测

自动检测工作流中的各种错误，包括：
- 缺少必填字段
- 节点缺少必填属性
- 重复的节点ID
- 无效的边引用

### 2. 工作流修复

自动修复工作流中的错误，包括：
- 添加缺少的必填字段
- 生成缺失的节点ID
- 修复重复的节点和边ID
- 添加缺失的边

### 3. 代码质量分析

分析工作流中的代码质量，包括：
- 代码行数统计
- 注释比例分析
- 长行检查
- 重复代码检测
- 缺少文档字符串检查

### 4. 工作流生成

根据需求自动生成工作流，支持：
- 基于自然语言描述生成工作流
- 生成符合Coze格式的工作流
- 包含节点和边的完整工作流

### 5. 画布自动化填写

自动填写Coze画布，包括：
- 设置画布标题和描述
- 自动布局节点
- 设置画布主题和样式

### 6. 批量处理

支持批量处理多个工作流，提高处理效率。

### 7. 智能结果合并

合并多个处理结果，提供统一的结果格式和类型。

## 示例

### 1. 生成工作流

```python
from ai_automated_workflow_processor import AIWorkflowProcessor

processor = AIWorkflowProcessor()
result = processor.generate_workflow("创建一个简单的用户注册工作流")
print(result["workflow"]["name"])
print(f"节点数量: {len(result['workflow']['nodes'])}")
```

### 2. 检测并修复工作流错误

```python
from ai_automated_workflow_processor import AIWorkflowProcessor

# 创建一个有错误的工作流
broken_workflow = {
    "name": "Broken Workflow",
    "nodes": [
        {"type": "start", "data": {"label": "Start"}}  # 缺少id字段
    ]
}

processor = AIWorkflowProcessor()

# 检测错误
error_report = processor.detect_workflow_errors(broken_workflow)
print(f"错误数量: {error_report['total_errors']}")

# 修复错误
fix_result = processor.fix_workflow_errors(broken_workflow, error_report)
print(f"修复数量: {fix_result['total_fixes']}")
print(f"修复后是否包含edges字段: {'edges' in fix_result['fixed_workflow']}")
```

### 3. 分析代码质量

```python
from ai_automated_workflow_processor import AIWorkflowProcessor

test_code = '''
def add(a, b):
    return a + b

print(add(1, 2))
'''

processor = AIWorkflowProcessor()
code_analysis = processor.analyze_code_quality(test_code)
print(f"代码行数: {code_analysis['total_lines']}")
print(f"注释比例: {code_analysis['comment_ratio']}")
print(f"问题数量: {code_analysis['total_issues']}")
```

## API 端点

### 1. POST /process

处理工作流请求。

**请求体格式**：

```json
{
    "type": "detect_errors",
    "workflow": { /* 工作流数据 */ }
}
```

**响应格式**：

```json
{
    "status": "success",
    "data": { /* 处理结果 */ },
    "message": "处理成功"
}
```

### 2. GET /health

健康检查端点。

**响应格式**：

```json
{
    "status": "healthy",
    "service": "AI_Automated_Workflow_Processo",
    "timestamp": 1735536000
}
```

## 支持的工作流格式

- JSON
- YAML
- YML

## 日志

日志将同时输出到控制台和 `ai_workflow_processor.log` 文件中。日志级别可以通过配置文件中的 `log_level` 选项进行设置。

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 项目地址: <repository_url>
- Issues: <repository_url>/issues

## 更新日志

### v1.0.0 (2025-12-29)

- 初始版本
- 实现了所有核心功能
- 支持HTTP服务器模式
- 支持命令行使用
- 支持配置文件

## 致谢

感谢所有为本项目做出贡献的开发者！

## 免责声明

本项目仅供学习和研究使用，请勿用于商业用途。使用本项目产生的任何后果，由使用者自行承担。

---

**AI_Automated_Workflow_Processo** - 让工作流开发更智能、更高效！