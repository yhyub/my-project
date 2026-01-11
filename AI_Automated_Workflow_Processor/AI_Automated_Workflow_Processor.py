#!/usr/bin/env python3
"""
AI_Automated_Workflow_Processo - 完整的AI自动化工作流处理器

集成了工作流修复、错误检测、人工智能代码分析、工作流生成、批量处理、画布自动化填写等核心功能。
支持从URL获取资源，自动检测并修复工作流错误，分析代码质量，根据需求生成新工作流，
实现工作流的批量修复和合并，以及自动化填写Coze画布。通过智能结果合并，返回统一的处理结果和类型，
提升工作流开发和维护效率。
"""

import json
import requests
import re
import os
import time
from typing import Dict, List, Any, Optional, Tuple

class AIWorkflowProcessor:
    """AI自动化工作流处理器核心类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化工作流处理器
        
        Args:
            config: 配置字典，包含API密钥、模型配置等
        """
        self.config = self._load_config(config)
        self.supported_workflow_formats = ["json", "yaml", "yml"]
        self.workflow_schema = self._load_workflow_schema()
        
    def _load_config(self, config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """加载配置
        
        Args:
            config: 外部配置
            
        Returns:
            合并后的配置字典
        """
        default_config = {
            "deepseek_api_key": "",
            "deepseek_api_url": "https://api.deepseek.com",
            "model": "deepseek-chat",
            "timeout": 60,
            "output_dir": "./workflow_output",
            "log_level": "info"
        }
        
        if config:
            default_config.update(config)
        
        # 创建输出目录
        os.makedirs(default_config["output_dir"], exist_ok=True)
        
        return default_config
    
    def _load_workflow_schema(self) -> Dict[str, Any]:
        """加载工作流schema
        
        Returns:
            工作流schema字典
        """
        # 简化的工作流schema，实际项目中可以从文件或API加载
        return {
            "type": "object",
            "required": ["name", "description", "nodes", "edges"],
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "version": {"type": "string"},
                "nodes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["id", "type", "data"],
                        "properties": {
                            "id": {"type": "string"},
                            "type": {"type": "string"},
                            "data": {"type": "object"},
                            "position": {"type": "object"}
                        }
                    }
                },
                "edges": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["id", "source", "target"],
                        "properties": {
                            "id": {"type": "string"},
                            "source": {"type": "string"},
                            "target": {"type": "string"},
                            "sourceHandle": {"type": "string"},
                            "targetHandle": {"type": "string"}
                        }
                    }
                }
            }
        }
    
    def get_resource_from_url(self, url: str) -> Dict[str, Any]:
        """从URL获取资源
        
        Args:
            url: 资源URL
            
        Returns:
            资源内容字典
        """
        try:
            response = requests.get(url, timeout=self.config["timeout"])
            response.raise_for_status()
            return {
                "status": "success",
                "data": response.json(),
                "message": f"Successfully fetched resource from {url}"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": f"Failed to fetch resource from {url}"
            }
    
    def detect_workflow_errors(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """检测工作流错误
        
        Args:
            workflow: 工作流数据
            
        Returns:
            错误检测结果
        """
        errors = []
        warnings = []
        
        # 检查必填字段
        required_fields = self.workflow_schema.get("required", [])
        for field in required_fields:
            if field not in workflow:
                errors.append({
                    "type": "missing_required_field",
                    "field": field,
                    "message": f"Missing required field: {field}"
                })
        
        # 检查节点
        if "nodes" in workflow:
            nodes = workflow["nodes"]
            node_ids = set()
            
            for i, node in enumerate(nodes):
                # 检查节点必填字段
                node_required = self.workflow_schema["properties"]["nodes"]["items"]["required"]
                for field in node_required:
                    if field not in node:
                        errors.append({
                            "type": "missing_node_field",
                            "node_index": i,
                            "field": field,
                            "message": f"Node {i} missing required field: {field}"
                        })
                
                # 检查节点ID唯一性
                if "id" in node:
                    if node["id"] in node_ids:
                        errors.append({
                            "type": "duplicate_node_id",
                            "node_id": node["id"],
                            "message": f"Duplicate node ID: {node['id']}"
                        })
                    node_ids.add(node["id"])
        
        # 检查边
        if "edges" in workflow:
            edges = workflow["edges"]
            edge_ids = set()
            
            for i, edge in enumerate(edges):
                # 检查边必填字段
                edge_required = self.workflow_schema["properties"]["edges"]["items"]["required"]
                for field in edge_required:
                    if field not in edge:
                        errors.append({
                            "type": "missing_edge_field",
                            "edge_index": i,
                            "field": field,
                            "message": f"Edge {i} missing required field: {field}"
                        })
                
                # 检查边ID唯一性
                if "id" in edge:
                    if edge["id"] in edge_ids:
                        errors.append({
                            "type": "duplicate_edge_id",
                            "edge_id": edge["id"],
                            "message": f"Duplicate edge ID: {edge['id']}"
                        })
                    edge_ids.add(edge["id"])
                
                # 检查边引用的节点是否存在
                if "source" in edge and "target" in edge and "nodes" in workflow:
                    node_ids = {node["id"] for node in workflow["nodes"]}
                    if edge["source"] not in node_ids:
                        errors.append({
                            "type": "invalid_edge_source",
                            "edge_id": edge.get("id", f"edge_{i}"),
                            "source": edge["source"],
                            "message": f"Edge references non-existent source node: {edge['source']}"
                        })
                    if edge["target"] not in node_ids:
                        errors.append({
                            "type": "invalid_edge_target",
                            "edge_id": edge.get("id", f"edge_{i}"),
                            "target": edge["target"],
                            "message": f"Edge references non-existent target node: {edge['target']}"
                        })
        
        return {
            "status": "success",
            "errors": errors,
            "warnings": warnings,
            "total_errors": len(errors),
            "total_warnings": len(warnings)
        }
    
    def fix_workflow_errors(self, workflow: Dict[str, Any], error_report: Dict[str, Any]) -> Dict[str, Any]:
        """修复工作流错误
        
        Args:
            workflow: 工作流数据
            error_report: 错误检测报告
            
        Returns:
            修复后的工作流和修复报告
        """
        fixed_workflow = workflow.copy()
        fixes = []
        
        # 修复缺失的必填字段
        required_fields = self.workflow_schema.get("required", [])
        for field in required_fields:
            if field not in fixed_workflow:
                if field == "name":
                    fixed_workflow["name"] = "Untitled Workflow"
                    fixes.append({
                        "type": "added_required_field",
                        "field": field,
                        "value": fixed_workflow[field],
                        "message": f"Added missing required field '{field}' with default value"
                    })
                elif field == "description":
                    fixed_workflow["description"] = "Automatically generated workflow"
                    fixes.append({
                        "type": "added_required_field",
                        "field": field,
                        "value": fixed_workflow[field],
                        "message": f"Added missing required field '{field}' with default value"
                    })
                elif field == "nodes":
                    fixed_workflow["nodes"] = []
                    fixes.append({
                        "type": "added_required_field",
                        "field": field,
                        "value": fixed_workflow[field],
                        "message": f"Added missing required field '{field}' with empty array"
                    })
                elif field == "edges":
                    fixed_workflow["edges"] = []
                    fixes.append({
                        "type": "added_required_field",
                        "field": field,
                        "value": fixed_workflow[field],
                        "message": f"Added missing required field '{field}' with empty array"
                    })
        
        # 修复节点问题
        if "nodes" in fixed_workflow:
            nodes = fixed_workflow["nodes"]
            node_ids = set()
            
            for i, node in enumerate(nodes):
                # 确保节点ID唯一
                if "id" in node:
                    original_id = node["id"]
                    counter = 1
                    while node["id"] in node_ids:
                        node["id"] = f"{original_id}_{counter}"
                        counter += 1
                    if node["id"] != original_id:
                        fixes.append({
                            "type": "fixed_duplicate_node_id",
                            "node_index": i,
                            "old_id": original_id,
                            "new_id": node["id"],
                            "message": f"Fixed duplicate node ID: {original_id} -> {node['id']}"
                        })
                    node_ids.add(node["id"])
                else:
                    # 添加缺失的节点ID
                    new_id = f"node_{i}"
                    node["id"] = new_id
                    node_ids.add(new_id)
                    fixes.append({
                        "type": "added_node_id",
                        "node_index": i,
                        "new_id": new_id,
                        "message": f"Added missing node ID: {new_id}"
                    })
        
        # 修复边问题
        if "edges" in fixed_workflow and "nodes" in fixed_workflow:
            edges = fixed_workflow["edges"]
            edge_ids = set()
            node_ids = {node["id"] for node in fixed_workflow["nodes"]}
            
            for i, edge in enumerate(edges):
                # 确保边ID唯一
                if "id" in edge:
                    original_id = edge["id"]
                    counter = 1
                    while edge["id"] in edge_ids:
                        edge["id"] = f"{original_id}_{counter}"
                        counter += 1
                    if edge["id"] != original_id:
                        fixes.append({
                            "type": "fixed_duplicate_edge_id",
                            "edge_index": i,
                            "old_id": original_id,
                            "new_id": edge["id"],
                            "message": f"Fixed duplicate edge ID: {original_id} -> {edge['id']}"
                        })
                    edge_ids.add(edge["id"])
                else:
                    # 添加缺失的边ID
                    new_id = f"edge_{i}"
                    edge["id"] = new_id
                    edge_ids.add(new_id)
                    fixes.append({
                        "type": "added_edge_id",
                        "edge_index": i,
                        "new_id": new_id,
                        "message": f"Added missing edge ID: {new_id}"
                    })
        
        return {
            "status": "success",
            "fixed_workflow": fixed_workflow,
            "fixes": fixes,
            "total_fixes": len(fixes)
        }
    
    def analyze_code_quality(self, code: str, language: str = "python") -> Dict[str, Any]:
        """分析代码质量
        
        Args:
            code: 代码内容
            language: 代码语言
            
        Returns:
            代码质量分析报告
        """
        # 简化的代码质量分析，实际项目中可以集成更复杂的分析工具
        issues = []
        
        # 检查代码行数
        lines = code.split('\n')
        total_lines = len(lines)
        
        # 检查空行
        empty_lines = sum(1 for line in lines if line.strip() == '')
        
        # 检查注释比例
        comment_lines = sum(1 for line in lines if line.strip().startswith('#') or '#' in line)
        comment_ratio = comment_lines / total_lines if total_lines > 0 else 0
        
        # 检查长行
        long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 80]
        for line_num in long_lines:
            issues.append({
                "type": "long_line",
                "line": line_num,
                "message": f"Line {line_num} is too long (exceeds 80 characters)"
            })
        
        # 检查重复代码（简化版本）
        line_counts = {}
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                line_counts[stripped] = line_counts.get(stripped, 0) + 1
        
        for line, count in line_counts.items():
            if count > 5:
                issues.append({
                    "type": "repeated_code",
                    "line_content": line,
                    "count": count,
                    "message": f"Code line repeated {count} times: {line}"
                })
        
        # 检查缺少文档字符串
        if language == "python":
            # 简单检查函数缺少文档字符串
            function_pattern = r'def\s+\w+\s*\([^)]*\)\s*:'
            functions = re.finditer(function_pattern, code)
            
            for match in functions:
                function_start = match.end()
                # 检查下一行是否是文档字符串
                next_line = code[function_start:].split('\n')[0].strip()
                if not (next_line.startswith('"""') or next_line.startswith("'""")):
                    issues.append({
                        "type": "missing_docstring",
                        "function": match.group(),
                        "message": f"Function {match.group()} missing docstring"
                    })
        
        return {
            "status": "success",
            "language": language,
            "total_lines": total_lines,
            "empty_lines": empty_lines,
            "comment_lines": comment_lines,
            "comment_ratio": round(comment_ratio, 2),
            "issues": issues,
            "total_issues": len(issues)
        }
    
    def generate_workflow(self, requirements: str) -> Dict[str, Any]:
        """根据需求生成工作流
        
        Args:
            requirements: 工作流需求描述
            
        Returns:
            生成的工作流
        """
        # 简化的工作流生成，实际项目中可以集成LLM来生成更复杂的工作流
        workflow = {
            "name": "Generated Workflow",
            "description": f"Automatically generated from requirements: {requirements}",
            "version": "1.0.0",
            "nodes": [
                {
                    "id": "start",
                    "type": "start",
                    "data": {
                        "label": "Start",
                        "description": "Workflow start node"
                    },
                    "position": {"x": 100, "y": 100}
                },
                {
                    "id": "process",
                    "type": "process",
                    "data": {
                        "label": "Process",
                        "description": "Main processing node",
                        "requirements": requirements
                    },
                    "position": {"x": 300, "y": 100}
                },
                {
                    "id": "end",
                    "type": "end",
                    "data": {
                        "label": "End",
                        "description": "Workflow end node"
                    },
                    "position": {"x": 500, "y": 100}
                }
            ],
            "edges": [
                {
                    "id": "edge_start_process",
                    "source": "start",
                    "target": "process"
                },
                {
                    "id": "edge_process_end",
                    "source": "process",
                    "target": "end"
                }
            ]
        }
        
        return {
            "status": "success",
            "workflow": workflow,
            "requirements": requirements
        }
    
    def auto_fill_canvas(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """自动化填写Coze画布
        
        Args:
            workflow: 工作流数据
            
        Returns:
            填写完成的画布数据
        """
        # 简化的画布填写，实际项目中需要根据Coze画布的具体格式进行填写
        canvas_data = {
            "workflow": workflow,
            "canvas_settings": {
                "title": workflow.get("name", "Untitled Canvas"),
                "description": workflow.get("description", ""),
                "version": workflow.get("version", "1.0.0"),
                "theme": "default",
                "zoom": 1.0,
                "centerX": 0,
                "centerY": 0
            },
            "nodes_positioned": True,
            "auto_layout": True
        }
        
        # 自动布局节点（简化版）
        if "nodes" in workflow:
            nodes = workflow["nodes"]
            for i, node in enumerate(nodes):
                if "position" not in node:
                    node["position"] = {
                        "x": 100 + (i * 200),
                        "y": 100
                    }
        
        return {
            "status": "success",
            "canvas_data": canvas_data,
            "message": "Canvas automatically filled"
        }
    
    def batch_process_workflows(self, workflows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量处理工作流
        
        Args:
            workflows: 工作流列表
            
        Returns:
            批量处理结果
        """
        results = []
        
        for i, workflow in enumerate(workflows):
            # 检测错误
            error_report = self.detect_workflow_errors(workflow)
            
            # 修复错误
            fix_result = self.fix_workflow_errors(workflow, error_report)
            
            # 填写画布
            canvas_result = self.auto_fill_canvas(fix_result["fixed_workflow"])
            
            results.append({
                "original_index": i,
                "error_detection": error_report,
                "fix_result": fix_result,
                "canvas_result": canvas_result
            })
        
        return {
            "status": "success",
            "results": results,
            "total_workflows": len(workflows),
            "processed_workflows": len(results)
        }
    
    def merge_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """智能合并结果
        
        Args:
            results: 结果列表
            
        Returns:
            合并后的结果
        """
        merged = {
            "status": "success",
            "total_results": len(results),
            "merged_at": time.time(),
            "summary": {
                "success_count": 0,
                "error_count": 0,
                "warning_count": 0
            },
            "detailed_results": []
        }
        
        for result in results:
            if result["status"] == "success":
                merged["summary"]["success_count"] += 1
            else:
                merged["summary"]["error_count"] += 1
            
            merged["detailed_results"].append(result)
        
        return merged
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """主处理函数
        
        Args:
            input_data: 输入数据，包含处理类型和参数
            
        Returns:
            处理结果
        """
        process_type = input_data.get("type", "")
        
        if process_type == "fetch_resource":
            # 从URL获取资源
            url = input_data.get("url", "")
            if not url:
                return {"status": "error", "message": "Missing URL parameter"}
            return self.get_resource_from_url(url)
        
        elif process_type == "detect_errors":
            # 检测工作流错误
            workflow = input_data.get("workflow", {})
            return self.detect_workflow_errors(workflow)
        
        elif process_type == "fix_errors":
            # 修复工作流错误
            workflow = input_data.get("workflow", {})
            error_report = input_data.get("error_report", {})
            if not error_report:
                error_report = self.detect_workflow_errors(workflow)
            return self.fix_workflow_errors(workflow, error_report)
        
        elif process_type == "analyze_code":
            # 分析代码质量
            code = input_data.get("code", "")
            language = input_data.get("language", "python")
            if not code:
                return {"status": "error", "message": "Missing code parameter"}
            return self.analyze_code_quality(code, language)
        
        elif process_type == "generate_workflow":
            # 生成工作流
            requirements = input_data.get("requirements", "")
            if not requirements:
                return {"status": "error", "message": "Missing requirements parameter"}
            return self.generate_workflow(requirements)
        
        elif process_type == "auto_fill_canvas":
            # 自动填写画布
            workflow = input_data.get("workflow", {})
            if not workflow:
                return {"status": "error", "message": "Missing workflow parameter"}
            return self.auto_fill_canvas(workflow)
        
        elif process_type == "batch_process":
            # 批量处理
            workflows = input_data.get("workflows", [])
            if not workflows:
                return {"status": "error", "message": "Missing workflows parameter"}
            return self.batch_process_workflows(workflows)
        
        elif process_type == "merge_results":
            # 合并结果
            results = input_data.get("results", [])
            if not results:
                return {"status": "error", "message": "Missing results parameter"}
            return self.merge_results(results)
        
        else:
            return {
                "status": "error",
                "message": f"Unknown process type: {process_type}",
                "supported_types": [
                    "fetch_resource", "detect_errors", "fix_errors", 
                    "analyze_code", "generate_workflow", "auto_fill_canvas",
                    "batch_process", "merge_results"
                ]
            }
    
    def run_as_server(self, host: str = "localhost", port: int = 8080):
        """以HTTP服务器模式运行
        
        Args:
            host: 服务器主机
            port: 服务器端口
        """
        from flask import Flask, request, jsonify
        
        app = Flask(__name__)
        
        @app.route('/process', methods=['POST'])
        def api_process():
            try:
                input_data = request.json
                result = self.process(input_data)
                return jsonify(result)
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
        
        @app.route('/health', methods=['GET'])
        def health_check():
            return jsonify({
                "status": "healthy",
                "service": "AI_Automated_Workflow_Processo",
                "timestamp": time.time()
            })
        
        print(f"🚀 AI_Automated_Workflow_Processo 服务器启动")
        print(f"📡 监听地址: http://{host}:{port}")
        print(f"💡 健康检查: http://{host}:{port}/health")
        print(f"🔧 API端点: http://{host}:{port}/process")
        print(f"📚 支持的处理类型: fetch_resource, detect_errors, fix_errors, analyze_code, generate_workflow, auto_fill_canvas, batch_process, merge_results")
        print(f"\n按 Ctrl+C 停止服务器")
        
        app.run(host=host, port=port)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI_Automated_Workflow_Processo - 完整的AI自动化工作流处理器')
    parser.add_argument('--server', action='store_true', help='以HTTP服务器模式运行')
    parser.add_argument('--host', type=str, default='localhost', help='服务器主机地址')
    parser.add_argument('--port', type=int, default=8080, help='服务器端口')
    parser.add_argument('--test', action='store_true', help='运行测试')
    
    args = parser.parse_args()
    
    processor = AIWorkflowProcessor()
    
    if args.test:
        # 运行测试
        print("🔍 运行AI自动化工作流处理器测试...")
        
        # 测试1: 生成工作流
        print("\n1. 测试工作流生成功能...")
        generate_result = processor.generate_workflow("创建一个简单的用户注册工作流")
        print(f"   结果: {generate_result['status']}")
        print(f"   生成的工作流名称: {generate_result['workflow']['name']}")
        print(f"   节点数量: {len(generate_result['workflow']['nodes'])}")
        print(f"   边数量: {len(generate_result['workflow']['edges'])}")
        
        # 测试2: 检测工作流错误
        print("\n2. 测试错误检测功能...")
        # 创建一个有错误的工作流
        broken_workflow = {
            "name": "Broken Workflow",
            "nodes": [
                {"type": "start", "data": {"label": "Start"}}  # 缺少id字段
            ]
        }
        error_result = processor.detect_workflow_errors(broken_workflow)
        print(f"   结果: {error_result['status']}")
        print(f"   错误数量: {error_result['total_errors']}")
        
        # 测试3: 修复工作流错误
        print("\n3. 测试工作流修复功能...")
        fix_result = processor.fix_workflow_errors(broken_workflow, error_result)
        print(f"   结果: {fix_result['status']}")
        print(f"   修复数量: {fix_result['total_fixes']}")
        print(f"   修复后是否包含edges字段: {'edges' in fix_result['fixed_workflow']}")
        
        # 测试4: 代码质量分析
        print("\n4. 测试代码质量分析功能...")
        test_code = '''
def add(a, b):
    return a + b

print(add(1, 2))
'''        
        code_analysis = processor.analyze_code_quality(test_code)
        print(f"   结果: {code_analysis['status']}")
        print(f"   代码行数: {code_analysis['total_lines']}")
        print(f"   注释比例: {code_analysis['comment_ratio']}")
        print(f"   问题数量: {code_analysis['total_issues']}")
        
        # 测试5: 自动填写画布
        print("\n5. 测试画布自动化填写功能...")
        canvas_result = processor.auto_fill_canvas(generate_result['workflow'])
        print(f"   结果: {canvas_result['status']}")
        
        print("\n🎉 所有测试完成！")
        
    elif args.server:
        # 启动服务器
        processor.run_as_server(args.host, args.port)
    else:
        # 显示帮助信息
        parser.print_help()


if __name__ == '__main__':
    main()
