#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的DeepSeek模型部署脚本
使用现有的transformers库直接部署DeepSeek模型
无需额外依赖，支持DeepSeek-V3.2和DeepSeek-R1模型
"""

import os
import sys
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch


def check_transformers_version():
    """检查transformers版本"""
    import transformers
    version = transformers.__version__
    print(f"✓ Transformers版本: {version}")
    if int(version.split('.')[0]) < 4 or (int(version.split('.')[0]) == 4 and int(version.split('.')[1]) < 40):
        print("⚠️  建议升级transformers到4.40+以获得更好的DeepSeek支持")
    return version


def download_model(model_name, save_path="./models"):
    """下载DeepSeek模型"""
    print(f"\n开始下载模型: {model_name}")
    print(f"保存路径: {save_path}")
    
    # 创建保存目录
    os.makedirs(save_path, exist_ok=True)
    
    try:
        # 下载tokenizer
        print("1. 下载Tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        tokenizer.save_pretrained(save_path)
        print("✓ Tokenizer下载成功")
        
        # 下载模型
        print("2. 下载模型...")
        print("注意：模型可能较大，下载时间较长")
        
        # 根据设备选择合适的精度
        if torch.cuda.is_available():
            print("使用GPU加速下载和推理")
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
        else:
            print("使用CPU下载和推理")
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float32,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
        
        # 保存模型
        model.save_pretrained(save_path)
        print("✓ 模型下载成功")
        
        return True
    except Exception as e:
        print(f"✗ 模型下载失败: {e}")
        print("建议检查网络连接，或尝试使用Ollama部署方式")
        return False


def load_model(model_path="./models"):
    """加载已下载的模型"""
    print(f"\n加载模型: {model_path}")
    
    try:
        # 加载tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        print("✓ Tokenizer加载成功")
        
        # 加载模型
        if torch.cuda.is_available():
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            ).to("cuda")
            print("✓ 模型加载成功 (GPU)")
        else:
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float32,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            ).to("cpu")
            print("✓ 模型加载成功 (CPU)")
        
        return model, tokenizer
    except Exception as e:
        print(f"✗ 模型加载失败: {e}")
        return None, None


def test_model_inference(model, tokenizer, prompt="你好，介绍一下自己"):
    """测试模型推理"""
    print(f"\n测试模型推理")
    print(f"提示词: {prompt}")
    
    try:
        # 生成文本
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        outputs = model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.7,
            do_sample=True,
            top_p=0.9
        )
        
        # 解码输出
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        print(f"✓ 推理成功")
        print(f"模型响应:")
        print(response)
        
        return response
    except Exception as e:
        print(f"✗ 推理失败: {e}")
        return None


def create_simple_api_server(model_path="./models"):
    """创建简单的API服务器"""
    api_code = f'''#!/usr/bin/env python3
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
print("正在加载模型...")
tokenizer = AutoTokenizer.from_pretrained("{model_path}", trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    "{model_path}",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    trust_remote_code=True
).to("cuda" if torch.cuda.is_available() else "cpu")
print("模型加载完成")

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
        "model": "deepseek-v3.2",
        "choices": [{"text": text, "index": 0, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": len(inputs["input_ids"][0]), "completion_tokens": len(outputs[0]) - len(inputs["input_ids"][0]), "total_tokens": len(outputs[0])}
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "model": "deepseek-v3.2"}

@app.get("/")
async def root():
    """根路径"""
    return {"message": "DeepSeek Local API is running", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
'''
    
    with open("simple_api_server.py", "w", encoding="utf-8") as f:
        f.write(api_code)
    
    print("\n✓ 简单API服务器已创建: simple_api_server.py")
    print("使用方法:")
    print("  python simple_api_server.py")
    print("  访问 http://127.0.0.1:8000/docs 查看API文档")


def main():
    """主函数"""
    print("=" * 60)
    print("DeepSeek模型部署工具")
    print("=" * 60)
    print("支持DeepSeek-V3.2和DeepSeek-R1模型部署")
    print("=" * 60)
    
    # 检查transformers版本
    check_transformers_version()
    
    # 模型选择
    print("\n模型选择:")
    print("1. DeepSeek-V3.2 (主要使用的模型)")
    print("2. DeepSeek-R1 (兼容模型)")
    print("3. 退出")
    
    while True:
        choice = input("请选择模型 (1-3): ").strip()
        
        if choice == "1":
            model_name = "deepseek-ai/deepseek-v3"
            save_path = "./models/deepseek-v3.2"
            break
        elif choice == "2":
            model_name = "deepseek-ai/deepseek-r1"
            save_path = "./models/deepseek-r1"
            break
        elif choice == "3":
            print("退出部署工具")
            return
        else:
            print("无效选择，请重新输入")
    
    # 下载模型
    if download_model(model_name, save_path):
        # 加载模型
        model, tokenizer = load_model(save_path)
        if model and tokenizer:
            # 测试模型
            test_model_inference(model, tokenizer)
            
            # 创建API服务器
            create_simple_api_server(save_path)
            
            print("\n" + "=" * 60)
            print("部署完成！")
            print("=" * 60)
            print("使用说明:")
            print(f"1. 直接使用模型:")
            print(f"   python -c \"from transformers import AutoModelForCausalLM, AutoTokenizer; tokenizer = AutoTokenizer.from_pretrained('{save_path}', trust_remote_code=True); model = AutoModelForCausalLM.from_pretrained('{save_path}', trust_remote_code=True, torch_dtype=torch.float16).to('cuda'); print(tokenizer.decode(model.generate(**tokenizer('你好', return_tensors='pt').to('cuda'))[0], skip_special_tokens=True)\"")
            print("\n2. 启动API服务:")
            print("   python simple_api_server.py")
            print("   访问 http://127.0.0.1:8000/docs 查看API文档")
            print("\n3. 测试API:")
            print("   curl http://127.0.0.1:8000/v1/completions -H 'Content-Type: application/json' -d '{\"prompt\": \"你好\"}'")


if __name__ == "__main__":
    main()
