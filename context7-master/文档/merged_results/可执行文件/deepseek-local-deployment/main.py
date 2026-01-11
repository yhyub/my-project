#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek本地部署主脚本
功能：
1. 检查并安装Git
2. 克隆DeepSeek相关仓库
3. 安装项目依赖
4. 下载预训练模型
5. 启动本地API服务
"""

import os
import sys
import subprocess
import shutil
from git import Repo

def check_git_installed():
    """检查Git是否已安装"""
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        print("✓ Git已安装")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Git未安装，正在尝试安装...")
        return install_git()

def install_git():
    """安装Git"""
    if sys.platform.startswith('win'):
        print("请手动下载并安装Git：https://git-scm.com/download/win")
        return False
    elif sys.platform.startswith('linux'):
        try:
            if os.path.exists('/etc/debian_version'):
                # Debian/Ubuntu
                subprocess.run(["sudo", "apt-get", "update"], check=True)
                subprocess.run(["sudo", "apt-get", "install", "-y", "git"], check=True)
            elif os.path.exists('/etc/centos-release'):
                # CentOS
                subprocess.run(["sudo", "yum", "install", "-y", "git"], check=True)
            print("✓ Git安装成功")
            return True
        except subprocess.CalledProcessError:
            print("✗ Git安装失败，请手动安装")
            return False
    elif sys.platform.startswith('darwin'):
        try:
            subprocess.run(["brew", "install", "git"], check=True)
            print("✓ Git安装成功")
            return True
        except subprocess.CalledProcessError:
            print("✗ Git安装失败，请先安装Homebrew或手动安装Git")
            return False
    return False

def clone_repository(repo_url, target_dir):
    """克隆Git仓库"""
    if os.path.exists(target_dir):
        print(f"✓ 仓库已存在：{target_dir}")
        return True
    
    try:
        print(f"正在克隆仓库：{repo_url} (浅克隆模式)")
        # 使用浅克隆加速下载，只获取最新commit
        Repo.clone_from(repo_url, target_dir, depth=1)
        print(f"✓ 仓库克隆成功：{target_dir}")
        return True
    except Exception as e:
        print(f"✗ 浅克隆失败，尝试完整克隆：{e}")
        # 浅克隆失败时，尝试完整克隆
        try:
            Repo.clone_from(repo_url, target_dir)
            print(f"✓ 完整克隆成功：{target_dir}")
            return True
        except Exception as full_error:
            print(f"✗ 完整克隆也失败：{full_error}")
            return False

def install_dependencies(requirements_file="requirements.txt"):
    """安装Python依赖"""
    try:
        print("正在安装依赖...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_file], check=True)
        print("✓ 依赖安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 依赖安装失败：{e}")
        return False

def download_deepseek_model(model_name="deepseek-r1-7b", save_dir="./models"):
    """下载DeepSeek预训练模型"""
    import os
    import sys
    import time
    
    os.makedirs(save_dir, exist_ok=True)
    
    print(f"正在下载模型：{model_name}")
    print("注意：如果遇到网络连接问题，可尝试以下解决方案：")
    print("1. 检查网络连接")
    print("2. 使用科学上网工具")
    print("3. 手动下载模型文件并放置到models目录")
    print("4. 选择使用Ollama部署方式")
    print("\n模型下载地址：")
    print(f"https://huggingface.co/deepseek-ai/{model_name}")
    print("\n正在尝试连接...")
    
    try:
        # 添加网络超时配置
        import requests
        from huggingface_hub import configure_http_backend
        
        # 配置更长的超时时间
        session = requests.Session()
        session.timeout = 30  # 30秒超时
        configure_http_backend(backend="huggingface_hub.transport.requests.RequestsTransport", session=session)
        
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        # 加载并保存模型
        model = AutoModelForCausalLM.from_pretrained(
            f"deepseek-ai/{model_name}",
            torch_dtype="auto",
            trust_remote_code=True,
            timeout=30,  # 30秒超时
            resume_download=True,  # 支持断点续传
            use_auth_token=None  # 不使用认证token
        )
        
        tokenizer = AutoTokenizer.from_pretrained(
            f"deepseek-ai/{model_name}",
            trust_remote_code=True,
            timeout=30,
            resume_download=True
        )
        
        # 保存到本地
        model.save_pretrained(save_dir)
        tokenizer.save_pretrained(save_dir)
        
        print(f"✓ 模型下载成功：{save_dir}")
        return True
    except requests.exceptions.Timeout:
        print("✗ 网络超时，无法连接到Hugging Face")
        print("建议：")
        print("- 检查网络连接是否稳定")
        print("- 增加超时时间")
        print("- 尝试手动下载模型")
        return False
    except requests.exceptions.ConnectionError:
        print("✗ 网络连接错误，无法访问Hugging Face")
        print("建议：")
        print("- 检查网络连接")
        print("- 尝试使用代理")
        print("- 选择Ollama部署方式")
        return False
    except Exception as e:
        print(f"✗ 模型下载失败：{e}")
        print("\n错误类型：{type(e).__name__}")
        print("\n建议尝试Ollama部署方式，或手动下载模型文件")
        return False

def setup_ollama_deepseek():
    """使用Ollama设置DeepSeek模型"""
    try:
        print("检查Ollama是否已安装...")
        subprocess.run(["ollama", "--version"], check=True, capture_output=True)
        
        print("正在拉取DeepSeek-R1模型...")
        subprocess.run(["ollama", "pull", "deepseek-r1"], check=True)
        
        print("✓ Ollama DeepSeek设置成功")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Ollama未安装或拉取失败")
        print("请先安装Ollama：https://ollama.com/download")
        return False

def create_api_server():
    """创建API服务器文件"""
    api_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek本地API服务器
"""

