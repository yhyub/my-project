import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import hashlib
import base64
import argparse
import json

# 解析命令行参数
parser = argparse.ArgumentParser(description='Backup project files to PostgreSQL cloud database')
parser.add_argument('--config', type=str, help='Path to JSON config file with database connection details')
parser.add_argument('--host', type=str, help='PostgreSQL host address')
parser.add_argument('--port', type=int, help='PostgreSQL port')
parser.add_argument('--user', type=str, help='PostgreSQL username')
parser.add_argument('--password', type=str, help='PostgreSQL password')
parser.add_argument('--database', type=str, help='PostgreSQL database name')
args = parser.parse_args()

# 从命令行参数或环境变量获取数据库连接配置
DB_CONFIG = {
    'host': args.host or os.environ.get('POSTGRES_HOST'),
    'port': args.port or int(os.environ.get('POSTGRES_PORT', 5432)),
    'user': args.user or os.environ.get('POSTGRES_USER'),
    'password': args.password or os.environ.get('POSTGRES_PASSWORD'),
    'database': args.database or os.environ.get('POSTGRES_DATABASE')
}

# 从配置文件加载配置（如果提供）
if args.config:
    with open(args.config, 'r') as f:
        config_file = json.load(f)
        DB_CONFIG.update(config_file)

# 验证必要的配置项
required_configs = ['host', 'user', 'password', 'database']
missing_configs = [cfg for cfg in required_configs if not DB_CONFIG[cfg]]
if missing_configs:
    print(f"缺少必要的数据库配置: {', '.join(missing_configs)}")
    print("请通过命令行参数、环境变量或配置文件提供这些信息")
    print("示例命令行用法:")
    print("python backup_to_postgres.py --host your-host --user your-user --password your-password --database your-db")
    exit(1)

# 要备份的项目文件夹路径
PROJECT_PATH = 'C:\Users\Administrator\Desktop\项目'

# 创建数据库连接
print("正在连接到PostgreSQL数据库...")
conn = psycopg2.connect(**DB_CONFIG)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor = conn.cursor()

# 创建文件表
try:
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS files (
        id SERIAL PRIMARY KEY,
        file_path TEXT NOT NULL UNIQUE,
        file_name TEXT NOT NULL,
        file_size BIGINT NOT NULL,
        file_type TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        modified_at TIMESTAMP NOT NULL,
        file_hash TEXT NOT NULL,
        file_content BYTEA
    )
    ''')
    print("文件表创建成功")
except Exception as e:
    print(f"创建文件表时出错: {e}")
    exit(1)

# 创建文件夹表
try:
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS folders (
        id SERIAL PRIMARY KEY,
        folder_path TEXT NOT NULL UNIQUE,
        folder_name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        modified_at TIMESTAMP NOT NULL
    )
    ''')
    print("文件夹表创建成功")
except Exception as e:
    print(f"创建文件夹表时出错: {e}")
    exit(1)

# 遍历文件夹并备份
def backup_folder(folder_path):
    print(f"正在备份文件夹: {folder_path}")
    
    # 获取文件夹信息
    folder_name = os.path.basename(folder_path)
    modified_time = os.path.getmtime(folder_path)
    modified_at = psycopg2.TimestampFromTicks(modified_time)
    
    # 插入文件夹记录
    try:
        cursor.execute('''
        INSERT INTO folders (folder_path, folder_name, modified_at)
        VALUES (%s, %s, %s)
        ON CONFLICT (folder_path) DO UPDATE
        SET folder_name = EXCLUDED.folder_name,
            modified_at = EXCLUDED.modified_at
        ''', (folder_path, folder_name, modified_at))
    except Exception as e:
        print(f"备份文件夹 {folder_path} 时出错: {e}")
        return
    
    # 遍历文件夹中的文件和子文件夹
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        
        if os.path.isdir(item_path):
            # 递归备份子文件夹
            backup_folder(item_path)
        else:
            # 备份文件
            backup_file(item_path)

def backup_file(file_path):
    print(f"正在备份文件: {file_path}")
    
    try:
        # 获取文件信息
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_type = os.path.splitext(file_path)[1].lower() if '.' in file_path else 'unknown'
        modified_time = os.path.getmtime(file_path)
        modified_at = psycopg2.TimestampFromTicks(modified_time)
        
        # 计算文件哈希
        with open(file_path, 'rb') as f:
            file_content = f.read()
            file_hash = hashlib.sha256(file_content).hexdigest()
        
        # 插入或更新文件记录
        cursor.execute('''
        INSERT INTO files (file_path, file_name, file_size, file_type, modified_at, file_hash, file_content)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (file_path) DO UPDATE
        SET file_name = EXCLUDED.file_name,
            file_size = EXCLUDED.file_size,
            file_type = EXCLUDED.file_type,
            modified_at = EXCLUDED.modified_at,
            file_hash = EXCLUDED.file_hash,
            file_content = EXCLUDED.file_content
        ''', (file_path, file_name, file_size, file_type, modified_at, file_hash, file_content))
        
    except Exception as e:
        print(f"备份文件 {file_path} 时出错: {e}")

# 开始备份
print("开始备份项目文件夹...")
backup_folder(PROJECT_PATH)

# 提交事务并关闭连接
conn.commit()
cursor.close()
conn.close()

print("备份完成！")