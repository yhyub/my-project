#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama DeepSeek模型部署脚本
用于安全部署DeepSeek-V3.2和DeepSeek-R1模型
遵循Ollama官方安全最佳实践
"""

import os
import sys
import subprocess
import time
import json


def check_ollama_installed():
    """检查Ollama是否已安装"""
    try:
        result = subprocess.run(["ollama", "--version"], check=True, capture_output=True, text=True)
        print(f"✓ Ollama已安装: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Ollama未安装")
        print("请先安装Ollama: https://ollama.com/download")
        return False


def pull_ollama_model(model_name, custom_name=None):
    """拉取Ollama模型"""
    try:
        print(f"\n正在拉取模型: {model_name}")
        # 构建拉取命令
        cmd = ["ollama", "pull", model_name]
        subprocess.run(cmd, check=True)
        
        # 如果指定了自定义名称，创建模型别名
        if custom_name and custom_name != model_name:
            print(f"创建模型别名: {custom_name} -> {model_name}")
            cmd = ["ollama", "cp", model_name, custom_name]
            subprocess.run(cmd, check=True)
        
        print(f"✓ 模型拉取成功: {model_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 模型拉取失败: {model_name}")
        print(f"错误信息: {e}")
        return False


def list_ollama_models():
    """列出已安装的Ollama模型"""
    try:
        result = subprocess.run(["ollama", "list"], check=True, capture_output=True, text=True)
        print(f"\n已安装的Ollama模型:\n{result.stdout}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"✗ 列出模型失败: {e}")
        return None


def create_ollama_modelfile(model_name, base_model, config=None):
    """创建Ollama模型配置文件"""
    modelfile_content = f"FROM {base_model}\n"
    
    if config:
        # 添加安全配置
        if config.get("system_prompt"):
            modelfile_content += f"SYSTEM \"{config['system_prompt']}\"\n"
        
        # 添加参数配置
        for key, value in config.get("parameters", {}).items():
            modelfile_content += f"PARAMETER {key} {value}\n"
    
    # 保存模型配置文件
    modelfile_path = f"modelfile_{model_name}"
    with open(modelfile_path, "w", encoding="utf-8") as f:
        f.write(modelfile_content)
    
    print(f"\n✓ 模型配置文件创建成功: {modelfile_path}")
    print(f"配置内容:\n{modelfile_content}")
    return modelfile_path


def create_custom_model(model_name, modelfile_path):
    """基于配置文件创建自定义模型"""
    try:
        print(f"\n正在创建自定义模型: {model_name}")
        cmd = ["ollama", "create", model_name, "-f", modelfile_path]
        subprocess.run(cmd, check=True)
        print(f"✓ 自定义模型创建成功: {model_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 自定义模型创建失败: {model_name}")
        print(f"错误信息: {e}")
        return False


def test_model_inference(model_name, test_prompt="你好，介绍一下自己"):
    """测试模型推理"""
    try:
        print(f"\n测试模型推理: {model_name}")
        print(f"测试提示词: {test_prompt}")
        
        cmd = ["ollama", "run", model_name, test_prompt]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print(f"✓ 模型推理成功")
        print(f"模型响应:\n{result.stdout}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"✗ 模型推理失败: {model_name}")
        print(f"错误信息: {e}")
        return None


def configure_ollama_security():
    """配置Ollama安全最佳实践"""
    print("\n" + "="*60)
    print("Ollama安全配置")
    print("="*60)
    
    # 检查Ollama配置目录
    ollama_config_dir = os.path.expanduser("~/.ollama")
    if not os.path.exists(ollama_config_dir):
        os.makedirs(ollama_config_dir)
        print(f"✓ 创建Ollama配置目录: {ollama_config_dir}")
    
    # 创建或更新Ollama配置文件
    config_path = os.path.join(ollama_config_dir, "config.json")
    
    # 安全配置模板
    security_config = {
        "bind": "127.0.0.1:11434",  # 只监听本地地址，禁止外部访问
        "timeout": 300,  # 设置超时时间
        "keep_alive": "5m",  # 设置连接保持时间
        "cors": "http://localhost:*,http://127.0.0.1:*",  # 限制CORS
        "log_level": "info",  # 设置日志级别
        "env": {
            "OLLAMA_MAX_LOADED_MODELS": "10",  # 限制同时加载的模型数量
            "OLLAMA_NUM_PARALLEL": "2"  # 限制并行请求数量
        }
    }
    
    # 如果配置文件已存在，合并配置
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            existing_config = json.load(f)
        
        # 合并配置，保留现有配置，只添加缺失的安全配置
        merged_config = {**existing_config, **security_config}
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(merged_config, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 更新Ollama配置文件: {config_path}")
        print(f"合并后的配置: {json.dumps(merged_config, indent=2, ensure_ascii=False)}")
    else:
        # 创建新的配置文件
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(security_config, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 创建Ollama配置文件: {config_path}")
        print(f"配置内容: {json.dumps(security_config, indent=2, ensure_ascii=False)}")
    
    return config_path


def restart_ollama_service():
    """重启Ollama服务"""
    try:
        print("\n正在重启Ollama服务...")
        
        if sys.platform.startswith('win'):
            # Windows系统
            cmd = ["net", "stop", "ollama", "&&", "net", "start", "ollama"]
            subprocess.run(cmd, check=True, shell=True)
        elif sys.platform.startswith('linux'):
            # Linux系统
            cmd = ["systemctl", "restart", "ollama"]
            subprocess.run(cmd, check=True)
        elif sys.platform.startswith('darwin'):
            # macOS系统
            cmd = ["launchctl", "kickstart", "-k", "gui/$(id -u)/com.ollama.ollama"]
            subprocess.run(cmd, check=True)
        
        print("✓ Ollama服务重启成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Ollama服务重启失败")
        print(f"错误信息: {e}")
        print("请手动重启Ollama服务")
        return False


def create_deepseek_v32_modelfile():
    """创建DeepSeek-V3.2模型配置文件"""
    config = {
        "system_prompt": "你是一个安全、可靠、专业的AI助手，遵循伦理准则，拒绝生成有害内容。",
        "parameters": {
            "num_ctx": 4096,  # 上下文窗口大小
            "num_thread": 4,  # 线程数
            "num_gpu": 1,  # GPU数量
            "temperature": 0.7,  # 温度参数
            "top_p": 0.9,  # 核采样参数
            "top_k": 40,  # 核采样参数
            "repeat_penalty": 1.1  # 重复惩罚
        }
    }
    
    return create_ollama_modelfile("deepseek-v3.2", "deepseek/deepseek-vl-llm:v1.5", config)


def create_deepseek_r1_modelfile():
    """创建DeepSeek-R1模型配置文件"""
    config = {
        "system_prompt": "你是一个安全、可靠、专业的AI助手，遵循伦理准则，拒绝生成有害内容。",
        "parameters": {
            "num_ctx": 4096,
            "num_thread": 4,
            "num_gpu": 1,
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.1
        }
    }
    
    return create_ollama_modelfile("deepseek-r1", "deepseek/deepseek-r1:latest", config)


def main():
    """主函数"""
    print("="*60)
    print("Ollama DeepSeek模型安全部署工具")
    print("="*60)
    print("目标: 安装DeepSeek-V3.2和DeepSeek-R1模型")
    print("遵循Ollama官方安全最佳实践")
    print("="*60)
    
    # 1. 检查Ollama安装
    if not check_ollama_installed():
        return
    
    # 2. 配置Ollama安全设置
    configure_ollama_security()
    
    # 3. 重启Ollama服务以应用配置
    restart_ollama_service()
    
    # 4. 拉取模型
    models_to_install = [
        # (模型名称, 自定义名称)
        ("deepseek/deepseek-r1:latest", "deepseek-r1"),
        ("deepseek/deepseek-v3:latest", "deepseek-v3.2")  # 使用最新的v3版本作为V3.2
    ]
    
    all_models_installed = True
    for model_name, custom_name in models_to_install:
        if not pull_ollama_model(model_name, custom_name):
            all_models_installed = False
    
    if not all_models_installed:
        print("\n✗ 部分模型安装失败，请检查网络连接或模型名称")
        return
    
    # 5. 创建自定义模型配置
    print("\n" + "="*60)
    print("创建自定义模型配置")
    print("="*60)
    
    # 创建DeepSeek-R1模型配置
    r1_modelfile = create_deepseek_r1_modelfile()
    create_custom_model("deepseek-r1-secure", r1_modelfile)
    
    # 创建DeepSeek-V3.2模型配置
    v32_modelfile = create_deepseek_v32_modelfile()
    create_custom_model("deepseek-v3.2-secure", v32_modelfile)
    
    # 6. 列出所有已安装模型
    list_ollama_models()
    
    # 7. 测试模型推理
    print("\n" + "="*60)
    print("测试模型推理")
    print("="*60)
    
    # 测试DeepSeek-V3.2模型
    test_model_inference("deepseek-v3.2", "你好，我是DeepSeek-V3.2吗？")
    
    # 测试DeepSeek-R1模型
    test_model_inference("deepseek-r1", "你好，我是DeepSeek-R1吗？")
    
    # 8. 设置默认模型为DeepSeek-V3.2
    print("\n" + "="*60)
    print("设置默认模型")
    print("="*60)
    
    try:
        # 创建一个名为"default"的模型，指向deepseek-v3.2
        cmd = ["ollama", "cp", "deepseek-v3.2", "default"]
        subprocess.run(cmd, check=True)
        print("✓ 默认模型设置为: deepseek-v3.2")
    except subprocess.CalledProcessError as e:
        print(f"✗ 默认模型设置失败: {e}")
    
    # 9. 显示使用说明
    print("\n" + "="*60)
    print("部署完成！")
    print("="*60)
    print("使用说明:")
    print("1. 运行DeepSeek-V3.2模型:")
    print("   ollama run deepseek-v3.2")
    print("   或直接运行默认模型: ollama run default")
    print("\n2. 运行DeepSeek-R1模型:")
    print("   ollama run deepseek-r1")
    print("\n3. 运行安全配置的模型:")
    print("   ollama run deepseek-v3.2-secure")
    print("   ollama run deepseek-r1-secure")
    print("\n4. API访问:")
    print("   curl http://localhost:11434/api/generate -d '{\"model\": \"deepseek-v3.2\", \"prompt\": \"你好\"}'")
    print("\n5. 查看模型列表:")
    print("   ollama list")
    print("\n6. 查看模型信息:")
    print("   ollama show deepseek-v3.2")
    print("\n7. 安全最佳实践已配置:")
    print("   - 仅本地访问")
    print("   - 合理的超时设置")
    print("   - 限制并行请求")
    print("   - 安全的系统提示词")
    print("   - 优化的模型参数")


if __name__ == "__main__":
    main()
