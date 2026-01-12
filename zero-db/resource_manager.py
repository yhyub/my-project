import os
import threading
import time
import gc
from typing import Any, Dict, Optional

class ResourceManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._last_activity_time = time.time()
    
    def start(self):
        """启动资源管理器"""
        if not self._running:
            self._running = True
            # 启动资源监控线程
            self._monitor_thread = threading.Thread(
                target=self._monitor_resources,
                daemon=True
            )
            self._monitor_thread.start()
    
    def stop(self):
        """停止资源管理器"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
            self._monitor_thread = None
    
    def update_activity(self):
        """更新最后活动时间"""
        self._last_activity_time = time.time()
    
    def _monitor_resources(self):
        """监控和调整资源使用"""
        while self._running:
            try:
                # 检查是否空闲，释放资源
                idle_time = time.time() - self._last_activity_time
                if (self.config['idle_resource_release'] and 
                    idle_time > self.config['release_delay_seconds']):
                    self._release_idle_resources()
                
                time.sleep(1)  # 每秒检查一次
            except Exception as e:
                time.sleep(1)
    
    def _release_memory(self):
        """释放内存资源"""
        try:
            # 尝试释放Python内存
            gc.collect()
        except Exception as e:
            pass
    
    def _throttle_cpu(self):
        """限制CPU使用"""
        try:
            # 简单的CPU限制方法：短暂休眠
            time.sleep(0.01)
        except Exception as e:
            pass
    
    def _release_idle_resources(self):
        """释放空闲资源"""
        try:
            # 触发垃圾回收
            gc.collect(2)  # 深度垃圾回收
        except Exception as e:
            pass
    
    def get_resource_usage(self) -> Dict[str, float]:
        """获取当前资源使用情况"""
        try:
            # 使用Python内置方法获取内存使用
            import sys
            memory_mb = sys.getsizeof(self) / (1024 * 1024)  # 简化的内存使用计算
            return {
                'memory_mb': memory_mb,
                'cpu_percent': 0.0,  # 不使用psutil，无法获取CPU使用率
                'threads': threading.active_count(),
                'uptime_seconds': time.time() - self._last_activity_time
            }
        except Exception as e:
            return {
                'memory_mb': 0.0,
                'cpu_percent': 0.0,
                'threads': threading.active_count(),
                'uptime_seconds': time.time() - self._last_activity_time
            }