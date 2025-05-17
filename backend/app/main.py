from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
import json
import sqlite3
from DB import DATABASE_FILE

app = Flask(__name__)
CORS(app)

CONFIG_FILE = 'node_configs.txt'


@app.route('/save_flow', methods=['POST'])
def save_flow():
    data = request.json
    print(f"data: {data}")
    flow_id = data['flow_id']

    # read from flows.txt, if the flow_id is already in the file, update the flow
    exists = False
    with open('flows.txt', 'r') as f:
        for line in f:
            if flow_id in line:
                exists = True
                with open('flows.txt', 'w') as f:
                    f.write(json.dumps(data) + '\n')
                return jsonify({'status': 'ok'})
    # if the flow_id is not in the file, append the flow
    if not exists:
        with open('flows.txt', 'a') as f:
            f.write(json.dumps(data) + '\n')
    return jsonify({'status': 'ok'})


@app.route('/get_flows')
def get_flows():
    try:
        with open('flows.txt') as f:
            flows = [json.loads(line.strip()) for line in f]
        simple_flows = [{"id": f["flow_id"],
                         "nodeCount": len(f["nodes"])} for f in flows]
        return jsonify({'flows': simple_flows})
    except FileNotFoundError:
        return jsonify({'flows': []})


@app.route('/get_flow/<flow_id>')
def get_flow(flow_id):
    print(f"Getting flow with ID: {flow_id}")
    try:
        with open('flows.txt') as f:
            for line in f:
                flow = json.loads(line.strip())
                if flow["flow_id"] == flow_id:
                    return jsonify(flow)
        return jsonify({"error": "not found"}), 200
    except FileNotFoundError:
        return jsonify({"error": "file missing"}), 200


@app.route('/save_config', methods=['POST'])
def save_config():
    data = request.json

    flow_id = data.get('flow_id')
    node_id = data.get('node_id')
    config = data.get('config', {})

    result_list = []

    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()

    # 提取所有的 config_name
    config_names = list(config.keys())

    # 一次性查询当前 flow_id + node_id + config_name 的所有记录
    query = '''
        SELECT config_name FROM node_configs
        WHERE flow_id = ? AND node_id = ?
        AND config_name IN ({})
    '''.format(','.join('?' * len(config_names)))

    params = [flow_id, node_id] + config_names
    c.execute(query, params)
    existing_configs = set(row[0] for row in c.fetchall())

    # 准备批量插入和更新的数据
    to_insert = []
    to_update = []

    for config_name, config_param in config.items():
        if isinstance(config_param, str) and config_param.startswith('"') and config_param.endswith('"'):
            config_param = config_param[1:-1]

        result_list.append({
            "flow_id": flow_id,
            "node_id": node_id,
            "config_name": config_name,
            "config_param": config_param
        })

        if config_name in existing_configs:
            to_update.append((config_param, flow_id, node_id, config_name))
        else:
            to_insert.append((flow_id, node_id, config_name, config_param))

    # 批量更新
    if to_update:
        c.executemany('''
            UPDATE node_configs SET config_param = ?
            WHERE flow_id = ? AND node_id = ? AND config_name = ?
        ''', to_update)

    # 批量插入
    if to_insert:
        c.executemany('''
            INSERT INTO node_configs (flow_id, node_id, config_name, config_param)
            VALUES (?, ?, ?, ?)
        ''', to_insert)

    conn.commit()
    conn.close()

    return jsonify({"status": "saved", "data": result_list}), 200


@app.route('/get_node_config', methods=['POST'])
def get_node_config():
    data = request.json
    node_id = data.get('node_id')

    if not node_id:
        return jsonify({"error": "Missing node_id"}), 400

    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()

    try:
        # 查询节点类型（来自 nodes 表）
        c.execute("SELECT type FROM nodes WHERE id = ?", (node_id,))
        node_type_row = c.fetchone()
        if not node_type_row:
            return jsonify({"error": "Node not found"}), 404
        node_type = node_type_row[0]

        print(f"node_type: {node_type}")

        # 如果不是 File Input 类型，直接返回
        if node_type == 'File Input':
            # 查询配置路径（来自 configs 表）
            c.execute("""
                SELECT config_param FROM node_configs 
                WHERE node_id = ? AND config_name = 'path'
            """, (node_id,))
            config_row = c.fetchone()
            if not config_row:
                return jsonify({
                })

            path = config_row[0]

            return jsonify({
                "path": path
            })
        if node_type == 'Data Viewer':
            return jsonify({

            })

    finally:
        conn.close()


