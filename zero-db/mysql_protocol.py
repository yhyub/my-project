import socket
import struct
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

class MySQLProtocol:
    def __init__(self, storage_engine, config: Dict[str, Any]):
        self.storage_engine = storage_engine
        self.config = config
        self._clients: Dict[int, socket.socket] = {}
        self._client_lock = threading.Lock()
        self._running = False
        self._server_socket: Optional[socket.socket] = None
    
    def start(self):
        """启动MySQL兼容服务器"""
        self._running = True
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self.config['host'], self.config['port']))
        self._server_socket.listen(self.config['max_connections'])
        self._server_socket.settimeout(0.5)
        
        # 启动客户端处理线程
        threading.Thread(target=self._accept_clients, daemon=True).start()
    
    def stop(self):
        """停止MySQL兼容服务器"""
        self._running = False
        if self._server_socket:
            self._server_socket.close()
        
        # 关闭所有客户端连接
        with self._client_lock:
            for client in self._clients.values():
                try:
                    client.close()
                except:
                    pass
            self._clients.clear()
    
    def _accept_clients(self):
        """接受客户端连接"""
        while self._running:
            try:
                client, addr = self._server_socket.accept()
                client_id = id(client)
                
                with self._client_lock:
                    if len(self._clients) < self.config['max_connections']:
                        self._clients[client_id] = client
                        # 启动客户端处理线程
                        threading.Thread(
                            target=self._handle_client,
                            args=(client, client_id),
                            daemon=True
                        ).start()
                    else:
                        # 拒绝连接，超过最大连接数
                        client.close()
            except socket.timeout:
                continue
            except Exception as e:
                if self._running:
                    print(f"Error accepting client: {e}")
    
    def _handle_client(self, client: socket.socket, client_id: int):
        """处理客户端连接"""
        try:
            # 发送MySQL握手包
            self._send_handshake(client)
            
            # 处理认证
            if not self._handle_auth(client):
                return
            
            # 处理命令循环
            self._handle_commands(client)
        except Exception as e:
            pass
        finally:
            # 关闭客户端连接
            with self._client_lock:
                if client_id in self._clients:
                    del self._clients[client_id]
            try:
                client.close()
            except:
                pass
    
    def _send_handshake(self, client: socket.socket):
        """发送MySQL握手包"""
        # 简化的MySQL握手包
        protocol_version = 10
        server_version = b"8.0.32"
        thread_id = 1
        scramble_buffer = b"" * 8
        filler = b"\x00"
        server_capabilities = struct.pack('<I', 0xffffff)
        server_language = 8
        server_status = 2
        scramble_buffer_ext = b"" * 12
        
        handshake = struct.pack(
            '!B{0}sxB{1}s6xHBB4x{2}s13x'
            .format(len(server_version), len(scramble_buffer), len(scramble_buffer_ext)),
            protocol_version,
            server_version,
            thread_id,
            scramble_buffer,
            server_capabilities[0],
            server_capabilities[1],
            server_language,
            server_status,
            scramble_buffer_ext
        )
        
        client.sendall(handshake)
    
    def _handle_auth(self, client: socket.socket) -> bool:
        """处理客户端认证"""
        # 简化认证，接受任何用户名密码
        try:
            # 接收认证包
            auth_data = self._recv_packet(client)
            if not auth_data:
                return False
            
            # 发送认证成功响应
            success_packet = b"\x07\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00"
            client.sendall(success_packet)
            return True
        except:
            return False
    
    def _handle_commands(self, client: socket.socket):
        """处理客户端命令"""
        while self._running:
            try:
                # 接收命令包
                packet = self._recv_packet(client)
                if not packet:
                    break
                
                # 解析命令
                command = packet[0]
                data = packet[1:]
                
                # 处理不同命令类型
                if command == 0x03:  # COM_QUERY
                    self._handle_query(client, data)
                elif command == 0x01:  # COM_QUIT
                    break
                elif command == 0x00:  # COM_SLEEP
                    continue
                else:
                    # 不支持的命令，返回错误
                    self._send_error(client, 1064, "Command not supported")
            except Exception as e:
                self._send_error(client, 1064, str(e))
    
    def _handle_query(self, client: socket.socket, query_data: bytes):
        """处理查询命令"""
        query = query_data.decode('utf-8', errors='ignore').strip()
        
        try:
            # 执行查询
            results = self.storage_engine.execute(query)
            
            # 发送结果
            if query.upper().startswith('SELECT'):
                self._send_result_set(client, results)
            else:
                self._send_ok_packet(client, results[0]['affected_rows'])
        except Exception as e:
            self._send_error(client, 1064, str(e))
    
    def _send_result_set(self, client: socket.socket, results: List[Dict[str, Any]]):
        """发送结果集"""
        if not results:
            # 空结果集
            self._send_ok_packet(client, 0)
            return
        
        # 发送字段数量
        field_count = len(results[0])
        client.sendall(struct.pack('!B', field_count))
        
        # 发送字段定义（简化）
        for field_name in results[0].keys():
            field_packet = self._build_field_packet(field_name)
            client.sendall(field_packet)
        
        # 发送EOF包
        client.sendall(b"\xfe\x00\x00\x02\x00\x00\x00")
        
        # 发送数据行
        for row in results:
            row_packet = self._build_row_packet(row)
            client.sendall(row_packet)
        
        # 发送EOF包
        client.sendall(b"\xfe\x00\x00\x02\x00\x00\x00")
    
    def _build_field_packet(self, field_name: str) -> bytes:
        """构建字段定义包"""
        # 简化的字段定义
        catalog = b"def"
        schema = b""
        table = b""
        org_table = b""
        name = field_name.encode('utf-8')
        org_name = b""
        
        packet = b"\x03"  # 字段包类型
        packet += struct.pack('B', len(catalog)) + catalog
        packet += struct.pack('B', len(schema)) + schema
        packet += struct.pack('B', len(table)) + table
        packet += struct.pack('B', len(org_table)) + org_table
        packet += struct.pack('B', len(name)) + name
        packet += struct.pack('B', len(org_name)) + org_name
        packet += b"\x0c"  # 填充
        packet += struct.pack('<H', 3)  # 字符集
        packet += struct.pack('<I', 255)  # 列长度
        packet += struct.pack('B', 253)  # 类型（TEXT）
        packet += struct.pack('<H', 0)  # 标志
        packet += struct.pack('B', 0)  # 小数位数
        packet += b"\x00\x00"  # 填充
        
        return packet
    
    def _build_row_packet(self, row: Dict[str, Any]) -> bytes:
        """构建数据行包"""
        packet = b"\x00"  # 行包类型
        
        for value in row.values():
            if value is None:
                packet += b"\xfb"  # NULL值
            else:
                value_str = str(value).encode('utf-8')
                length = len(value_str)
                if length < 251:
                    packet += struct.pack('B', length) + value_str
                elif length < 65536:
                    packet += b"\xfc" + struct.pack('<H', length) + value_str
                elif length < 16777216:
                    packet += b"\xfd" + struct.pack('<I', length)[:3] + value_str
                else:
                    packet += b"\xfe" + struct.pack('<I', length) + value_str
        
        return packet
    
    def _send_ok_packet(self, client: socket.socket, affected_rows: int):
        """发送OK包"""
        ok_packet = b"\x07\x00\x00\x02"
        ok_packet += struct.pack('<I', affected_rows)  # 影响行数
        ok_packet += struct.pack('<I', 0)  # 插入ID
        ok_packet += b"\x00\x00"  # 服务器状态
        ok_packet += b"\x00\x00"  # 警告数
        client.sendall(ok_packet)
    
    def _send_error(self, client: socket.socket, error_code: int, error_msg: str):
        """发送错误包"""
        error_packet = b"\xff"
        error_packet += struct.pack('<H', error_code)  # 错误码
        error_packet += b"#"  # SQL状态标记
        error_packet += b"42000"  # SQL状态
        error_packet += error_msg.encode('utf-8')
        client.sendall(error_packet)
    
    def _recv_packet(self, client: socket.socket) -> Optional[bytes]:
        """接收MySQL数据包"""
        # 接收包头（4字节）
        header = client.recv(4)
        if not header or len(header) < 4:
            return None
        
        # 解析包头
        payload_len = struct.unpack('<I', header[:3] + b'\x00')[0]
        
        # 接收包体
        data = b''
        while len(data) < payload_len:
            chunk = client.recv(payload_len - len(data))
            if not chunk:
                return None
            data += chunk
        
        return data