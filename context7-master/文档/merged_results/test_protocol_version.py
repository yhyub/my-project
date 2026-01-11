#!/usr/bin/env python3
"""
测试protocolVersion参数处理
"""

import subprocess
import json
import sys

def test_initialize_request(params):
    """测试initialize请求"""
    # 创建请求JSON
    request = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "id": 1,
        "params": params
    }
    
    # 运行mcp_server.py并发送请求
    process = subprocess.Popen(
        [sys.executable, "mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # 发送请求
    process.stdin.write(json.dumps(request) + "\n")
    process.stdin.flush()
    
    # 读取响应
    response = process.stdout.readline()
    process.terminate()
    
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response", "raw_response": response}

def main():
    """主函数"""
    print("=== 测试protocolVersion参数处理 ===")
    
    # 测试1: 缺少protocolVersion参数（应该返回错误）
    print("\n1. 测试缺少protocolVersion参数:")
    response1 = test_initialize_request({})
    print(f"响应: {json.dumps(response1, indent=2, ensure_ascii=False)}")
    
    # 测试2: 无效的protocolVersion参数（应该返回错误）
    print("\n2. 测试无效的protocolVersion参数:")
    response2 = test_initialize_request({"protocolVersion": "invalid-version"})
    print(f"响应: {json.dumps(response2, indent=2, ensure_ascii=False)}")
    
    # 测试3: 有效的protocolVersion参数（应该返回成功）
    print("\n3. 测试有效的protocolVersion参数:")
    response3 = test_initialize_request({"protocolVersion": "2025-06-18"})
    print(f"响应: {json.dumps(response3, indent=2, ensure_ascii=False)}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()