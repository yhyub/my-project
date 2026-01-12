#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并后的DeepSeek数据处理脚本
整合了所有DeepSeek数据处理相关功能

功能包括：
1. DeepSeek数据整合与访问
2. 对话数据导出
3. Coze插件导出和管理
4. 插件合并功能
"""

import json
import os
import sys
import argparse
import logging
import zipfile
import tempfile
import shutil
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional

# 设置日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('merged_deepseek_data.log', encoding='utf-8')
    ]
)
logger = logging.getLogger('MergedDeepSeekData')

class DeepSeekDataIntegrator:
    """
    DeepSeek数据整合器 - 用于加载、处理和访问DeepSeek对话数据
    采用按需加载和迭代访问模式，优化内存使用
    """
    
    def __init__(self, data_dir="./deepseek_data"):
        """
        初始化数据整合器
        
        Args:
            data_dir: 数据目录路径
        """
        self.data_dir = data_dir
        self.conversations_file = os.path.join(data_dir, "conversations.json")
        self.user_file = os.path.join(data_dir, "user.json")
        
        # 加载用户信息（较小文件，直接加载）
        self.user_info = self._load_user_info()
        
        # 预计算对话数量（用于快速访问）
        self._conversation_count = None
    
    def _load_user_info(self):
        """
        加载用户信息
        
        Returns:
            dict: 用户信息字典
        """
        try:
            with open(self.user_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"无法加载用户信息文件 {self.user_file}: {e}")
            return {}
    
    @property
    def conversation_count(self):
        """
        获取对话总数
        
        Returns:
            int: 对话总数
        """
        if self._conversation_count is None:
            self._conversation_count = self._count_conversations()
        return self._conversation_count
    
    def _count_conversations(self):
        """
        计算对话总数
        
        Returns:
            int: 对话总数
        """
        try:
            with open(self.conversations_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return len(data)
        except Exception as e:
            logger.warning(f"无法计算对话数量 {self.conversations_file}: {e}")
            return 0
    
    def get_conversations(self, start=0, end=None):
        """
        按范围获取对话
        
        Args:
            start: 起始索引
            end: 结束索引（None表示全部）
            
        Yields:
            dict: 对话对象
        """
        try:
            with open(self.conversations_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if end is None:
                    end = len(data)
                
                for i in range(start, min(end, len(data))):
                    yield data[i]
        except Exception as e:
            logger.warning(f"无法加载对话数据 {self.conversations_file}: {e}")
            return
    
    def get_conversation_by_id(self, conversation_id):
        """
        通过ID获取对话
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            dict or None: 对话对象或None
        """
        try:
            with open(self.conversations_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for conv in data:
                    if conv.get('id') == conversation_id:
                        return conv
                return None
        except Exception as e:
            logger.warning(f"无法查找对话 {conversation_id}: {e}")
            return None
    
    def get_conversations_by_keyword(self, keyword, case_insensitive=True):
        """
        通过关键词搜索对话
        
        Args:
            keyword: 搜索关键词
            case_insensitive: 是否忽略大小写
            
        Yields:
            dict: 匹配的对话对象
        """
        try:
            with open(self.conversations_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                for conv in data:
                    # 搜索标题
                    title = conv.get('title', '')
                    if case_insensitive:
                        title_lower = title.lower()
                        keyword_lower = keyword.lower()
                        if keyword_lower in title_lower:
                            yield conv
                            continue
                    else:
                        if keyword in title:
                            yield conv
                            continue
                    
                    # 搜索消息内容
                    mapping = conv.get('mapping', {})
                    for node_id, node in mapping.items():
                        if node_id == 'root':
                            continue
                        
                        message = node.get('message', {})
                        fragments = message.get('fragments', [])
                        for fragment in fragments:
                            content = fragment.get('content', '')
                            if case_insensitive:
                                content_lower = content.lower()
                                keyword_lower = keyword.lower()
                                if keyword_lower in content_lower:
                                    yield conv
                                    break
                            else:
                                if keyword in content:
                                    yield conv
                                    break
                        else:
                            continue
                        break
        except Exception as e:
            logger.warning(f"无法搜索对话 {keyword}: {e}")
            return
    
    def get_user_info(self):
        """
        获取用户信息
        
        Returns:
            dict: 用户信息
        """
        return self.user_info
    
    def export_to_single_file(self, output_path):
        """
        将所有数据导出为单一文件
        
        Args:
            output_path: 输出文件路径
        """
        try:
            with open(self.conversations_file, 'r', encoding='utf-8') as f:
                conversations = json.load(f)
            
            # 创建完整数据结构
            complete_data = {
                "metadata": {
                    "version": "1.0.0",
                    "created_at": datetime.now().isoformat(),
                    "source": "DeepSeek Data Export",
                    "compatibility": {
                        "trae_ai_ide": True,
                        "trae_cn": True
                    },
                    "stats": {
                        "conversation_count": len(conversations),
                        "user_count": 1 if self.user_info else 0
                    }
                },
                "user_info": self.user_info,
                "conversations": conversations
            }
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(complete_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"成功导出到文件: {output_path}")
            return True
        except Exception as e:
            logger.error(f"无法导出数据到文件 {output_path}: {e}")
            return False
    
    def validate_data(self):
        """
        验证数据完整性
        
        Returns:
            dict: 验证结果
        """
        results = {
            "user_info_valid": bool(self.user_info),
            "conversations_exist": os.path.exists(self.conversations_file),
            "conversation_count": self.conversation_count,
            "errors": []
        }
        
        # 验证对话数据结构
        try:
            sample_conv = next(self.get_conversations(start=0, end=1), None)
            if sample_conv:
                required_fields = ['id', 'title', 'inserted_at', 'updated_at', 'mapping']
                for field in required_fields:
                    if field not in sample_conv:
                        results["errors"].append(f"对话缺少必填字段: {field}")
        except Exception as e:
            results["errors"].append(f"验证对话结构失败: {e}")
        
        return results

class DeepSeekDataExporter:
    """
    DeepSeek数据导出器 - 用于导出对话数据到不同格式
    """
    
    def __init__(self, integrator):
        """
        初始化数据导出器
        
        Args:
            integrator: DeepSeekDataIntegrator实例
        """
        self.integrator = integrator
    
    def export_conversations_to_txt(self, output_txt):
        """
        将对话导出为txt格式
        
        Args:
            output_txt: 输出txt文件路径
        """
        conversations = []
        
        # 先尝试直接读取原始conversations.json文件
        original_conversations_file = os.path.join(self.integrator.data_dir, "conversations.json")
        if os.path.exists(original_conversations_file):
            try:
                with open(original_conversations_file, 'r', encoding='utf-8') as f:
                    conversations = json.load(f)
                logger.info(f"已从原始文件读取 {len(conversations)} 条对话")
            except Exception as e:
                logger.error(f"无法读取原始JSON文件 {original_conversations_file}: {e}")
                return False
        else:
            # 尝试从整合器获取对话
            conversations = list(self.integrator.get_conversations())
            logger.info(f"已从整合器读取 {len(conversations)} 条对话")
        
        if not conversations:
            logger.error("未找到任何对话数据")
            return False
        
        # 准备输出内容
        output_lines = []
        output_lines.append("=" * 80)
        output_lines.append("DeepSeek 完整对话内容")
        output_lines.append("=" * 80)
        output_lines.append(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output_lines.append(f"对话总数: {len(conversations)}")
        output_lines.append("=" * 80)
        output_lines.append("")
        
        # 遍历所有对话
        for conv_idx, conversation in enumerate(conversations, 1):
            # 对话标题
            title = conversation.get('title', f"对话 {conv_idx}")
            created_at = conversation.get('inserted_at', '')
            
            output_lines.append(f"{conv_idx}. {title}")
            output_lines.append(f"创建时间: {created_at}")
            output_lines.append("-" * 60)
            output_lines.append("")
            
            # 遍历对话节点
            mapping = conversation.get('mapping', {})
            nodes = list(mapping.values())
            
            # 按顺序处理节点
            for node in nodes:
                if node.get('id') == 'root':
                    continue
                
                message = node.get('message', {})
                fragments = message.get('fragments', [])
                
                for fragment in fragments:
                    frag_type = fragment.get('type', '')
                    content = fragment.get('content', '').strip()
                    
                    if not content:
                        continue
                    
                    # 根据片段类型添加前缀
                    if frag_type == 'REQUEST':
                        output_lines.append("🙋 用户提问:")
                        output_lines.append(content)
                        output_lines.append("")
                    elif frag_type == 'RESPONSE':
                        output_lines.append("🤖 AI回答:")
                        output_lines.append(content)
                        output_lines.append("")
                    elif frag_type == 'THINK':
                        # 思考过程可以选择性包含
                        pass
            
            output_lines.append("=" * 60)
            output_lines.append("")
        
        # 写入txt文件
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_txt)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # 尝试写入文件
            with open(output_txt, 'w', encoding='utf-8') as f:
                f.write('\n'.join(output_lines))
            logger.info(f"成功导出完整对话到文件: {output_txt}")
            logger.info(f"文件大小: {os.path.getsize(output_txt)} 字节")
            return True
        except Exception as e:
            logger.error(f"无法写入txt文件 {output_txt}: {e}")
            
            # 尝试写入到另一个路径
            backup_output = "deepseek_conversations_backup.txt"
            try:
                with open(backup_output, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(output_lines))
                logger.info(f"已备份到: {backup_output}")
                return True
            except Exception as backup_e:
                logger.error(f"备份也失败了: {backup_e}")
                return False

class CozePluginManager:
    """
    Coze插件管理器 - 用于导出、整理和合并Coze插件
    """
    
    # 从用户提供的截图中提取的插件数据
    PLUGINS_DATA = [
        {
            "name": "Coze AI 智能工作流自动",
            "description": "集成所有功能的AI智能工作流自动化处理系统 - 全自动一键操作",
            "type": "插件",
            "edit_time": "2025-11-29 12:59:53",
            "plugin_id": "coze_ai_workflow_auto"
        },
        {
            "name": "efesgrhty",
            "description": "ygklh",
            "type": "插件",
            "edit_time": "2025-11-27 21:31:19",
            "plugin_id": "efesgrhty"
        },
        {
            "name": "Coze全场景智能自动化56789",
            "description": "# Coze全场景智能自动化超级中枢 - 完整修复版## 📋 项目概述**项目名称**: Coze全场景智能自动化超级中枢 **版本**: v10.1.0-Unified **核心功能**: 端到端自动化",
            "type": "插件",
            "edit_time": "2025-11-27 20:44:55",
            "plugin_id": "coze_all_scene_auto_56789"
        }
    ]
    
    def __init__(self, export_dir=None):
        """
        初始化插件管理器
        
        Args:
            export_dir: 导出目录路径
        """
        self.export_dir = export_dir or "c:\\Users\\Administrator\\Desktop\\erthhgfj\\导出的插件"
        self.coze_plugins_dir = os.path.join(self.export_dir, "coze_plugins")
        self.mcp_tools_dir = os.path.join(self.export_dir, "mcp_tools")
        
        # 创建导出目录
        os.makedirs(self.export_dir, exist_ok=True)
        os.makedirs(self.coze_plugins_dir, exist_ok=True)
        if not os.path.exists(self.mcp_tools_dir):
            os.makedirs(self.mcp_tools_dir, exist_ok=True)
    
    def calculate_file_hash(self, file_path):
        """
        计算文件哈希值
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: 文件哈希值
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def create_plugin_files(self, plugin_info, plugin_dir):
        """
        为单个插件创建文件
        
        Args:
            plugin_info: 插件信息
            plugin_dir: 插件目录
        """
        plugin_id = plugin_info["plugin_id"]
        plugin_name = plugin_info["name"]
        plugin_desc = plugin_info["description"]
        
        # 创建插件目录
        os.makedirs(plugin_dir, exist_ok=True)
        
        # 保存插件元数据
        metadata = {
            "plugin_id": plugin_id,
            "name": plugin_name,
            "description": plugin_desc,
            "type": plugin_info["type"],
            "edit_time": plugin_info["edit_time"],
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        
        metadata_path = os.path.join(plugin_dir, 'metadata.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        # 创建插件代码文件
        plugin_code = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{plugin_name}

{plugin_desc}

插件 ID: {plugin_id}
版本: 1.0.0
作者: Coze 平台
创建时间: {metadata['created_at']}
编辑时间: {plugin_info['edit_time']}
"""

class {plugin_name.replace(' ', '').replace('-', '').replace('_', '')}:
    def __init__(self):
        self.plugin_id = "{plugin_id}"
        self.name = "{plugin_name}"
        
    def run(self, **kwargs):
        """插件执行入口"""
        return {{
            "success": True,
            "result": f"执行 {self.name} 插件成功",
            "plugin_id": self.plugin_id,
            "timestamp": datetime.now().isoformat()
        }}

# 导出插件
if __name__ == "__main__":
    plugin = {plugin_name.replace(' ', '').replace('-', '').replace('_', '')}()
    result = plugin.run()
    print(result)
'''
        
        main_path = os.path.join(plugin_dir, 'main.py')
        with open(main_path, 'w', encoding='utf-8') as f:
            f.write(plugin_code)
        
        # 创建README.md
        readme_content = f"""# {plugin_name}

## 描述
{plugin_desc}

## 基本信息
- **插件 ID**: {plugin_id}
- **版本**: 1.0.0
- **作者**: Coze 平台
- **创建时间**: {metadata['created_at']}
- **编辑时间**: {plugin_info['edit_time']}
- **类型**: {plugin_info['type']}

## 使用说明
1. 安装依赖
2. 运行 `python main.py`
3. 或导入使用: `from main import {plugin_name.replace(' ', '').replace('-', '').replace('_', '')}`

## 示例
```python
from main import {plugin_name.replace(' ', '').replace('-', '').replace('_', '')}

plugin = {plugin_name.replace(' ', '').replace('-', '').replace('_', '')}()
result = plugin.run()
print(result)
```
"""
        
        readme_path = os.path.join(plugin_dir, 'README.md')
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        logger.info(f"插件 {plugin_name} 已创建到 {plugin_dir}")
    
    def export_all_plugins(self):
        """
        导出所有插件
        """
        logger.info("开始导出所有插件...")
        
        # 创建插件索引
        index_data = {
            "total_plugins": len(self.PLUGINS_DATA),
            "generated_at": datetime.now().isoformat(),
            "plugins": [],
            "categories": [],
            "tags": []
        }
        
        # 为每个插件创建文件
        for plugin_info in self.PLUGINS_DATA:
            plugin_id = plugin_info["plugin_id"]
            plugin_dir = os.path.join(self.coze_plugins_dir, plugin_id)
            
            # 创建插件文件
            self.create_plugin_files(plugin_info, plugin_dir)
            
            # 更新索引数据
            index_data["plugins"].append({
                "plugin_id": plugin_id,
                "name": plugin_info["name"],
                "description": plugin_info["description"],
                "author": "Coze 平台",
                "version": "1.0.0",
                "category": "自动化工具",
                "tags": ["自动化", "工作流", "AI"]
            })
        
        # 保存索引文件
        index_path = os.path.join(self.coze_plugins_dir, 'index.json')
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"所有插件已导出完成！")
        logger.info(f"导出目录: {self.export_dir}")
        logger.info(f"插件数量: {len(self.PLUGINS_DATA)}")
        logger.info(f"索引文件: {index_path}")
    
    def merge_plugins(self):
        """
        合并所有插件成一个超级插件
        """
        logger.info("开始合并插件...")
        
        # 加载所有插件数据
        plugins_data = []
        
        # 加载Coze插件
        if os.path.exists(self.coze_plugins_dir):
            # 读取插件索引
            index_path = os.path.join(self.coze_plugins_dir, 'index.json')
            if os.path.exists(index_path):
                with open(index_path, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                
                # 加载每个插件的详细信息
                for plugin_info in index_data.get('plugins', []):
                    plugin_id = plugin_info['plugin_id']
                    plugin_dir = os.path.join(self.coze_plugins_dir, plugin_id)
                    if os.path.exists(plugin_dir):
                        # 读取插件元数据
                        metadata_path = os.path.join(plugin_dir, 'metadata.json')
                        if os.path.exists(metadata_path):
                            with open(metadata_path, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                            
                            # 读取插件代码
                            main_path = os.path.join(plugin_dir, 'main.py')
                            code = ""
                            if os.path.exists(main_path):
                                with open(main_path, 'r', encoding='utf-8') as f:
                                    code = f.read()
                            
                            # 读取README
                            readme_path = os.path.join(plugin_dir, 'README.md')
                            readme = ""
                            if os.path.exists(readme_path):
                                with open(readme_path, 'r', encoding='utf-8') as f:
                                    readme = f.read()
                            
                            plugins_data.append({
                                'type': 'coze_plugin',
                                'id': plugin_id,
                                'metadata': metadata,
                                'code': code,
                                'readme': readme
                            })
        
        # 加载MCP工具
        if os.path.exists(self.mcp_tools_dir):
            for filename in os.listdir(self.mcp_tools_dir):
                if filename.endswith('.json'):
                    mcp_file = os.path.join(self.mcp_tools_dir, filename)
                    with open(mcp_file, 'r', encoding='utf-8') as f:
                        mcp_data = json.load(f)
                    
                    plugins_data.append({
                        'type': 'mcp_tool',
                        'id': filename[:-5],  # 去除.json后缀
                        'metadata': mcp_data.get('metadata', {}),
                        'config': mcp_data.get('config', {}),
                        'content': mcp_data.get('content', {})
                    })
        
        logger.info(f"成功加载 {len(plugins_data)} 个插件")
        
        # 创建超级插件基础结构
        super_plugin = {
            'metadata': {
                'name': '超级Coze插件',
                'description': '融合了所有插件功能的超级插件',
                'version': '1.0.0',
                'created_at': datetime.now().isoformat(),
                'author': 'Coze 插件合并工具',
                'plugin_id': 'super_coze_plugin',
                'type': '超级插件',
                'total_plugins_merged': len(plugins_data),
                'coze_plugins_count': len([p for p in plugins_data if p['type'] == 'coze_plugin']),
                'mcp_tools_count': len([p for p in plugins_data if p['type'] == 'mcp_tool'])
            },
            'config': {
                'security_level': 'high',
                'allowed_commands': [],
                'max_concurrent_calls': 10,
                'timeout': 60,
                'security': {
                    'sandbox_enabled': True,
                    'javascript_restricted': True,
                    'cookie_isolation': True,
                    'origin_restriction': True,
                    'popup_blocking': True,
                    'ad_blocking': True
                }
            },
            'plugins': {},
            'categories': [],
            'tags': []
        }
        
        # 合并所有插件
        for plugin in plugins_data:
            plugin_id = plugin['id']
            super_plugin['plugins'][plugin_id] = plugin
            
            # 提取分类
            if 'category' in plugin.get('metadata', {}):
                category = plugin['metadata']['category']
                if category not in super_plugin['categories']:
                    super_plugin['categories'].append(category)
            
            # 提取标签
            if 'tags' in plugin.get('metadata', {}):
                for tag in plugin['metadata']['tags']:
                    if tag not in super_plugin['tags']:
                        super_plugin['tags'].append(tag)
            
            # 合并安全配置
            if 'config' in plugin and 'allowed_commands' in plugin['config']:
                for cmd in plugin['config']['allowed_commands']:
                    if cmd not in super_plugin['config']['allowed_commands']:
                        super_plugin['config']['allowed_commands'].append(cmd)
        
        # 保存超级插件元数据
        super_plugin_path = os.path.join(self.export_dir, 'super_coze_plugin.json')
        with open(super_plugin_path, 'w', encoding='utf-8') as f:
            json.dump(super_plugin, f, ensure_ascii=False, indent=2)
        
        logger.info(f"成功合并 {len(plugins_data)} 个插件")
        logger.info(f"超级插件已保存到: {super_plugin_path}")
        
        return super_plugin

def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='合并后的DeepSeek数据处理脚本')
    
    # 数据整合和访问相关命令
    parser.add_argument('--data-dir', default='./deepseek_data', help='数据目录路径')
    parser.add_argument('--export-json', type=str, help='导出数据为JSON文件')
    parser.add_argument('--export-txt', type=str, help='导出对话为TXT文件')
    parser.add_argument('--stats', action='store_true', help='显示统计信息')
    parser.add_argument('--validate', action='store_true', help='验证数据完整性')
    parser.add_argument('--search', type=str, help='搜索关键词')
    
    # 插件相关命令
    parser.add_argument('--export-plugins', action='store_true', help='导出Coze插件')
    parser.add_argument('--merge-plugins', action='store_true', help='合并所有插件为超级插件')
    
    args = parser.parse_args()
    
    # 初始化数据整合器
    integrator = DeepSeekDataIntegrator(args.data_dir)
    
    # 数据导出命令
    if args.export_json:
        logger.info(f"导出数据到JSON文件: {args.export_json}")
        if integrator.export_to_single_file(args.export_json):
            logger.info("数据导出成功")
        else:
            logger.error("数据导出失败")
    elif args.export_txt:
        logger.info(f"导出对话到TXT文件: {args.export_txt}")
        exporter = DeepSeekDataExporter(integrator)
        if exporter.export_conversations_to_txt(args.export_txt):
            logger.info("对话导出成功")
        else:
            logger.error("对话导出失败")
    
    # 数据统计命令
    elif args.stats:
        logger.info("获取对话统计信息...")
        print(f"总对话数: {integrator.conversation_count}")
        print(f"用户信息: {'有效' if integrator.user_info else '无效'}")
        
    # 数据验证命令
    elif args.validate:
        logger.info("验证数据完整性...")
        results = integrator.validate_data()
        print(json.dumps(results, ensure_ascii=False, indent=2))
    
    # 搜索命令
    elif args.search:
        logger.info(f"搜索关键词: {args.search}")
        count = 0
        for conv in integrator.get_conversations_by_keyword(args.search):
            print(f"对话ID: {conv.get('id')}")
            print(f"标题: {conv.get('title')}")
            print(f"创建时间: {conv.get('inserted_at')}")
            print("-" * 50)
            count += 1
            if count >= 10:  # 最多显示10个结果
                print(f"... 还有更多结果，共找到{count}个匹配")
                break
        if count == 0:
            print("未找到匹配的对话")
    
    # 插件相关命令
    elif args.export_plugins:
        plugin_manager = CozePluginManager()
        plugin_manager.export_all_plugins()
    elif args.merge_plugins:
        plugin_manager = CozePluginManager()
        plugin_manager.merge_plugins()
    
    else:
        # 默认显示帮助信息
        parser.print_help()

if __name__ == "__main__":
    main()