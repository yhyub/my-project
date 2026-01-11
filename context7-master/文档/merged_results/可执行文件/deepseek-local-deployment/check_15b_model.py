#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查DeepSeek-R1 1.5B模型的可用性
"""

from transformers import AutoTokenizer

def check_15b_model():
    """检查1.5B模型是否可用"""
    print("Checking 1.5B model availability...")
    
    try:
        # 测试1.5B模型的tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            'deepseek-ai/deepseek-r1-1.5b',
            trust_remote_code=True
        )
        print("Success: 1.5B model is available!")
        return True
    except Exception as e:
        print(f"Error: {e}")
        print("\nPossible reasons:")
        print("1. Network connection issue")
        print("2. Model name is incorrect")
        print("3. Hugging Face API is down")
        return False

if __name__ == "__main__":
    check_15b_model()