@app.route('/preview_data', methods=['POST'])
def preview_data():
    data = request.json
    print(f"{data['flow_id']}")
    print(f"{data['node_id']}")
    print(f"{data}")

    from dag_util import build_flowchart_data, execute_dag

    flowchart_data = build_flowchart_data(
        flow_id=data['flow_id'],
        flows_file="flows.txt"
    )

    res = execute_dag(
        nodes=flowchart_data["nodes"],
        edges=flowchart_data["edges"],
        backend_name="pandas"  # 👈 可以切换为 "polars"
    )

    print("flowchart_data", flowchart_data)
    print("res", res)
    print("res", res[data['node_id']])

    # 获取res[data['node_id']]的head(5)
    res_data = res[data['node_id']].head(5).to_dict(orient='records')

    # return jsonify({'status': 'ok'})
    return jsonify(res_data)


@app.route('/add_dependency', methods=['POST'])
def add_dependency():
    data = request.json
    source = data.get('source')
    target = data.get('target')

    if not source or not target:
        return jsonify({"status": "error", "message": "Missing source or target"}), 400

    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()

    try:
        # 插入依赖关系，如果已存在则忽略（使用 INSERT OR IGNORE）
        c.execute('''
            INSERT OR IGNORE INTO dependencies (source, target)
            VALUES (?, ?)
        ''', (source, target))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()

    return jsonify({"status": "ok"}), 200


@app.route('/delete_node_dependencies', methods=['POST'])
def delete_node_dependencies():
    data = request.json
    node_id = data.get('nodeId')

    if not node_id:
        return jsonify({"status": "error", "message": "Missing nodeId"}), 400

    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()

    try:
        # 删除作为 source 或 target 的记录
        c.execute(
            "DELETE FROM dependencies WHERE source = ? OR target = ?", (node_id, node_id))
        deleted_rows = c.rowcount

        conn.commit()

        if deleted_rows > 0:
            return jsonify({"status": "deleted", "deleted_rows": deleted_rows}), 200
        else:
            return jsonify({"status": "no_dependencies_found"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()


@app.route('/save_node', methods=['POST'])
def save_node():
    data = request.json

    node_id = data.get('id')
    node_type = data.get('type')
    created_at = data.get('created_at')

    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()

    # 尝试查询是否存在该 node_id
    c.execute('SELECT 1 FROM nodes WHERE id = ?', (node_id,))
    exists = c.fetchone()

    if exists:
        # 更新已有记录
        c.execute('''
            UPDATE nodes SET type = ?, created_at = ?
            WHERE id = ?
        ''', (node_type, created_at, node_id))
    else:
        # 插入新记录
        c.execute('''
            INSERT INTO nodes (id, type, created_at)
            VALUES (?, ?, ?)
        ''', (node_id, node_type, created_at))

    conn.commit()
    conn.close()

    return jsonify({'status': 'saved'}), 200


@app.route('/compute_node', methods=['POST'])
def compute_node():
    data = request.json

    from dag_util import build_flowchart_data, execute_dag
    flowchart_data = build_flowchart_data(
        flow_id="43cd13c7-25b3-42f3-8d89-6ea353ac5daa",
        flows_file="flows.txt",
        nodes_file="nodes.txt",
        node_configs_file="node_configs.txt"
    )

    res = execute_dag(
        nodes=flowchart_data["nodes"],
        edges=flowchart_data["edges"],
        backend_name="pandas"  # 👈 可以切换为 "polars"
    )

    # 获取res[data['node_id']]的head(5)
    res_data = res[data['node_id']].head(5).to_dict(orient='records')

    # return jsonify({'status': 'ok'})
    return jsonify(res_data)


if __name__ == '__main__':
    print("Starting server...")
    app.run(debug=True)
