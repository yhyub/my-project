#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整多模态DeepSeek本地API服务器
支持使用Hugging Face Transformers运行DeepSeek-R1和中文CLIP模型
实现完整的OpenAI兼容API端点
"""

from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import time
import torch
from transformers import (
    AutoModelForCausalLM, AutoTokenizer,
    CLIPProcessor, CLIPModel
)
from PIL import Image
import io
from fastapi.responses import StreamingResponse

app = FastAPI(title="Complete Multimodal DeepSeek Local API", version="1.0")

# 文本生成模型配置
TEXT_MODEL_CONFIG = {
    "model_path": "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "dtype": torch.float16,
    "trust_remote_code": True,
    "device_map": "auto"
}

# 中文CLIP模型配置
CLIP_MODEL_CONFIG = {
    "model_path": "OFA-Sys/chinese-clip-vit-base-patch16",
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "dtype": torch.float16
}

# 全局模型变量
text_model = None
text_tokenizer = None
clip_model = None
clip_processor = None

# 请求模型定义
class CompletionRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 512
    temperature: float = 0.6
    top_p: float = 0.95
    stop: Optional[List[str]] = None

class ChatCompletionRequest(BaseModel):
    messages: List[Dict[str, str]]
    max_new_tokens: int = 512
    temperature: float = 0.6
    top_p: float = 0.95
    stop: Optional[List[str]] = None
    stream: bool = False

class EmbeddingRequest(BaseModel):
    input: List[str]
    model: str = "deepseek-r1"

class CodeCompletionRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 1024
    temperature: float = 0.2
    top_p: float = 0.95
    stop: Optional[List[str]] = None

@app.on_event("startup")
async def load_models():
    """在API启动时加载所有模型"""
    global text_model, text_tokenizer, clip_model, clip_processor

# 加载文本生成模型
    print("正在加载DeepSeek-R1-Distill-Qwen-32B模型...")
    start_time = time.time()
    try:
        text_tokenizer = AutoTokenizer.from_pretrained(
            TEXT_MODEL_CONFIG["model_path"],
            trust_remote_code=TEXT_MODEL_CONFIG["trust_remote_code"]
        )
        text_model = AutoModelForCausalLM.from_pretrained(
            TEXT_MODEL_CONFIG["model_path"],
            torch_dtype=TEXT_MODEL_CONFIG["dtype"],
            trust_remote_code=TEXT_MODEL_CONFIG["trust_remote_code"],
            device_map=TEXT_MODEL_CONFIG["device_map"]
        )
        text_model.eval()
        end_time = time.time()
        print(f"文本模型加载完成，耗时: {end_time - start_time:.2f}秒")
    except Exception as e:
        print(f"文本模型加载失败: {e}")
        raise e

# 加载中文CLIP模型
    print("\n正在加载中文CLIP模型...")
    start_time = time.time()
    try:
        clip_processor = CLIPProcessor.from_pretrained(CLIP_MODEL_CONFIG["model_path"])
        clip_model = CLIPModel.from_pretrained(CLIP_MODEL_CONFIG["model_path"])
        clip_model.to(CLIP_MODEL_CONFIG["device"])
        clip_model.eval()
        end_time = time.time()
        print(f"CLIP模型加载完成，耗时: {end_time - start_time:.2f}秒")
    except Exception as e:
        print(f"CLIP模型加载失败: {e}")
        raise e

@app.post("/v1/completions")
async def create_completion(request: CompletionRequest):
    """生成文本完成"""
    global text_model, text_tokenizer

try:
        if text_model is None or text_tokenizer is None:
            return {
                "id": "cmpl-123",
                "object": "text_completion",
                "created": int(time.time()),
                "model": "deepseek-r1",
                "choices": [{"text": "文本模型尚未加载完成，请稍后再试", "index": 0, "finish_reason": "error"}],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            }

# 确保模型使用推荐的格式：以<think>开头
        formatted_prompt = f"<think>\n{request.prompt}"

# 编码输入
        inputs = text_tokenizer(formatted_prompt, return_tensors="pt").to(TEXT_MODEL_CONFIG["device"])
        prompt_tokens = len(inputs["input_ids"][0])

print(f"正在生成文本，输入长度: {prompt_tokens} tokens")
        start_time = time.time()

# 生成文本
        with torch.no_grad():
            outputs = text_model.generate(
                **inputs,
                max_new_tokens=request.max_new_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                do_sample=True,
                stop=request.stop
            )

end_time = time.time()

# 解码输出
        generated_text = text_tokenizer.decode(outputs[0], skip_special_tokens=True)
        completion_tokens = len(outputs[0]) - prompt_tokens
        total_tokens = len(outputs[0])

print(f"文本生成完成，耗时: {end_time - start_time:.2f}秒")
        print(f"生成长度: {completion_tokens} tokens")

return {
            "id": "cmpl-123",
            "object": "text_completion",
            "created": int(time.time()),
            "model": "deepseek-r1",
            "choices": [{"text": generated_text, "index": 0, "finish_reason": "stop"}],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens
            }
        }
    except Exception as e:
        print(f"生成文本时出错: {e}")
        return {
            "id": "cmpl-123",
            "object": "text_completion",
            "created": int(time.time()),
            "model": "deepseek-r1",
            "choices": [{"text": f"Error: {str(e)}", "index": 0, "finish_reason": "error"}],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        }

@app.post("/v1/chat/completions")
async def create_chat_completion(request: ChatCompletionRequest):
    """多轮对话生成"""
    global text_model, text_tokenizer

try:
        if text_model is None or text_tokenizer is None:
            return {
                "id": "chatcmpl-123",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "deepseek-r1",
                "choices": [{"message": {"role": "assistant", "content": "文本模型尚未加载完成，请稍后再试"}, "index": 0, "finish_reason": "error"}],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            }

# 构建对话历史
        conversation = ""
        for msg in request.messages:
            if msg["role"] == "system":
                conversation += f"<system>\n{msg['content']}\n"
            elif msg["role"] == "user":
                conversation += f"<user>\n{msg['content']}\n"
            elif msg["role"] == "assistant":
                conversation += f"<assistant>\n{msg['content']}\n"

# 添加思考前缀和助手前缀
        formatted_prompt = f"<think>\n{conversation}<assistant>\n"

print(f"正在生成对话，输入长度: {prompt_tokens} tokens")
        start_time = time.time()

# 解码输出
        generated_text = text_tokenizer.decode(outputs[0], skip_special_tokens=True)
        # 提取助手回复（去除对话历史）
        assistant_response = generated_text.split("<assistant>\n")[-1]
        completion_tokens = len(outputs[0]) - prompt_tokens
        total_tokens = len(outputs[0])

print(f"对话生成完成，耗时: {end_time - start_time:.2f}秒")
        print(f"生成长度: {completion_tokens} tokens")

# 流式输出处理
        if request.stream:
            def stream_generator():
                yield f"data: {str({'id': 'chatcmpl-123', 'object': 'chat.completion.chunk', 'created': int(time.time()), 'model': 'deepseek-r1', 'choices': [{'index': 0, 'delta': {'role': 'assistant'}, 'finish_reason': None}]})}\n\n"
                for char in assistant_response:
                    yield f"data: {str({'id': 'chatcmpl-123', 'object': 'chat.completion.chunk', 'created': int(time.time()), 'model': 'deepseek-r1', 'choices': [{'index': 0, 'delta': {'content': char}, 'finish_reason': None}]})}\n\n"
                yield f"data: {str({'id': 'chatcmpl-123', 'object': 'chat.completion.chunk', 'created': int(time.time()), 'model': 'deepseek-r1', 'choices': [{'index': 0, 'delta': {}, 'finish_reason': 'stop'}]})}\n\n"
                yield "data: [DONE]\n\n"

return StreamingResponse(stream_generator(), media_type="text/event-stream")
        else:
            # 非流式输出
            return {
                "id": "chatcmpl-123",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "deepseek-r1",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": assistant_response
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens
                }
            }
    except Exception as e:
        print(f"生成对话时出错: {e}")
        return {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "deepseek-r1",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": f"Error: {str(e)}"
                },
                "finish_reason": "error"
            }],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        }

@app.post("/v1/code/completions")
async def create_code_completion(request: CodeCompletionRequest):
    """代码生成"""
    global text_model, text_tokenizer

try:
        if text_model is None or text_tokenizer is None:
            return {
                "id": "cmpl-123",
                "object": "text_completion",
                "created": int(time.time()),
                "model": "deepseek-r1-code",
                "choices": [{"text": "文本模型尚未加载完成，请稍后再试", "index": 0, "finish_reason": "error"}],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            }

# 代码生成优化：添加代码上下文提示
        formatted_prompt = f"<think>\n请生成高效、安全、可读性强的代码，确保代码能直接运行。\n\n{request.prompt}"

print(f"正在生成代码，输入长度: {prompt_tokens} tokens")
        start_time = time.time()

# 代码生成优化：使用较低温度和较高top_p
        with torch.no_grad():
            outputs = text_model.generate(
                **inputs,
                max_new_tokens=request.max_new_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                do_sample=True,
                stop=request.stop
            )

# 解码输出
        generated_code = text_tokenizer.decode(outputs[0], skip_special_tokens=True)
        completion_tokens = len(outputs[0]) - prompt_tokens
        total_tokens = len(outputs[0])

print(f"代码生成完成，耗时: {end_time - start_time:.2f}秒")
        print(f"生成长度: {completion_tokens} tokens")

return {
            "id": "cmpl-123",
            "object": "text_completion",
            "created": int(time.time()),
            "model": "deepseek-r1-code",
            "choices": [{"text": generated_code, "index": 0, "finish_reason": "stop"}],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens
            }
        }
    except Exception as e:
        print(f"生成代码时出错: {e}")
        return {
            "id": "cmpl-123",
            "object": "text_completion",
            "created": int(time.time()),
            "model": "deepseek-r1-code",
            "choices": [{"text": f"Error: {str(e)}", "index": 0, "finish_reason": "error"}],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        }

@app.post("/v1/clip/text-to-image-similarity")
async def text_to_image_similarity(text: str, file: UploadFile = File(...)):
    """文本-图像相似度计算"""
    global clip_model, clip_processor

try:
        if clip_model is None or clip_processor is None:
            return {
                "status": "error",
                "message": "CLIP模型尚未加载完成，请稍后再试"
            }

# 处理图像
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))

# 准备输入
        inputs = clip_processor(
            text=[text],
            images=image,
            return_tensors="pt",
            padding=True
        ).to(CLIP_MODEL_CONFIG["device"])

# 计算相似度
        with torch.no_grad():
            outputs = clip_model(**inputs)
            logits_per_image = outputs.logits_per_image  # 图像到文本的相似度
            probs = logits_per_image.softmax(dim=1)  # 转换为概率

similarity_score = probs[0][0].item()

return {
            "status": "ok",
            "text": text,
            "similarity_score": similarity_score,
            "model": "chinese-clip-vit-base-patch16"
        }
    except Exception as e:
        print(f"计算文本-图像相似度时出错: {e}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

@app.get("/health")
async def health_check():
    """健康检查"""
    global text_model, text_tokenizer, clip_model, clip_processor

text_model_healthy = text_model is not None and text_tokenizer is not None
    clip_model_healthy = clip_model is not None and clip_processor is not None

return {
        "status": "ok" if (text_model_healthy and clip_model_healthy) else "error",
        "text_model": "deepseek-r1" if text_model_healthy else "not loaded",
        "clip_model": "chinese-clip-vit-base-patch16" if clip_model_healthy else "not loaded",
        "message": "完整多模态DeepSeek API服务器运行正常" if (text_model_healthy and clip_model_healthy) else "部分模型尚未加载",
        "text_model_path": TEXT_MODEL_CONFIG["model_path"],
        "clip_model_path": CLIP_MODEL_CONFIG["model_path"],
        "device": TEXT_MODEL_CONFIG["device"]
    }

@app.get("/v1/models")
async def list_models():
    """列出可用模型"""
    return {
        "object": "list",
        "data": [
            {
                "id": "deepseek-r1",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "deepseek-ai",
                "root": TEXT_MODEL_CONFIG["model_path"],
                "parent": None,
                "permission": []
            },
            {
                "id": "deepseek-r1-code",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "deepseek-ai",
                "root": TEXT_MODEL_CONFIG["model_path"],
                "parent": None,
                "permission": []
            },
            {
                "id": "chinese-clip-vit-base-patch16",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "OFA-Sys",
                "root": CLIP_MODEL_CONFIG["model_path"],
                "parent": None,
                "permission": []
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("启动完整多模态DeepSeek API服务器...")
    print("访问 http://localhost:8000/docs 查看API文档")
    print("使用POST /v1/completions 端点进行文本生成")
    print("使用POST /v1/chat/completions 端点进行多轮对话")
    print("使用POST /v1/code/completions 端点进行代码生成")
    print("使用POST /v1/clip/text-to-image-similarity 端点进行文本-图像相似度计算")
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=1)