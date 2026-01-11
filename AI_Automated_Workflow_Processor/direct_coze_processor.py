#!/usr/bin/env python3
"""
直接处理Coze工作流URL，包含完整的AIWorkflowProcessor功能
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

# Coze工作流URL
COZE_WORKFLOW_URL = "https://www.coze.cn/work_flow?space_id=7382283479335403547&workflow_id=7582809614418624547&force_stay=1"

def main():
    """主函数"""
    print("🚀 开始处理Coze工作流")
    print(f"📡 工作流URL: {COZE_WORKFLOW_URL}")
    
    # 初始化工作流处理器
    processor = AIWorkflowProcessor()
    
    # 从URL获取工作流数据
    print("\n1. 从URL获取工作流数据...")
    fetch_result = processor.get_resource_from_url(COZE_WORKFLOW_URL)
    
    if fetch_result["status"] == "success":
        print(f"✅ 成功获取工作流数据")
        
        # 保存原始工作流数据
        with open("original_coze_workflow.json", "w", encoding="utf-8") as f:
            json.dump(fetch_result["data"], f, ensure_ascii=False, indent=2)
        print(f"💾 原始工作流数据已保存到: original_coze_workflow.json")
        
        # 检测工作流错误
        print("\n2. 检测工作流错误...")
        error_result = processor.detect_workflow_errors(fetch_result["data"])
        
        print(f"📋 错误检测结果:")
        print(f"   错误数量: {error_result['total_errors']}")
        print(f"   警告数量: {error_result['total_warnings']}")
        
        # 保存错误检测结果
        with open("workflow_error_report.json", "w", encoding="utf-8") as f:
            json.dump(error_result, f, ensure_ascii=False, indent=2)
        print(f"💾 错误检测报告已保存到: workflow_error_report.json")
        
        # 如果有错误，修复工作流
        if error_result["total_errors"] > 0:
            print("\n3. 修复工作流错误...")
            fix_result = processor.fix_workflow_errors(fetch_result["data"], error_result)
            
            print(f"📋 工作流修复结果:")
            print(f"   修复数量: {fix_result['total_fixes']}")
            print(f"   修复后是否包含edges字段: {'edges' in fix_result['fixed_workflow']}")
            
            # 保存修复后的工作流
            with open("repaired_coze_workflow.json", "w", encoding="utf-8") as f:
                json.dump(fix_result["fixed_workflow"], f, ensure_ascii=False, indent=2)
            print(f"💾 修复后的工作流已保存到: repaired_coze_workflow.json")
            
            # 保存修复报告
            with open("workflow_fix_report.json", "w", encoding="utf-8") as f:
                json.dump(fix_result, f, ensure_ascii=False, indent=2)
            print(f"💾 工作流修复报告已保存到: workflow_fix_report.json")
        
        # 自动填写画布
        print("\n4. 自动填写Coze画布...")
        canvas_result = processor.auto_fill_canvas(fetch_result["data"])
        
        # 保存画布数据
        with open("auto_filled_canvas.json", "w", encoding="utf-8") as f:
            json.dump(canvas_result["canvas_data"], f, ensure_ascii=False, indent=2)
        print(f"💾 自动填写的画布数据已保存到: auto_filled_canvas.json")
        
        print("\n🎉 Coze工作流处理完成！")
        print("📁 生成的文件:")
        print("   - original_coze_workflow.json: 原始工作流数据")
        print("   - workflow_error_report.json: 错误检测报告")
        if error_result["total_errors"] > 0:
            print("   - repaired_coze_workflow.json: 修复后的工作流")
            print("   - workflow_fix_report.json: 工作流修复报告")
        print("   - auto_filled_canvas.json: 自动填写的画布数据")
        
    else:
        print(f"❌ 从URL获取工作流数据失败: {fetch_result['error']}")
        print(f"ℹ️  可能需要登录Coze账号才能访问工作流数据")
        print(f"💡 建议: 手动登录Coze账号，导出工作流JSON文件，然后使用AI自动化工作流处理器处理")


if __name__ == "__main__":
    main()
