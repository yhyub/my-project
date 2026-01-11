import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any

class ZeroDBConfigurer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ZeroDB 配置工具")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # 配置文件路径
        self.config_path = "config.json"
        # 默认配置
        self.default_config = {
            "server": {
                "port": 3306,
                "host": "127.0.0.1",
                "max_connections": 10,
                "idle_timeout": 300,
                "thread_pool_size": 1
            },
            "storage": {
                "engine": "sqlite",
                "path": ":memory:",
                "sync_interval": 3600,
                "cache_size": 100,
                "journal_mode": "WAL",
                "synchronous": "OFF"
            },
            "mysql": {
                "version": "8.0.32",
                "charset": "utf8mb4",
                "collation": "utf8mb4_unicode_ci",
                "skip_networking": False
            },
            "resource": {
                "max_memory_mb": 10,
                "max_cpu_percent": 5,
                "dynamic_allocation": True,
                "idle_resource_release": True,
                "release_delay_seconds": 30
            },
            "logging": {
                "level": "error",
                "file": None,
                "console": False
            }
        }
        
        # 当前配置
        self.current_config = self._load_config()
        
        # 创建UI
        self._create_ui()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 合并默认配置
                self._merge_config(self.default_config, config)
                return self.default_config
            except Exception as e:
                messagebox.showerror("错误", f"无法加载配置文件: {e}")
                return self.default_config.copy()
        else:
            return self.default_config.copy()
    
    def _merge_config(self, default: Dict[str, Any], user: Dict[str, Any]) -> None:
        """递归合并配置"""
        for key, value in user.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_config(default[key], value)
            else:
                default[key] = value
    
    def _save_config(self) -> None:
        """保存配置文件"""
        try:
            # 从UI获取配置
            self._get_config_from_ui()
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_config, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("成功", "配置已保存！")
        except Exception as e:
            messagebox.showerror("错误", f"无法保存配置: {e}")
    
    def _create_ui(self) -> None:
        """创建UI界面"""
        # 创建笔记本（标签页）
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 服务器配置页
        server_frame = ttk.Frame(notebook)
        notebook.add(server_frame, text="服务器配置")
        self._create_server_config(server_frame)
        
        # 存储配置页
        storage_frame = ttk.Frame(notebook)
        notebook.add(storage_frame, text="存储配置")
        self._create_storage_config(storage_frame)
        
        # 资源配置页
        resource_frame = ttk.Frame(notebook)
        notebook.add(resource_frame, text="资源配置")
        self._create_resource_config(resource_frame)
        
        # 保存按钮
        save_btn = ttk.Button(self.root, text="保存配置", command=self._save_config)
        save_btn.pack(pady=10)
    
    def _create_server_config(self, parent: ttk.Frame) -> None:
        """创建服务器配置界面"""
        frame = ttk.LabelFrame(parent, text="服务器设置", padding=10)
        frame.pack(fill=tk.X, expand=True, padx=10, pady=10)
        
        # 端口
        ttk.Label(frame, text="端口: ").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.port_var = tk.IntVar(value=self.current_config['server']['port'])
        ttk.Entry(frame, textvariable=self.port_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 主机
        ttk.Label(frame, text="主机: ").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.host_var = tk.StringVar(value=self.current_config['server']['host'])
        ttk.Entry(frame, textvariable=self.host_var, width=20).grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # 最大连接数
        ttk.Label(frame, text="最大连接数: ").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.max_connections_var = tk.IntVar(value=self.current_config['server']['max_connections'])
        ttk.Entry(frame, textvariable=self.max_connections_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 空闲超时
        ttk.Label(frame, text="空闲超时(秒): ").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.idle_timeout_var = tk.IntVar(value=self.current_config['server']['idle_timeout'])
        ttk.Entry(frame, textvariable=self.idle_timeout_var, width=10).grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
    
    def _create_storage_config(self, parent: ttk.Frame) -> None:
        """创建存储配置界面"""
        frame = ttk.LabelFrame(parent, text="存储设置", padding=10)
        frame.pack(fill=tk.X, expand=True, padx=10, pady=10)
        
        # 存储路径
        ttk.Label(frame, text="存储路径: ").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.storage_path_var = tk.StringVar(value=self.current_config['storage']['path'])
        ttk.Entry(frame, textvariable=self.storage_path_var, width=40).grid(row=0, column=1, columnspan=3, sticky=tk.W, padx=5, pady=5)
        
        # 缓存大小
        ttk.Label(frame, text="缓存大小: ").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.cache_size_var = tk.IntVar(value=self.current_config['storage']['cache_size'])
        ttk.Entry(frame, textvariable=self.cache_size_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 日志模式
        ttk.Label(frame, text="日志模式: ").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.journal_mode_var = tk.StringVar(value=self.current_config['storage']['journal_mode'])
        ttk.Combobox(frame, textvariable=self.journal_mode_var, values=["DELETE", "TRUNCATE", "PERSIST", "MEMORY", "WAL", "OFF"], width=10).grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        
        # 同步模式
        ttk.Label(frame, text="同步模式: ").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.synchronous_var = tk.StringVar(value=self.current_config['storage']['synchronous'])
        ttk.Combobox(frame, textvariable=self.synchronous_var, values=["OFF", "NORMAL", "FULL"], width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
    
    def _create_resource_config(self, parent: ttk.Frame) -> None:
        """创建资源配置界面"""
        frame = ttk.LabelFrame(parent, text="资源设置", padding=10)
        frame.pack(fill=tk.X, expand=True, padx=10, pady=10)
        
        # 最大内存
        ttk.Label(frame, text="最大内存(MB): ").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.max_memory_var = tk.IntVar(value=self.current_config['resource']['max_memory_mb'])
        ttk.Entry(frame, textvariable=self.max_memory_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 最大CPU使用率
        ttk.Label(frame, text="最大CPU使用率(%): ").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.max_cpu_var = tk.IntVar(value=self.current_config['resource']['max_cpu_percent'])
        ttk.Entry(frame, textvariable=self.max_cpu_var, width=10).grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # 动态分配
        ttk.Label(frame, text="动态资源分配: ").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.dynamic_allocation_var = tk.BooleanVar(value=self.current_config['resource']['dynamic_allocation'])
        ttk.Checkbutton(frame, variable=self.dynamic_allocation_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 空闲资源释放
        ttk.Label(frame, text="空闲资源释放: ").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.idle_release_var = tk.BooleanVar(value=self.current_config['resource']['idle_resource_release'])
        ttk.Checkbutton(frame, variable=self.idle_release_var).grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        
        # 释放延迟
        ttk.Label(frame, text="释放延迟(秒): ").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.release_delay_var = tk.IntVar(value=self.current_config['resource']['release_delay_seconds'])
        ttk.Entry(frame, textvariable=self.release_delay_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
    
    def _get_config_from_ui(self) -> None:
        """从UI获取配置"""
        # 服务器配置
        self.current_config['server']['port'] = self.port_var.get()
        self.current_config['server']['host'] = self.host_var.get()
        self.current_config['server']['max_connections'] = self.max_connections_var.get()
        self.current_config['server']['idle_timeout'] = self.idle_timeout_var.get()
        
        # 存储配置
        self.current_config['storage']['path'] = self.storage_path_var.get()
        self.current_config['storage']['cache_size'] = self.cache_size_var.get()
        self.current_config['storage']['journal_mode'] = self.journal_mode_var.get()
        self.current_config['storage']['synchronous'] = self.synchronous_var.get()
        
        # 资源配置
        self.current_config['resource']['max_memory_mb'] = self.max_memory_var.get()
        self.current_config['resource']['max_cpu_percent'] = self.max_cpu_var.get()
        self.current_config['resource']['dynamic_allocation'] = self.dynamic_allocation_var.get()
        self.current_config['resource']['idle_resource_release'] = self.idle_release_var.get()
        self.current_config['resource']['release_delay_seconds'] = self.release_delay_var.get()
    
    def run(self) -> None:
        """运行配置工具"""
        self.root.mainloop()

if __name__ == "__main__":
    configurer = ZeroDBConfigurer()
    configurer.run()