from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = FastAPI(title="DeepSeek Local API", version="1.0")

# 加载模型
model_path = "./models"
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype=torch.float16,
    trust_remote_code=True
).to("cuda" if torch.cuda.is_available() else "cpu")

class CompletionRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 512
    temperature: float = 0.7

@app.post("/v1/completions")
async def create_completion(request: CompletionRequest):
    """生成文本完成"""
    inputs = tokenizer(request.prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=request.max_new_tokens,
        temperature=request.temperature,
        do_sample=True
    )
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return {
        "id": "cmpl-123",
        "object": "text_completion",
        "created": 1627044000,
        "model": "deepseek-r1",
        "choices": [{"text": text, "index": 0, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": len(inputs["input_ids"][0]), "completion_tokens": len(outputs[0]) - len(inputs["input_ids"][0]), "total_tokens": len(outputs[0])}
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "model": "deepseek-r1"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    with open("api_server.py", "w", encoding="utf-8") as f:
        f.write(api_code)
    print("✓ API服务器文件已创建：api_server.py")

def main():
    """主函数"""
    print("=" * 60)
    print("DeepSeek本地部署工具")
    print("=" * 60)
    
    # 1. 检查Git
    if not check_git_installed():
        return
    
    # 2. 克隆核心仓库
    core_repos = [
        ("https://github.com/deepseek-ai/DeepSeek-R1.git", "DeepSeek-R1"),
        ("https://github.com/deepseek-ai/awesome-deepseek-integration.git", "awesome-deepseek-integration")
    ]
    
    for repo_url, target_dir in core_repos:
        clone_repository(repo_url, target_dir)
    
    # 3. 安装依赖
    install_dependencies()
    
    # 4. 下载模型选项
    print("\n模型部署选项：")
    print("1. 使用Transformers直接下载DeepSeek模型")
    print("2. 使用Ollama部署DeepSeek模型")
    print("3. 跳过模型下载（手动部署）")
    
    choice = input("请选择部署方式（1-3）：").strip()
    
    if choice == "1":
        model_size = input("请选择模型大小（1.5b/7b/8b/14b/32b/70b）：").strip().lower()
        model_name = f"deepseek-r1-{model_size}"
        download_deepseek_model(model_name)
        create_api_server()
    elif choice == "2":
        setup_ollama_deepseek()
    else:
        print("跳过模型下载")
    
    print("\n" + "=" * 60)
    print("DeepSeek本地部署完成！")
    print("=" * 60)
    print("使用说明：")
    
    # 集成工具说明（无论模型是否下载成功，都可以使用）
    print("\n4. 查看集成工具：")
    print("   awesome-deepseek-integration仓库包含80+个DeepSeek集成工具")
    print("   目录：awesome-deepseek-integration/")
    print("   工具类型：")
    print("   - 代码生成工具")
    print("   - 自动化办公工具")
    print("   - AI助理")
    print("   - 跨平台开发工具")
    print("   - 知识库系统")
    print("   - IDE插件")
    print("   - 浏览器扩展")
    print("   - 移动应用")
    
    # 模型相关说明（仅当模型下载成功时可用）
    if os.path.exists("./models") and len(os.listdir("./models")) > 0:
        print("\n1. 直接使用Transformers：")
        print("   python -c \"from transformers import AutoModelForCausalLM, AutoTokenizer; tokenizer = AutoTokenizer.from_pretrained('./models'); model = AutoModelForCausalLM.from_pretrained('./models'); print(tokenizer.decode(model.generate(**tokenizer('你好', return_tensors='pt'))[0]))\"")
        print("\n2. 启动API服务：")
        print("   python api_server.py")
        print("   访问 http://localhost:8000/docs 查看API文档")
    
    print("\n3. 使用Ollama：")
    print("   ollama run deepseek-r1 '你好'")
    
    # 网络问题解决方案
    print("\n5. 常见问题解决方案：")
    print("   - 网络连接问题：检查网络或使用科学上网")
    print("   - 模型下载失败：手动下载模型到models目录")
    print("   - Ollama未安装：访问 https://ollama.com/download 下载")
    print("   - Git克隆失败：手动下载仓库压缩包")
    
    # 手动下载链接
    print("\n6. 手动下载链接：")
    print("   awesome-deepseek-integration仓库：")
    print("   https://github.com/deepseek-ai/awesome-deepseek-integration/archive/refs/heads/main.zip")
    print("   ")
    print("   DeepSeek-R1模型：")
    print("   https://huggingface.co/deepseek-ai/deepseek-r1-7b")

if __name__ == "__main__":
    main()
