#!/usr/bin/env python3
"""
处理Coze工作流URL，获取工作流数据并进行分析和修复
"""

import os
import sys
import json
import requests

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入工作流处理器
from ai_automated_workflow_processor import AIWorkflowProcessor

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
            print(f"   修复后错误数量: {fix_result['final_errors']}")
            print(f"   修复后警告数量: {fix_result['final_warnings']}")
            
            # 保存修复后的工作流
            with open("repaired_coze_workflow.json", "w", encoding="utf-8") as f:
                json.dump(fix_result["repaired_workflow"], f, ensure_ascii=False, indent=2)
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
