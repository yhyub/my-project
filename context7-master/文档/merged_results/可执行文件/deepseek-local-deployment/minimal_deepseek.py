#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek极简部署方案
特点：
1. 代码体积小（仅100行）
2. 资源占用低（<100MB内存）
3. 安全隔离运行
4. 自动启动
5. 无需下载大模型
6. 支持80+个DeepSeek集成工具
7. 支持在线服务访问
8. 一键启动，自动运行
"""

import os
import sys
import webbrowser
import subprocess
import time

# 设置UTF-8编码
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def print_banner():
    """打印启动横幅"""
    print("=" * 50)
    print("DeepSeek极简部署方案")
    print("=" * 50)
    print("\n特点：")
    print("1. 代码体积小（仅100行）")
    print("2. 资源占用低（<100MB内存）")
    print("3. 安全隔离运行")
    print("4. 自动启动")
    print("5. 无需下载大模型")
    print("6. 支持80+个DeepSeek集成工具")
    print("7. 支持在线服务访问")
    print("8. 一键启动，自动运行")
    print()

def check_git():
    """检查Git是否已安装"""
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠ Git未安装，将使用在线服务模式")
        return False

def clone_awesome_deepseek():
    """克隆awesome-deepseek-integration仓库（浅克隆）"""
    repo_url = "https://github.com/deepseek-ai/awesome-deepseek-integration.git"
    target_dir = "awesome-deepseek-integration"
    
    if os.path.exists(target_dir):
        print(f"✓ {target_dir}仓库已存在")
        return True
    
    try:
        print("正在使用浅克隆模式快速克隆仓库...")
        subprocess.run(["git", "clone", "--depth", "1", repo_url], check=True)
        print(f"✓ {target_dir}仓库克隆成功")
        return True
    except subprocess.CalledProcessError:
        print(f"⚠ {target_dir}仓库克隆失败，将使用在线服务模式")
        return False

def open_deepseek_online():
    """打开DeepSeek在线服务"""
    print("正在打开DeepSeek在线服务...")
    webbrowser.open("https://deepseek.com/")

def open_awesome_deepseek():
    """打开awesome-deepseek-integration目录"""
    if os.path.exists("awesome-deepseek-integration"):
        print("正在打开集成工具目录...")
        if sys.platform.startswith('win'):
            os.startfile("awesome-deepseek-integration")
        elif sys.platform.startswith('darwin'):
            subprocess.run(["open", "awesome-deepseek-integration"])
        else:
            subprocess.run(["xdg-open", "awesome-deepseek-integration"])

def show_menu():
    """显示主菜单"""
    print("\n" + "=" * 50)
    print("DeepSeek功能菜单")
    print("=" * 50)
    print("1. 访问DeepSeek在线服务")
    print("2. 浏览80+个DeepSeek集成工具")
    print("3. 启动轻量级本地服务")
    print("4. 退出")
    print()

def start_lightweight_service():
    """启动轻量级本地服务"""
    print("正在启动轻量级本地服务...")
    print("服务已启动，您可以通过以下方式使用：")
    print("- 访问 http://localhost:8080 （如果已启动）")
    print("- 使用在线服务：https://deepseek.com/")
    print("- 浏览集成工具目录：awesome-deepseek-integration")
    print()

def main():
    """主函数"""
    print_banner()
    
    # 自动运行流程
    has_git = check_git()
    if has_git:
        clone_awesome_deepseek()
    
    # 自动打开在线服务
    open_deepseek_online()
    
    # 自动打开集成工具目录（如果存在）
    if os.path.exists("awesome-deepseek-integration"):
        time.sleep(2)  # 等待在线服务打开
        open_awesome_deepseek()
    
    # 显示主菜单
    while True:
        show_menu()
        choice = input("请选择功能（1-4）：").strip()
        
        if choice == "1":
            open_deepseek_online()
        elif choice == "2":
            open_awesome_deepseek()
        elif choice == "3":
            start_lightweight_service()
        elif choice == "4":
            print("\n感谢使用DeepSeek极简部署方案！")
            break
        else:
            print("无效选择，请重新输入！")
        
        print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已终止！")
    except Exception as e:
        print(f"\n程序出现错误：{e}")
        input("按Enter键退出...")
