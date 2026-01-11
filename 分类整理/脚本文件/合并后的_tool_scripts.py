#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并后的工具脚本
整合了所有工具类脚本功能

功能包括：
1. MCP服务器检查和调试工具
2. JSON修复工具
3. MCP响应修复工具
4. Coze文档获取工具
5. Python NPX工具
6. MCP服务器启动工具
7. 统一MCP管理器
8. 其他实用工具
"""

import json
import os
import sys
import argparse
import logging
import tempfile
import shutil
import time
import subprocess
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional

# 设置日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('merged_tool_scripts.log', encoding='utf-8')
    ]
)
logger = logging.getLogger('MergedToolScripts')

class MCPServerChecker:
    """
    MCP服务器检查工具
    """
    
    def __init__(self, config: dict = None):
        """
        初始化检查工具
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        logger.info("MCP服务器检查工具初始化完成")
    
    def check_mcp_server_path(self) -> Dict[str, Any]:
        """
        检查MCP服务器路径
        
        Returns:
            dict: 检查结果
        """
        logger.info("检查MCP服务器路径...")
        
        try:
            # 检查MCP服务器文件是否存在
            mcp_server_files = [
                "mcp_server.py",
                "super_mcp_unified.py",
                "deepseek_complete_mcp.py",
                "trae_cn_mcp_server.py"
            ]
            
            results = {
                "status": "success",
                "files_found": 0,
                "files_missing": 0,
                "details": []
            }
            
            current_dir = os.getcwd()
            for file in mcp_server_files:
                file_path = os.path.join(current_dir, file)
                if os.path.exists(file_path):
                    results["files_found"] += 1
                    results["details"].append({
                        "file": file,
                        "path": file_path,
                        "status": "found"
                    })
                else:
                    results["files_missing"] += 1
                    results["details"].append({
                        "file": file,
                        "path": file_path,
                        "status": "missing"
                    })
            
            logger.info(f"MCP服务器路径检查完成: 找到 {results['files_found']} 个文件，缺失 {results['files_missing']} 个文件")
            return results
        except Exception as e:
            logger.error(f"MCP服务器路径检查失败: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

class MCPServerDebugger:
    """
    MCP服务器调试工具
    """
    
    def __init__(self, config: dict = None):
        """
        初始化调试工具
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        logger.info("MCP服务器调试工具初始化完成")
    
    def debug_mcp_server(self) -> Dict[str, Any]:
        """
        调试MCP服务器
        
        Returns:
            dict: 调试结果
        """
        logger.info("开始调试MCP服务器...")
        
        try:
            # 检查Python版本
            python_version = sys.version
            logger.info(f"Python版本: {python_version}")
            
            # 检查依赖包
            required_packages = [
                "requests",
                "flask",
                "json",
                "os",
                "sys"
            ]
            
            results = {
                "status": "success",
                "python_version": python_version,
                "packages": [],
                "debug_info": []
            }
            
            for package in required_packages:
                try:
                    __import__(package)
                    results["packages"].append({
                        "package": package,
                        "status": "installed"
                    })
                except ImportError:
                    results["packages"].append({
                        "package": package,
                        "status": "missing"
                    })
            
            # 检查端口是否被占用
            port = self.config.get("port", 5000)
            try:
                import socket
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(("localhost", port))
                    results["debug_info"].append({
                        "test": "port_check",
                        "port": port,
                        "status": "available"
                    })
            except OSError:
                results["debug_info"].append({
                    "test": "port_check",
                    "port": port,
                    "status": "in_use"
                })
            
            logger.info("MCP服务器调试完成")
            return results
        except Exception as e:
            logger.error(f"MCP服务器调试失败: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

class JSONFixer:
    """
    JSON修复工具
    """
    
    def __init__(self, config: dict = None):
        """
        初始化JSON修复工具
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        logger.info("JSON修复工具初始化完成")
    
    def fix_json(self, json_string: str) -> Dict[str, Any]:
        """
        修复JSON字符串
        
        Args:
            json_string: 需要修复的JSON字符串
        
        Returns:
            dict: 修复结果
        """
        logger.info("开始修复JSON...")
        
        try:
            # 尝试直接解析
            json_data = json.loads(json_string)
            return {
                "status": "success",
                "original_json": json_string,
                "fixed_json": json_data,
                "message": "JSON格式正确，无需修复"
            }
        except json.JSONDecodeError as e:
            logger.warning(f"JSON格式错误: {e}")
            
            # 尝试修复常见JSON错误
            try:
                # 移除尾部多余逗号
                fixed_string = json_string.replace(",\n}", "\n}").replace(",\n]", "\n]")
                # 替换单引号为双引号
                fixed_string = fixed_string.replace("'", "\"")
                # 解析修复后的JSON
                json_data = json.loads(fixed_string)
                
                return {
                    "status": "success",
                    "original_json": json_string,
                    "fixed_json": json_data,
                    "fixed_string": fixed_string,
                    "message": "JSON已修复"
                }
            except json.JSONDecodeError as e2:
                logger.error(f"JSON修复失败: {e2}")
                return {
                    "status": "failed",
                    "original_json": json_string,
                    "error": str(e2),
                    "message": "无法修复JSON格式错误"
                }
    
    def fix_json_file(self, file_path: str) -> Dict[str, Any]:
        """
        修复JSON文件
        
        Args:
            file_path: JSON文件路径
        
        Returns:
            dict: 修复结果
        """
        logger.info(f"修复JSON文件: {file_path}")
        
        try:
            if not os.path.exists(file_path):
                return {
                    "status": "failed",
                    "error": f"文件不存在: {file_path}"
                }
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            result = self.fix_json(content)
            
            if result["status"] == "success" and "fixed_string" in result:
                # 保存修复后的JSON
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(result["fixed_json"], f, ensure_ascii=False, indent=2)
                logger.info(f"JSON文件已修复并保存: {file_path}")
            
            return result
        except Exception as e:
            logger.error(f"修复JSON文件失败: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

class MCPResponseFixer:
    """
    MCP响应修复工具
    """
    
    def __init__(self, config: dict = None):
        """
        初始化MCP响应修复工具
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        logger.info("MCP响应修复工具初始化完成")
    
    def fix_mcp_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        修复MCP响应
        
        Args:
            response: MCP响应数据
        
        Returns:
            dict: 修复后的响应
        """
        logger.info("开始修复MCP响应...")
        
        try:
            # 检查响应结构
            fixed_response = response.copy()
            
            # 确保响应包含必要字段
            required_fields = [
                "status",
                "message",
                "data",
                "timestamp"
            ]
            
            for field in required_fields:
                if field not in fixed_response:
                    if field == "status":
                        fixed_response["status"] = "success"
                    elif field == "message":
                        fixed_response["message"] = "Operation completed"
                    elif field == "data":
                        fixed_response["data"] = {}
                    elif field == "timestamp":
                        fixed_response["timestamp"] = time.time()
            
            logger.info("MCP响应修复完成")
            return fixed_response
        except Exception as e:
            logger.error(f"MCP响应修复失败: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

class CozeDocsGetter:
    """
    Coze文档获取工具
    """
    
    def __init__(self, config: dict = None):
        """
        初始化Coze文档获取工具
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        logger.info("Coze文档获取工具初始化完成")
    
    def get_coze_docs(self) -> Dict[str, Any]:
        """
        获取Coze文档
        
        Returns:
            dict: 获取结果
        """
        logger.info("获取Coze文档...")
        
        try:
            # 这里可以添加获取Coze文档的逻辑
            # 目前返回示例数据
            coze_docs = {
                "docs": [
                    {
                        "title": "Coze平台使用指南",
                        "url": "https://www.coze.com/docs",
                        "description": "Coze平台的官方使用指南"
                    },
                    {
                        "title": "Coze插件开发文档",
                        "url": "https://www.coze.com/docs/plugins",
                        "description": "Coze插件开发的详细文档"
                    },
                    {
                        "title": "Coze API参考",
                        "url": "https://www.coze.com/docs/api",
                        "description": "Coze API的详细参考文档"
                    }
                ]
            }
            
            logger.info("Coze文档获取完成")
            return {
                "status": "success",
                "coze_docs": coze_docs,
                "message": "Coze文档获取成功"
            }
        except Exception as e:
            logger.error(f"Coze文档获取失败: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

class PythonNPXTool:
    """
    Python NPX工具
    """
    
    def __init__(self, config: dict = None):
        """
        初始化Python NPX工具
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        logger.info("Python NPX工具初始化完成")
    
    def run_npx_command(self, command: str) -> Dict[str, Any]:
        """
        运行NPX命令
        
        Args:
            command: NPX命令
        
        Returns:
            dict: 运行结果
        """
        logger.info(f"运行NPX命令: {command}")
        
        try:
            # 构建完整命令
            full_command = f"npx {command}"
            
            # 运行命令
            result = subprocess.run(
                full_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "status": "success" if result.returncode == 0 else "failed",
                "command": full_command,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "output": result.stdout + result.stderr
            }
        except Exception as e:
            logger.error(f"NPX命令运行失败: {e}")
            return {
                "status": "failed",
                "command": command,
                "error": str(e)
            }

class MCPServerStarter:
    """
    MCP服务器启动工具
    """
    
    def __init__(self, config: dict = None):
        """
        初始化MCP服务器启动工具
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        logger.info("MCP服务器启动工具初始化完成")
    
    def start_mcp_server(self, server_file: str = "mcp_server.py") -> Dict[str, Any]:
        """
        启动MCP服务器
        
        Args:
            server_file: 服务器文件名
        
        Returns:
            dict: 启动结果
        """
        logger.info(f"启动MCP服务器: {server_file}")
        
        try:
            if not os.path.exists(server_file):
                return {
                    "status": "failed",
                    "error": f"服务器文件不存在: {server_file}"
                }
            
            # 启动服务器进程
            process = subprocess.Popen(
                [sys.executable, server_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待服务器启动
            time.sleep(2)
            
            # 检查进程状态
            if process.poll() is None:
                # 进程仍在运行
                logger.info(f"MCP服务器启动成功: {server_file}, PID: {process.pid}")
                return {
                    "status": "success",
                    "server_file": server_file,
                    "pid": process.pid,
                    "message": f"MCP服务器已启动，PID: {process.pid}"
                }
            else:
                # 进程已退出，读取错误信息
                stdout, stderr = process.communicate()
                logger.error(f"MCP服务器启动失败，退出码: {process.returncode}")
                return {
                    "status": "failed",
                    "server_file": server_file,
                    "returncode": process.returncode,
                    "stdout": stdout,
                    "stderr": stderr,
                    "message": "MCP服务器启动失败"
                }
        except Exception as e:
            logger.error(f"MCP服务器启动失败: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

class UnifiedMCPManager:
    """
    统一MCP管理器
    """
    
    def __init__(self, config: dict = None):
        """
        初始化统一MCP管理器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        self.temp_dir = tempfile.mkdtemp(prefix='unified_mcp_manager_')
        logger.info(f"统一MCP管理器初始化完成，临时目录: {self.temp_dir}")
    
    def manage_mcp_servers(self) -> Dict[str, Any]:
        """
        管理MCP服务器
        
        Returns:
            dict: 管理结果
        """
        logger.info("开始管理MCP服务器...")
        
        try:
            # 检查所有MCP服务器
            checker = MCPServerChecker(self.config)
            path_check = checker.check_mcp_server_path()
            
            # 调试MCP服务器
            debugger = MCPServerDebugger(self.config)
            debug_result = debugger.debug_mcp_server()
            
            return {
                "status": "success",
                "path_check": path_check,
                "debug_result": debug_result,
                "message": "MCP服务器管理完成"
            }
        except Exception as e:
            logger.error(f"MCP服务器管理失败: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

class ToolManager:
    """
    工具管理器 - 统一管理所有工具
    """
    
    def __init__(self, config: dict = None):
        """
        初始化工具管理器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        self.tools = {
            "check_mcp_server_path": MCPServerChecker,
            "debug_mcp_server": MCPServerDebugger,
            "fix_json": JSONFixer,
            "fix_mcp_response": MCPResponseFixer,
            "get_coze_docs": CozeDocsGetter,
            "run_npx_command": PythonNPXTool,
            "start_mcp_server": MCPServerStarter,
            "manage_mcp_servers": UnifiedMCPManager
        }
        logger.info(f"工具管理器初始化完成，共包含 {len(self.tools)} 种工具")
    
    def run_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        运行指定工具
        
        Args:
            tool_name: 工具名称
            **kwargs: 工具参数
        
        Returns:
            dict: 工具运行结果
        """
        logger.info(f"运行工具: {tool_name}")
        
        if tool_name in self.tools:
            tool_class = self.tools[tool_name]
            tool_instance = tool_class(self.config)
            tool_method = getattr(tool_instance, tool_name)
            
            try:
                result = tool_method(**kwargs)
                logger.info(f"工具 {tool_name} 运行成功")
                return result
            except Exception as e:
                logger.error(f"工具 {tool_name} 运行失败: {e}")
                return {
                    "status": "failed",
                    "error": str(e),
                    "tool_name": tool_name
                }
        else:
            logger.error(f"未知工具名称: {tool_name}")
            return {
                "status": "failed",
                "error": f"未知工具名称: {tool_name}",
                "tool_name": tool_name
            }

# 工具函数
def run_tool(tool_name: str, **kwargs) -> Dict[str, Any]:
    """
    运行指定工具
    
    Args:
        tool_name: 工具名称
        **kwargs: 工具参数
    
    Returns:
        dict: 工具运行结果
    """
    tool_manager = ToolManager()
    return tool_manager.run_tool(tool_name, **kwargs)

def get_available_tools() -> List[str]:
    """
    获取可用工具列表
    
    Returns:
        list: 可用工具列表
    """
    tool_manager = ToolManager()
    return list(tool_manager.tools.keys())

def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='合并后的工具脚本')
    parser.add_argument('--tool', type=str, help='工具名称')
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--list-tools', action='store_true', help='列出所有可用工具')
    parser.add_argument('--verbose', action='store_true', help='显示详细结果')
    
    # 工具特定参数
    parser.add_argument('--file', type=str, help='文件路径（用于修复JSON等工具）')
    parser.add_argument('--command', type=str, help='命令（用于NPX等工具）')
    parser.add_argument('--server-file', type=str, help='服务器文件（用于启动MCP服务器）')
    parser.add_argument('--json', type=str, help='JSON字符串（用于修复JSON）')
    
    args = parser.parse_args()
    
    # 加载配置
    config = {}
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r', encoding='utf-8') as f:
            config = json.load(f)
    
    if args.list_tools:
        # 列出所有可用工具
        print("\n📋 可用工具列表:")
        for tool in get_available_tools():
            print(f"   - {tool}")
        return
    
    if args.tool:
        # 运行指定工具
        tool_name = args.tool
        kwargs = {}
        
        # 根据工具名称添加相应参数
        if tool_name == "fix_json_file" and args.file:
            kwargs["file_path"] = args.file
        elif tool_name == "fix_json" and args.json:
            kwargs["json_string"] = args.json
        elif tool_name == "run_npx_command" and args.command:
            kwargs["command"] = args.command
        elif tool_name == "start_mcp_server" and args.server_file:
            kwargs["server_file"] = args.server_file
        
        print(f"\n🚀 运行工具: {tool_name}...")
        results = run_tool(tool_name, **kwargs)
        
        print(f"\n📊 工具运行结果:")
        print(f"   状态: {results['status']}")
        
        if args.verbose or results['status'] == "failed":
            print(f"\n🔍 详细结果:")
            for key, value in results.items():
                if key not in ["original_json", "fixed_json", "fixed_string"]:
                    print(f"   {key}: {value}")
        
        if results['status'] == "failed":
            sys.exit(1)
    else:
        # 显示帮助信息
        parser.print_help()

if __name__ == '__main__':
    main()
