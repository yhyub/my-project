import os
import psycopg2
import argparse
import json

# 解析命令行参数
parser = argparse.ArgumentParser(description='Test PostgreSQL connection')
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
    exit(1)

# 测试数据库连接
try:
    print("正在连接到PostgreSQL数据库...")
    conn = psycopg2.connect(**DB_CONFIG)
    print("连接成功！")
    
    # 执行简单查询
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"PostgreSQL版本: {version}")
    
    # 关闭连接
    cursor.close()
    conn.close()
    print("连接已关闭")
    
except Exception as e:
    print(f"连接失败: {e}")
    exit(1)

print("测试完成！")