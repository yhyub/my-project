#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豆包seed-1.6模型与DeepSeek集成实现
功能：
1. 支持豆包seed-1.6模型API调用
2. 与DeepSeek框架集成
3. 提供统一的模型调用接口
4. 支持多种模型变体（base/thinking/flash）
"""

import requests
import json
import os
import sys

# 设置UTF-8编码
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

class DoubaoSeed16Integration:
    """豆包seed-1.6模型集成类"""
    
    def __init__(self, api_key=None, model="doubao-seed-1-6"):
        """初始化豆包API集成
        
        Args:
            api_key: 豆包API密钥
            model: 模型名称，可选值：
                - doubao-seed-1-6 (基础版)
                - doubao-seed-1-6-thinking (思考版)
                - doubao-seed-1-6-flash (快速版)
        """
        self.api_key = api_key or os.environ.get("DOBAO_API_KEY")
        self.model = model
        self.base_url = "https://api.doubao.com/v1/chat/completions"
        
        if not self.api_key:
            raise ValueError("API密钥不能为空，请提供api_key参数或设置DOBAO_API_KEY环境变量")
        
    def generate(self, prompt, max_tokens=1024, temperature=0.7, top_p=0.95):
        """调用豆包seed-1.6模型生成文本
        
        Args:
            prompt: 提示词
            max_tokens: 最大生成 tokens 数
            temperature: 温度参数
            top_p: top_p 参数
        
        Returns:
            生成的文本结果
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [{
                "role": "user",
                "content": prompt
            }],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            print(f"API调用失败：{e}")
            return None
        except KeyError as e:
            print(f"API响应格式错误：{e}")
            return None
    
    def compare_with_deepseek(self, prompt):
        """对比豆包seed-1.6和DeepSeek模型的生成结果
        
        Args:
            prompt: 提示词
            
        Returns:
            包含两个模型生成结果的字典
        """
        # 调用豆包seed-1.6模型
        doubao_result = self.generate(prompt)
        
        # 调用DeepSeek模型（如果可用）
        deepseek_result = None
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            # 加载DeepSeek模型
            tokenizer = AutoTokenizer.from_pretrained("./models" if os.path.exists("./models") else "deepseek-ai/DeepSeek-R1")
            model = AutoModelForCausalLM.from_pretrained(
                "./models" if os.path.exists("./models") else "deepseek-ai/DeepSeek-R1",
                trust_remote_code=True
            )
            
            # 生成文本
            inputs = tokenizer(prompt, return_tensors="pt")
            outputs = model.generate(**inputs, max_new_tokens=1024)
            deepseek_result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        except Exception as e:
            print(f"DeepSeek模型调用失败：{e}")
            deepseek_result = "DeepSeek模型不可用"
        
        return {
            "prompt": prompt,
            "doubao_result": doubao_result,
            "deepseek_result": deepseek_result
        }

class DeepSeekWithDoubao:
    """DeepSeek与豆包seed-1.6集成的统一接口"""
    
    def __init__(self, doubao_api_key=None):
        """初始化集成接口
        
        Args:
            doubao_api_key: 豆包API密钥
        """
        self.doubao_integration = None
        if doubao_api_key:
            self.doubao_integration = DoubaoSeed16Integration(doubao_api_key)
        
    def generate(self, prompt, model_choice="deepseek", **kwargs):
        """统一生成接口
        
        Args:
            prompt: 提示词
            model_choice: 模型选择，可选值：deepseek/doubao/doubao-thinking/doubao-flash
            **kwargs: 其他参数
            
        Returns:
            生成的文本结果
        """
        if model_choice == "deepseek":
            # 使用DeepSeek模型
            return self._generate_deepseek(prompt, **kwargs)
        else:
            # 使用豆包模型
            if not self.doubao_integration:
                raise ValueError("豆包API密钥未设置，无法使用豆包模型")
            
            # 设置豆包模型变体
            if model_choice == "doubao":
                self.doubao_integration.model = "doubao-seed-1-6"
            elif model_choice == "doubao-thinking":
                self.doubao_integration.model = "doubao-seed-1-6-thinking"
            elif model_choice == "doubao-flash":
                self.doubao_integration.model = "doubao-seed-1-6-flash"
            
            return self.doubao_integration.generate(prompt, **kwargs)
    
    def _generate_deepseek(self, prompt, max_tokens=1024, temperature=0.7):
        """使用DeepSeek模型生成文本
        
        Args:
            prompt: 提示词
            max_tokens: 最大生成 tokens 数
            temperature: 温度参数
            
        Returns:
            生成的文本结果
        """
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            # 加载DeepSeek模型
            model_path = "./models" if os.path.exists("./models") else "deepseek-ai/DeepSeek-R1"
            print(f"正在加载DeepSeek模型：{model_path}")
            
            tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                trust_remote_code=True
            )
            
            # 生成文本
            inputs = tokenizer(prompt, return_tensors="pt")
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature
            )
            
            return tokenizer.decode(outputs[0], skip_special_tokens=True)
        except ImportError:
            print("transformers库未安装，无法使用DeepSeek模型")
            return None
        except Exception as e:
            print(f"DeepSeek模型调用失败：{e}")
            return None

def main():
    """主函数，演示豆包seed-1.6模型与DeepSeek集成使用"""
    print("=" * 60)
    print("豆包seed-1.6模型与DeepSeek集成演示")
    print("=" * 60)
    
    # 获取API密钥（从环境变量或用户输入）
    api_key = os.environ.get("DOBAO_API_KEY")
    if not api_key:
        api_key = input("请输入豆包API密钥：").strip()
        if not api_key:
            print("API密钥不能为空，程序退出")
            return
    
    # 创建集成实例
    integration = DeepSeekWithDoubao(api_key)
    
    # 演示菜单
    while True:
        print("\n演示功能：")
        print("1. 调用豆包seed-1.6基础版模型")
        print("2. 调用豆包seed-1.6思考版模型")
        print("3. 调用豆包seed-1.6快速版模型")
        print("4. 调用DeepSeek模型")
        print("5. 对比豆包和DeepSeek模型")
        print("6. 退出")
        
        choice = input("请选择功能（1-6）：").strip()
        
        if choice == "6":
            break
        
        prompt = input("请输入提示词：").strip()
        if not prompt:
            print("提示词不能为空")
            continue
        
        print("\n正在生成...")
        
        if choice == "1":
            result = integration.generate(prompt, "doubao")
            print(f"\n豆包seed-1.6基础版结果：")
            print(result)
        elif choice == "2":
            result = integration.generate(prompt, "doubao-thinking")
            print(f"\n豆包seed-1.6思考版结果：")
            print(result)
        elif choice == "3":
            result = integration.generate(prompt, "doubao-flash")
            print(f"\n豆包seed-1.6快速版结果：")
            print(result)
        elif choice == "4":
            result = integration.generate(prompt, "deepseek")
            print(f"\nDeepSeek模型结果：")
            print(result)
        elif choice == "5":
            # 直接使用DoubaoSeed16Integration的compare_with_deepseek方法
            doubao_integration = DoubaoSeed16Integration(api_key)
            result = doubao_integration.compare_with_deepseek(prompt)
            
            print(f"\n提示词：{result['prompt']}")
            print(f"\n豆包seed-1.6结果：")
            print(result['doubao_result'])
            print(f"\nDeepSeek结果：")
            print(result['deepseek_result'])
        else:
            print("无效的选择")
    
    print("\n演示结束")

if __name__ == "__main__":
    main()
