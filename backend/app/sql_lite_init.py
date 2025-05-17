import sqlite3

# 假设你的数据库文件名为 config.db
# DATABASE_FILE = 'config.db'

from DB import DATABASE_FILE


def init_db():
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS node_configs (
            flow_id TEXT,
            node_id TEXT,
            config_name TEXT,
            config_param TEXT,
            PRIMARY KEY (flow_id, node_id, config_name)
        )
    ''')

    # 创建 nodes 表
    c.execute('''
        CREATE TABLE IF NOT EXISTS nodes (
            id TEXT PRIMARY KEY,
            type TEXT,
            created_at TEXT
        )
    ''')

    # dependencies 表
    c.execute('''
        CREATE TABLE IF NOT EXISTS dependencies (
            source TEXT NOT NULL,
            target TEXT NOT NULL,
            PRIMARY KEY (source, target)
        )
    ''')

    conn.commit()
    conn.close()


init_db()
