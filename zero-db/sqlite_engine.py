import sqlite3
import time
import threading
from typing import Any, Dict, List, Optional, Tuple

class SQLiteEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._conn: Optional[sqlite3.Connection] = None
        self._cursor: Optional[sqlite3.Cursor] = None
        self._last_used = time.time()
        self._lock = threading.Lock()
        self._init_db()
    
    def _init_db(self):
        """初始化数据库连接，应用优化配置"""
        with self._lock:
            if self._conn is None:
                self._conn = sqlite3.connect(
                    self.config['path'],
                    check_same_thread=False,
                    timeout=5.0
                )
                self._cursor = self._conn.cursor()
                
                # 应用资源优化配置
                self._apply_optimizations()
                
                # 初始化系统表
                self._init_system_tables()
    
    def _apply_optimizations(self):
        """应用SQLite优化配置"""
        optimizations = [
            f"PRAGMA cache_size = {self.config.get('cache_size', 100)}",
            f"PRAGMA journal_mode = {self.config.get('journal_mode', 'WAL')}",
            f"PRAGMA synchronous = {self.config.get('synchronous', 'OFF')}",
            f"PRAGMA temp_store = MEMORY",
            f"PRAGMA mmap_size = 0",
            f"PRAGMA auto_vacuum = NONE",
            f"PRAGMA incremental_vacuum = 0",
            f"PRAGMA busy_timeout = 1000"
        ]
        
        for opt in optimizations:
            self._cursor.execute(opt)
    
    def _init_system_tables(self):
        """初始化系统表"""
        # 创建MySQL兼容的系统表模拟
        system_tables = [
            # 模拟information_schema.tables
            "CREATE TABLE IF NOT EXISTS information_schema_tables (
                TABLE_SCHEMA TEXT,
                TABLE_NAME TEXT,
                TABLE_TYPE TEXT,
                ENGINE TEXT,
                AUTO_INCREMENT INTEGER,
                CREATE_TIME TEXT
            )",
            
            # 模拟information_schema.columns
            "CREATE TABLE IF NOT EXISTS information_schema_columns (
                TABLE_SCHEMA TEXT,
                TABLE_NAME TEXT,
                COLUMN_NAME TEXT,
                DATA_TYPE TEXT,
                COLUMN_TYPE TEXT,
                IS_NULLABLE TEXT,
                COLUMN_DEFAULT TEXT,
                EXTRA TEXT
            )"
        ]
        
        for table_sql in system_tables:
            self._cursor.execute(table_sql)
        self._conn.commit()
    
    def execute(self, query: str, params: Tuple[Any, ...] = ()) -> List[Dict[str, Any]]:
        """执行SQL查询，返回结果"""
        with self._lock:
            self._last_used = time.time()
            
            try:
                self._cursor.execute(query, params)
                
                # 处理不同类型的查询
                if query.strip().upper().startswith(('SELECT', 'PRAGMA')):
                    # 查询语句，返回结果
                    columns = [desc[0] for desc in self._cursor.description or []]
                    results = []
                    for row in self._cursor.fetchall():
                        results.append(dict(zip(columns, row)))
                    return results
                else:
                    # 非查询语句，提交并返回影响行数
                    self._conn.commit()
                    return [{"affected_rows": self._cursor.rowcount}]
            except sqlite3.Error as e:
                # 回滚事务
                if not query.strip().upper().startswith('SELECT'):
                    self._conn.rollback()
                raise e
    
    def close(self):
        """关闭数据库连接"""
        with self._lock:
            if self._cursor:
                self._cursor.close()
                self._cursor = None
            if self._conn:
                self._conn.close()
                self._conn = None
    
    def is_idle(self, idle_time: int = 300) -> bool:
        """检查数据库连接是否空闲"""
        return time.time() - self._last_used > idle_time
    
    def release_resources(self):
        """释放资源"""
        with self._lock:
            if self._cursor:
                # 清空缓存
                self._cursor.execute("PRAGMA shrink_memory")
            self._last_used = time.time()
    
    def __del__(self):
        """析构函数，确保资源释放"""
        self.close()
    
    @property
    def connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        self._init_db()
        return self._conn
    
    @property
    def cursor(self) -> sqlite3.Cursor:
        """获取数据库游标"""
        self._init_db()
        return self._cursor