#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek快捷启动脚本
用于修复在coze-studio-0.5.0目录运行minimal_deepseek.py的错误
"""

import os
import sys
import subprocess

# 设置UTF-8编码
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def main():
    """主函数"""
    # 定义正确的脚本路径
    correct_script_path = r"C:\Users\Administrator\Desktop\可执行文件\deepseek-local-deployment\minimal_deepseek.py"
    
    # 检查脚本是否存在
    if not os.path.exists(correct_script_path):
        print(f"错误：脚本文件不存在：{correct_script_path}")
        print("请检查deepseek-local-deployment目录是否存在")
        input("按Enter键退出...")
        return 1
    
    # 运行正确的脚本
    print(f"正在运行DeepSeek极简部署方案...")
    print(f"脚本路径：{correct_script_path}")
    print()
    
    try:
        # 使用subprocess运行脚本
        subprocess.run([sys.executable, correct_script_path], check=True)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"脚本运行失败：{e}")
        input("按Enter键退出...")
        return e.returncode
    except KeyboardInterrupt:
        print("\n脚本已中断")
        input("按Enter键退出...")
        return 0

if __name__ == "__main__":
    sys.exit(main())
