#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZeroDB - 自包含的零占用数据库服务
无需安装任何客户端，直接通过浏览器使用
"""

import sqlite3
import socket
import threading
import time
import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class ZeroDB:
    """零占用数据库主类"""
    def __init__(self, db_path=":memory:"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._init_tables()
        self._lock = threading.Lock()
    
    def _init_tables(self):
        """初始化表结构"""
        # 用户表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # AI调用记录表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_calls (
            call_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            prompt TEXT NOT NULL,
            response TEXT NOT NULL,
            model TEXT NOT NULL,
            tokens_used INTEGER,
            cost REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        ''')
        
        # 用户会话表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        ''')
        self.conn.commit()
    
    def execute(self, sql, params=()):
        """执行SQL语句"""
        with self._lock:
            try:
                self.cursor.execute(sql, params)
                self.conn.commit()
                return True
            except Exception as e:
                print(f"SQL执行错误: {e}")
                self.conn.rollback()
                return False
    
    def fetchall(self, sql, params=()):
        """执行查询并返回所有结果"""
        with self._lock:
            try:
                self.cursor.execute(sql, params)
                return self.cursor.fetchall(), [desc[0] for desc in self.cursor.description]
            except Exception as e:
                print(f"查询错误: {e}")
                return [], []
    
    def fetchone(self, sql, params=()):
        """执行查询并返回一条结果"""
        with self._lock:
            try:
                self.cursor.execute(sql, params)
                return self.cursor.fetchone()
            except Exception as e:
                print(f"查询错误: {e}")
                return None
    
    def backup(self, backup_path):
        """备份数据库"""
        if self.db_path != ":memory:":
            try:
                import shutil
                shutil.copy2(self.db_path, backup_path)
                return True
            except Exception as e:
                print(f"备份错误: {e}")
                return False
        return True
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    """简单HTTP请求处理器"""
    
    def __init__(self, *args, **kwargs):
        self.zero_db = ZeroDB(":memory:")
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """处理GET请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)
        
        # 首页
        if path == '/':
            self._send_html_response(self._get_index_page())
        
        # API端点
        elif path == '/api/users':
            self._handle_get_users(query)
        
        elif path == '/api/ai_calls':
            self._handle_get_ai_calls(query)
        
        elif path == '/api/stats':
            self._handle_get_stats()
        
        # 静态文件
        elif path == '/style.css':
            self._send_css_response()
        
        else:
            self._send_404()
    
    def do_POST(self):
        """处理POST请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # 读取请求体
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
        except:
            data = {}
        
        if path == '/api/users':
            self._handle_create_user(data)
        
        elif path == '/api/ai_calls':
            self._handle_create_ai_call(data)
        
        elif path == '/api/query':
            self._handle_sql_query(data)
        
        else:
            self._send_404()
    
    def _send_html_response(self, content):
        """发送HTML响应"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))
    
    def _send_json_response(self, data):
        """发送JSON响应"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def _send_css_response(self):
        """发送CSS响应"""
        css = '''
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f0f2f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #1a73e8;
        }
        .section {
            margin: 20px 0;
        }
        .form-group {
            margin: 10px 0;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input, textarea, select {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background-color: #1a73e8;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #1557b0;
        }
        .table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }
        .table th, .table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        .table th {
            background-color: #f5f5f5;
        }
        .table tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .alert {
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
        }
        .alert.success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .alert.error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        '''
        self.send_response(200)
        self.send_header('Content-type', 'text/css')
        self.end_headers()
        self.wfile.write(css.encode('utf-8'))
    
    def _send_404(self):
        """发送404响应"""
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<h1>404 Not Found</h1>')
    
    def _get_index_page(self):
        """生成首页HTML"""
        # 获取统计数据
        stats = self._get_stats()
        
        # 获取最近的AI调用
        ai_calls, _ = self.zero_db.fetchall("SELECT * FROM ai_calls ORDER BY created_at DESC LIMIT 10")
        
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>ZeroDB - 零占用数据库</title>
            <link rel="stylesheet" href="/style.css">
        </head>
        <body>
            <div class="container">
                <h1>ZeroDB - 零占用数据库</h1>
                
                <div class="section">
                    <h2>📊 统计信息</h2>
                    <div class="stats">
                        <div style="display: inline-block; margin: 0 20px;">
                            <strong>用户数:</strong> {stats['user_count']}
                        </div>
                        <div style="display: inline-block; margin: 0 20px;">
                            <strong>AI调用次数:</strong> {stats['ai_call_count']}
                        </div>
                        <div style="display: inline-block; margin: 0 20px;">
                            <strong>总花费:</strong> ${stats['total_cost']:.2f}
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>🤖 最近AI调用</h2>
                    <table class="table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>用户ID</th>
                                <th>模型</th>
                                <th>花费</th>
                                <th>时间</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([f'<tr><td>{call[0]}</td><td>{call[1]}</td><td>{call[4]}</td><td>${call[6]:.4f}</td><td>{call[7]}</td></tr>' for call in ai_calls])}
                        </tbody>
                    </table>
                </div>
                
                <div class="section">
                    <h2>➕ 创建用户</h2>
                    <form id="userForm">
                        <div class="form-group">
                            <label for="username">用户名:</label>
                            <input type="text" id="username" name="username" required>
                        </div>
                        <div class="form-group">
                            <label for="email">邮箱:</label>
                            <input type="email" id="email" name="email" required>
                        </div>
                        <button type="submit">创建用户</button>
                    </form>
                    <div id="userMessage" class="alert"></div>
                </div>
                
                <div class="section">
                    <h2>📝 记录AI调用</h2>
                    <form id="aiCallForm">
                        <div class="form-group">
                            <label for="userId">用户ID:</label>
                            <input type="number" id="userId" name="userId" value="1" required>
                        </div>
                        <div class="form-group">
                            <label for="prompt">提示:</label>
                            <textarea id="prompt" name="prompt" rows="3" required></textarea>
                        </div>
                        <div class="form-group">
                            <label for="response">响应:</label>
                            <textarea id="response" name="response" rows="3" required></textarea>
                        </div>
                        <div class="form-group">
                            <label for="model">模型:</label>
                            <input type="text" id="model" name="model" value="gpt-3.5-turbo" required>
                        </div>
                        <div class="form-group">
                            <label for="cost">花费:</label>
                            <input type="number" id="cost" name="cost" step="0.0001" value="0.002">
                        </div>
                        <button type="submit">记录AI调用</button>
                    </form>
                    <div id="aiMessage" class="alert"></div>
                </div>
                
                <div class="section">
                    <h2>🔍 SQL查询</h2>
                    <form id="queryForm">
                        <div class="form-group">
                            <label for="sqlQuery">SQL查询:</label>
                            <textarea id="sqlQuery" name="sql" rows="3" placeholder="SELECT * FROM ai_calls LIMIT 10;"></textarea>
                        </div>
                        <button type="submit">执行查询</button>
                    </form>
                    <div id="queryResult"></div>
                </div>
            </div>
            
            <script>
                // 用户表单提交
                document.getElementById('userForm').addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const formData = new FormData(e.target);
                    const data = Object.fromEntries(formData);
                    
                    const response = await fetch('/api/users', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    const messageEl = document.getElementById('userMessage');
                    messageEl.className = 'alert ' + (result.success ? 'success' : 'error');
                    messageEl.textContent = result.message;
                });
                
                // AI调用表单提交
                document.getElementById('aiCallForm').addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const formData = new FormData(e.target);
                    const data = Object.fromEntries(formData);
                    
                    // 转换数值类型
                    data.userId = parseInt(data.userId);
                    data.cost = parseFloat(data.cost);
                    
                    const response = await fetch('/api/ai_calls', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    const messageEl = document.getElementById('aiMessage');
                    messageEl.className = 'alert ' + (result.success ? 'success' : 'error');
                    messageEl.textContent = result.message;
                    
                    if (result.success) {
                        e.target.reset();
                        // 刷新页面
                        setTimeout(() => location.reload(), 1000);
                    }
                });
                
                // SQL查询表单
                document.getElementById('queryForm').addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const sql = document.getElementById('sqlQuery').value;
                    
                    const response = await fetch('/api/query', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ sql: sql })
                    });
                    
                    const result = await response.json();
                    const resultEl = document.getElementById('queryResult');
                    
                    if (result.success) {
                        let html = '<h3>查询结果</h3>';
                        if (result.data && result.data.length > 0) {
                            html += '<table class="table">';
                            // 添加表头
                            html += '<thead><tr>';
                            for (const key in result.data[0]) {
                                html += `<th>${key}</th>`;
                            }
                            html += '</tr></thead>';
                            
                            // 添加数据行
                            html += '<tbody>';
                            result.data.forEach(row => {
                                html += '<tr>';
                                for (const key in row) {
                                    html += `<td>${row[key]}</td>`;
                                }
                                html += '</tr>';
                            });
                            html += '</tbody></table>';
                        } else {
                            html += '<p>查询成功，但没有返回数据</p>';
                        }
                        resultEl.innerHTML = html;
                    } else {
                        resultEl.innerHTML = `<div class="alert error">查询失败: ${result.error}</div>`;
                    }
                });
            </script>
        </body>
        </html>
        '''
    
    def _get_stats(self):
        """获取统计信息"""
        # 用户数
        users, _ = self.zero_db.fetchall("SELECT COUNT(*) FROM users")
        user_count = users[0][0] if users else 0
        
        # AI调用次数
        ai_calls, _ = self.zero_db.fetchall("SELECT COUNT(*) FROM ai_calls")
        ai_call_count = ai_calls[0][0] if ai_calls else 0
        
        # 总花费
        total_cost, _ = self.zero_db.fetchall("SELECT COALESCE(SUM(cost), 0) FROM ai_calls")
        total_cost = total_cost[0][0] if total_cost else 0
        
        return {
            'user_count': user_count,
            'ai_call_count': ai_call_count,
            'total_cost': total_cost
        }
    
    def _handle_get_users(self, query):
        """处理获取用户请求"""
        limit = int(query.get('limit', ['100'])[0])
        users, columns = self.zero_db.fetchall("SELECT * FROM users LIMIT ?", (limit,))
        
        # 转换为字典列表
        users_list = [dict(zip(columns, user)) for user in users]
        self._send_json_response({'success': True, 'data': users_list, 'count': len(users_list)})
    
    def _handle_get_ai_calls(self, query):
        """处理获取AI调用请求"""
        limit = int(query.get('limit', ['100'])[0])
        ai_calls, columns = self.zero_db.fetchall("SELECT * FROM ai_calls ORDER BY created_at DESC LIMIT ?", (limit,))
        
        ai_calls_list = [dict(zip(columns, call)) for call in ai_calls]
        self._send_json_response({'success': True, 'data': ai_calls_list, 'count': len(ai_calls_list)})
    
    def _handle_get_stats(self):
        """处理获取统计请求"""
        stats = self._get_stats()
        self._send_json_response({'success': True, 'data': stats})
    
    def _handle_create_user(self, data):
        """处理创建用户请求"""
        username = data.get('username', '')
        email = data.get('email', '')
        
        if not username or not email:
            self._send_json_response({'success': False, 'message': '缺少必要字段'})
            return
        
        success = self.zero_db.execute(
            "INSERT INTO users (username, email) VALUES (?, ?)",
            (username, email)
        )
        
        if success:
            self._send_json_response({'success': True, 'message': '用户创建成功'})
        else:
            self._send_json_response({'success': False, 'message': '创建用户失败'})
    
    def _handle_create_ai_call(self, data):
        """处理创建AI调用请求"""
        user_id = data.get('userId')
        prompt = data.get('prompt', '')
        response = data.get('response', '')
        model = data.get('model', 'default')
        cost = data.get('cost', 0.0)
        
        if not user_id or not prompt or not response:
            self._send_json_response({'success': False, 'message': '缺少必要字段'})
            return
        
        success = self.zero_db.execute(
            "INSERT INTO ai_calls (user_id, prompt, response, model, cost) VALUES (?, ?, ?, ?, ?)",
            (user_id, prompt, response, model, cost)
        )
        
        if success:
            self._send_json_response({'success': True, 'message': 'AI调用记录成功'})
        else:
            self._send_json_response({'success': False, 'message': 'AI调用记录失败'})
    
    def _handle_sql_query(self, data):
        """处理SQL查询请求"""
        sql = data.get('sql', '')
        if not sql:
            self._send_json_response({'success': False, 'error': 'SQL语句为空'})
            return
        
        try:
            results, columns = self.zero_db.fetchall(sql)
            result_list = [dict(zip(columns, row)) for row in results]
            self._send_json_response({'success': True, 'data': result_list, 'count': len(result_list)})
        except Exception as e:
            self._send_json_response({'success': False, 'error': str(e)})

class ZeroDBServer:
    """ZeroDB服务器类"""
    def __init__(self, host='0.0.0.0', port=8080, db_path=':memory:'):
        self.host = host
        self.port = port
        self.db_path = db_path
        self.zero_db = ZeroDB(db_path)
        self.http_server = None
    
    def start(self):
        """启动服务器"""
        # 创建HTTP服务器
        SimpleHTTPRequestHandler.zero_db = self.zero_db
        self.http_server = HTTPServer((self.host, self.port), SimpleHTTPRequestHandler)
        
        print(f"ZeroDB服务器启动成功!")
        print(f"访问地址: http://{self.host}:{self.port}")
        print(f"数据库路径: {self.db_path}")
        print(f"按 Ctrl+C 停止服务器")
        
        try:
            self.http_server.serve_forever()
        except KeyboardInterrupt:
            print("\n服务器已停止")
        
        self.http_server.shutdown()
        self.zero_db.close()
    
    def stop(self):
        """停止服务器"""
        if self.http_server:
            self.http_server.shutdown()
            self.http_server.server_close()
        self.zero_db.close()

if __name__ == "__main__":
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description='ZeroDB服务器')
    parser.add_argument('--host', type=str, default='0.0.0.0')
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--db_path', default=':memory:')
    
    args = parser.parse_args()
    
    # 创建并启动服务器
    server = ZeroDBServer(
        host=args.host,
        port=args.port,
        db_path=args.db_path
    )
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n服务器正在停止...")
        server.stop()
        print("服务器已停止")
