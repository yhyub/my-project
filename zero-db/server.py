import json
import os
import signal
import sys
import threading
import time
from typing import Any, Dict, Optional

from sqlite_engine import SQLiteEngine
from mysql_protocol import MySQLProtocol
from resource_manager import ResourceManager

class ZeroDBServer:
    def __init__(self, config_path: str = 'config.json'):
        """初始化ZeroDB服务器"""
        self.config_path = config_path
        self.config = self._load_config()
        self._running = False
        self._storage_engine: Optional[SQLiteEngine] = None
        self._mysql_protocol: Optional[MySQLProtocol] = None
        self._resource_manager: Optional[ResourceManager] = None
        self._shutdown_lock = threading.Lock()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
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
        
        # 如果配置文件存在，加载并合并
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                # 递归合并配置
                self._merge_config(default_config, user_config)
            except Exception as e:
                print(f"警告: 无法加载配置文件 {self.config_path}, 使用默认配置")
        
        return default_config
    
    def _merge_config(self, default: Dict[str, Any], user: Dict[str, Any]) -> None:
        """递归合并配置"""
        for key, value in user.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_config(default[key], value)
            else:
                default[key] = value
    
    def start(self):
        """启动服务器"""
        with self._shutdown_lock:
            if self._running:
                return
            self._running = True
        
        # 注册信号处理
        self._register_signals()
        
        print("启动ZeroDB服务器...")
        print(f"配置: {json.dumps(self.config, indent=2, ensure_ascii=False)}")
        
        # 初始化存储引擎
        print("初始化存储引擎...")
        self._storage_engine = SQLiteEngine(self.config['storage'])
        
        # 初始化资源管理器
        print("初始化资源管理器...")
        self._resource_manager = ResourceManager(self.config['resource'])
        self._resource_manager.start()
        
        # 初始化MySQL协议服务
        print("初始化MySQL协议服务...")
        self._mysql_protocol = MySQLProtocol(self._storage_engine, self.config['server'])
        self._mysql_protocol.start()
        
        print(f"ZeroDB服务器已启动，监听 {self.config['server']['host']}:{self.config['server']['port']}")
        print("按 Ctrl+C 停止服务器")
        
        # 启动监控线程
        threading.Thread(target=self._monitor_server, daemon=True).start()
        
        # 主线程保持运行
        try:
            while self._running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n接收到停止信号，正在停止服务器...")
            self.stop()
    
    def stop(self):
        """停止服务器"""
        with self._shutdown_lock:
            if not self._running:
                return
            self._running = False
        
        print("正在停止ZeroDB服务器...")
        
        # 停止MySQL协议服务
        if self._mysql_protocol:
            self._mysql_protocol.stop()
            self._mysql_protocol = None
        
        # 停止资源管理器
        if self._resource_manager:
            self._resource_manager.stop()
            self._resource_manager = None
        
        # 关闭存储引擎
        if self._storage_engine:
            self._storage_engine.close()
            self._storage_engine = None
        
        print("ZeroDB服务器已停止")
    
    def _register_signals(self):
        """注册信号处理"""
        def signal_handler(sig, frame):
            print(f"\n接收到信号 {sig}，正在停止服务器...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def _monitor_server(self):
        """监控服务器状态"""
        while self._running:
            try:
                # 定期更新资源管理器活动时间
                if self._resource_manager:
                    self._resource_manager.update_activity()
                time.sleep(5)
            except Exception as e:
                time.sleep(5)

if __name__ == "__main__":
    # 运行服务器
    server = ZeroDBServer()
    server.start()