#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件分析、分类、整理和合并工具
统一MCP工具 - 整合版
功能：文件分析、分类、整理和合并
作者：自动生成
日期：2025-12-25
"""

import os
import re
import json
import shutil
from collections import defaultdict
import argparse
import datetime
import hashlib

class MCPTool:
    def __init__(self):
        self.desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        
    def analyze_directory(self, source_dir=None, output_file=None):
        """分析目录结构和文件类型"""
        if source_dir is None:
            source_dir = self.current_dir
        if output_file is None:
            output_file = os.path.join(self.current_dir, "dir_analysis.json")
        
        print(f"正在分析目录: {source_dir}")
        
        # 存储目录结构
        result = {
            "root": source_dir,
            "directories": [],
            "files": [],
            "file_types": {}
        }
        
        # 遍历目录
        for dirpath, dirnames, filenames in os.walk(source_dir):
            # 记录目录
            result["directories"].append(dirpath)
            
            # 记录文件和文件类型
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                result["files"].append(full_path)
                
                # 记录文件类型
                ext = os.path.splitext(filename)[1].lower()
                if ext not in result["file_types"]:
                    result["file_types"][ext] = 0
                result["file_types"][ext] += 1
        
        # 输出结果
        print(f"总目录数: {len(result['directories'])}")
        print(f"总文件数: {len(result['files'])}")
        print("文件类型统计:")
        for ext, count in sorted(result['file_types'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {ext}: {count}个文件")
        
        # 保存结果到文件
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n分析结果已保存到 {output_file}")
        return result
    
    def organize_files(self, source_dir=None, output_dir=None):
        """按照文件类型分类和整理文件"""
        if source_dir is None:
            source_dir = self.current_dir
        if output_dir is None:
            output_dir = os.path.join(self.desktop_path, "整理后的文件")
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 定义文件分类规则
        file_categories = {
            "JavaScript": [".js", ".cjs", ".mjs"],
            "TypeScript": [".ts", ".d.ts", ".cts", ".mts", ".d.cts", ".d.mts"],
            "SourceMap": [".map"],
            "Markup": [".html", ".css"],
            "Configuration": ["_no_extension"],  # 无扩展名的文件通常是配置文件
            "Fonts": [".bcmap", ".pfb", ".ttf"],
            "Protocol": [".proto"],
            "Scripts": [".coffee", ".sh"],
            "License": [".bsd", ".apache2", ".mit"],
            "Other": []  # 其他类型
        }
        
        # 反向映射：扩展名 -> 分类
        category_map = {}
        for category, exts in file_categories.items():
            for ext in exts:
                category_map[ext] = category
        
        # 收集并分类所有文件
        print("正在收集和分类文件...")
        category_files = defaultdict(lambda: defaultdict(list))
        
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()
                if not ext:
                    ext = "_no_extension"
                
                # 确定文件分类
                category = category_map.get(ext, "Other")
                
                # 获取文件名（不含扩展名和版本后缀）
                base_name = os.path.splitext(file)[0]
                clean_name = re.sub(r'_\d+$', '', base_name)
                
                # 添加到分类中
                category_files[category][clean_name].append(file_path)
        
        # 统计分类结果
        print("\n文件分类统计:")
        total_files = 0
        for category, name_groups in sorted(category_files.items(), key=lambda x: len(x[1]), reverse=True):
            cat_file_count = sum(len(files) for files in name_groups.values())
            total_files += cat_file_count
            print(f"{category}: {len(name_groups)} 组, {cat_file_count} 个文件")
        
        print(f"\n总文件数: {total_files}")
        
        # 合并文件
        print("\n开始合并文件...")
        for category, name_groups in category_files.items():
            # 创建分类目录
            cat_dir = os.path.join(output_dir, category)
            os.makedirs(cat_dir, exist_ok=True)
            
            # 合并每个名称组的文件
            for name, file_paths in name_groups.items():
                # 创建合并文件路径
                if category == "Configuration":
                    output_file = os.path.join(cat_dir, f"{name}.txt")
                else:
                    # 为JavaScript和TypeScript添加合适的扩展名
                    if category == "JavaScript":
                        output_file = os.path.join(cat_dir, f"{name}.js")
                    elif category == "TypeScript":
                        output_file = os.path.join(cat_dir, f"{name}.ts")
                    else:
                        # 对于其他分类，使用第一个文件的扩展名
                        first_ext = os.path.splitext(os.path.basename(file_paths[0]))[1]
                        output_file = os.path.join(cat_dir, f"{name}{first_ext}")
                
                # 如果文件已存在，跳过
                if os.path.exists(output_file):
                    continue
                
                print(f"合并 {category}/{name} ({len(file_paths)} 个文件)")
                
                with open(output_file, 'w', encoding='utf-8') as out_f:
                    out_f.write(f"{'='*60}\n")
                    out_f.write(f"分类: {category}\n")
                    out_f.write(f"文件名: {name}\n")
                    out_f.write(f"文件数量: {len(file_paths)}\n")
                    out_f.write(f"{'='*60}\n\n")
                    
                    for i, file_path in enumerate(file_paths):
                        file_name = os.path.basename(file_path)
                        out_f.write(f"--- {file_name} (第 {i+1}/{len(file_paths)} 个) ---\n")
                        try:
                            with open(file_path, 'r', encoding='utf-8') as in_f:
                                content = in_f.read()
                                out_f.write(content)
                        except UnicodeDecodeError:
                            try:
                                with open(file_path, 'r', encoding='gbk') as in_f:
                                    content = in_f.read()
                                    out_f.write(content)
                            except Exception as e:
                                out_f.write(f"无法读取文件: {str(e)}")
                        out_f.write("\n\n")
        
        # 创建合并报告
        report_file = os.path.join(output_dir, "整理报告.txt")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("文件整理报告\n")
            f.write(f"{'='*50}\n")
            f.write(f"源目录: {source_dir}\n")
            f.write(f"目标目录: {output_dir}\n")
            f.write(f"总文件数: {total_files}\n")
            f.write(f"文件类型数: {len(category_files)}\n")
            f.write(f"{'='*50}\n\n")
            
            f.write("分类详情:\n")
            for category, name_groups in sorted(category_files.items(), key=lambda x: len(x[1]), reverse=True):
                cat_file_count = sum(len(files) for files in name_groups.values())
                f.write(f"{category}: {len(name_groups)} 组, {cat_file_count} 个文件\n")
            
            f.write(f"\n{'='*50}\n")
            f.write("整理完成！\n")
            f.write("所有文件已按照类型和名称分类合并到目标目录中。\n")
        
        print(f"\n整理完成！")
        print(f"文件已保存到: {output_dir}")
        print(f"整理报告: {report_file}")
        return output_dir
    
    def simple_organize(self, source_dir=None, output_dir=None):
        """简单整理文件，按扩展名合并"""
        if source_dir is None:
            source_dir = self.current_dir
        if output_dir is None:
            output_dir = self.desktop_path
        
        # 定义主要文件类型，只处理常见的重要类型
        main_extensions = [".js", ".ts", ".cjs", ".mjs", ".d.ts", ".map", ".html", ".css"]
        
        print("正在整理文件...")
        
        # 按扩展名分组文件
        extension_files = defaultdict(list)
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()
                if not ext:
                    ext = "_no_ext"
                extension_files[ext].append(file_path)
        
        # 合并每个扩展名的文件
        for ext, files in extension_files.items():
            # 跳过不重要的小文件类型
            if ext not in main_extensions and len(files) < 10:
                continue
            
            # 创建输出文件
            output_file = os.path.join(output_dir, f"整理_{ext[1:] if ext.startswith('.') else ext}.txt")
            print(f"合并 {ext} 文件 ({len(files)} 个) 到 {output_file}")
            
            # 按文件名（不含版本号）分组
            name_groups = defaultdict(list)
            for file_path in files:
                file_name = os.path.basename(file_path)
                base_name = os.path.splitext(file_name)[0]
                clean_name = re.sub(r'_\d+$', '', base_name)
                name_groups[clean_name].append(file_path)
            
            with open(output_file, 'w', encoding='utf-8') as out_f:
                for name, file_paths in sorted(name_groups.items()):
                    out_f.write(f"\n{'='*50}\n")
                    out_f.write(f"文件名组: {name}{ext}\n")
                    out_f.write(f"文件数量: {len(file_paths)}\n")
                    out_f.write(f"{'='*50}\n\n")
                    
                    for i, file_path in enumerate(file_paths):
                        file_name = os.path.basename(file_path)
                        out_f.write(f"--- {file_name} (第 {i+1}/{len(file_paths)} 个) ---\n")
                        try:
                            with open(file_path, 'r', encoding='utf-8') as in_f:
                                content = in_f.read()
                                out_f.write(content)
                        except UnicodeDecodeError:
                            try:
                                with open(file_path, 'r', encoding='gbk') as in_f:
                                    content = in_f.read()
                                    out_f.write(content)
                            except:
                                out_f.write("[无法读取文件内容]")
                        out_f.write("\n\n")
        
        print("\n整理完成！")
        print("已在桌面上生成按类型分类的合并文件。")
        return True
    
    def merge_all_in_one(self, source_dir=None, output_file=None):
        """合并所有文件到一个单一文件"""
        if source_dir is None:
            source_dir = self.current_dir
        if output_file is None:
            output_file = os.path.join(self.current_dir, "merged_all_in_one.txt")
        
        print(f"正在将 {source_dir} 中的所有文件合并到 {output_file}...")
        
        # 计算文件哈希值
        def calculate_hash(file_path):
            hash_md5 = hashlib.md5()
            try:
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b''):
                        hash_md5.update(chunk)
                return hash_md5.hexdigest()
            except:
                return None
        
        # 收集所有文件并分类
        print("收集文件中...")
        file_groups = defaultdict(list)
        total_files = 0
        
        # 首先收集所有文件
        all_files = []
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                all_files.append(file_path)
                total_files += 1
        
        print(f"共收集到 {total_files} 个文件")
        
        # 检测重复文件
        print("检测重复文件中...")
        hash_to_files = defaultdict(list)
        for file_path in all_files:
            file_hash = calculate_hash(file_path)
            if file_hash:
                hash_to_files[file_hash].append(file_path)
        
        # 分类文件：重复和唯一
        unique_files = []
        duplicate_files = []
        for file_hash, files in hash_to_files.items():
            if len(files) > 1:
                duplicate_files.extend(files)
                # 只保留第一个文件
                unique_files.append(files[0])
            else:
                unique_files.append(files[0])
        
        print(f"检测到 {len(duplicate_files)} 个重复文件")
        print(f"保留 {len(unique_files)} 个唯一文件")
        
        # 按扩展名和名称分类唯一文件
        for file_path in unique_files:
            file_name = os.path.basename(file_path)
            # 获取扩展名和基础名称
            ext = os.path.splitext(file_name)[1].lower()
            base_name = os.path.splitext(file_name)[0]
            
            # 去除版本号后缀
            clean_name = re.sub(r'_\d+$', '', base_name)
            
            # 组合键：扩展名 + 基础名称
            group_key = f"{ext}_{clean_name}"
            file_groups[group_key].append((file_name, file_path))
        
        print(f"分类为 {len(file_groups)} 组")
        
        # 写入合并文件
        print(f"写入合并文件 {output_file}...")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as out_f:
                # 写入文件头
                out_f.write("="*80 + "\n")
                out_f.write("MCP工具配置与开发文件 - 所有文件合并\n")
                out_f.write(f"源目录: {source_dir}\n")
                out_f.write(f"合并时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                out_f.write(f"总文件数: {total_files}\n")
                out_f.write(f"重复文件数: {len(duplicate_files)}\n")
                out_f.write(f"唯一文件数: {len(unique_files)}\n")
                out_f.write(f"文件组数: {len(file_groups)}\n")
                out_f.write("="*80 + "\n\n")
                
                # 按组写入文件内容
                written_files = 0
                for i, (group_key, file_list) in enumerate(sorted(file_groups.items()), 1):
                    ext, clean_name = group_key.split('_', 1)
                    
                    out_f.write(f"\n{'='*60}\n")
                    out_f.write(f"组 {i}/{len(file_groups)}: {clean_name}{ext}\n")
                    out_f.write(f"文件数量: {len(file_list)}\n")
                    out_f.write(f"{'='*60}\n\n")
                    
                    for j, (file_name, file_path) in enumerate(file_list, 1):
                        out_f.write(f"--- 文件 {j}/{len(file_list)}: {file_name} ---")
                        out_f.write("\n")
                        out_f.write(f"路径: {file_path}\n\n")
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8') as in_f:
                                content = in_f.read()
                                out_f.write(content)
                                written_files += 1
                        except UnicodeDecodeError:
                            try:
                                with open(file_path, 'r', encoding='gbk') as in_f:
                                    content = in_f.read()
                                    out_f.write(content)
                                    written_files += 1
                            except Exception as e:
                                error_msg = f"[无法读取文件内容: {str(e)}]"
                                out_f.write(error_msg)
                                print(f"警告: {error_msg} - {file_path}")
                        except Exception as e:
                            error_msg = f"[读取文件时发生错误: {str(e)}]"
                            out_f.write(error_msg)
                            print(f"错误: {error_msg} - {file_path}")
                    
                    out_f.write("\n\n")
        except Exception as e:
            print(f"\n合并失败！")
            print(f"错误信息: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        file_size = os.path.getsize(output_file)
        print(f"\n合并完成！")
        print(f"输出文件: {output_file}")
        print(f"文件大小: {file_size/1024/1024:.2f} MB")
        print(f"成功写入: {written_files} 个文件")
        print("所有文件已成功合并到一个单一文件中，并按类型和名称分类整理。")
        return True
    
    def run(self, mode="all"):
        """运行主程序"""
        print("统一MCP工具 - 整合版")
        print("="*50)
        print("1. 分析目录结构")
        print("2. 完整整理文件")
        print("3. 简单整理文件")
        print("4. 合并所有文件到一个")
        print("5. 运行所有功能")
        print("="*50)
        
        if mode == "all" or mode == "1":
            self.analyze_directory()
            print()
        
        if mode == "all" or mode == "2":
            self.organize_files()
            print()
        
        if mode == "all" or mode == "3":
            self.simple_organize()
            print()
        
        if mode == "all" or mode == "4":
            self.merge_all_in_one()
            print()
        
        if mode == "all" or mode == "5":
            print("所有功能已运行完成！")
            print("请检查输出文件和目录。")
        
        return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='统一MCP工具 - 整合版')
    parser.add_argument('--mode', choices=['all', '1', '2', '3', '4', '5'], default='all', 
                        help='运行模式：1-分析目录，2-完整整理，3-简单整理，4-合并所有，5-运行所有')
    args = parser.parse_args()
    
    mcp_tool = MCPTool()
    mcp_tool.run(args.mode)

if __name__ == "__main__":
    main()
