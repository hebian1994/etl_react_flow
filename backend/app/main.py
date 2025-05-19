from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
import json
import sqlite3
from DB import DATABASE_FILE

app = Flask(__name__)
CORS(app)


@app.route('/save_flow', methods=['POST'])
def save_flow():
    data = request.json
    flow_id = data['flow_id']
    flow_json = json.dumps(data)

    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()

    # 尝试更新，如果没有更新行，说明不存在，插入
    c.execute('UPDATE flows SET flow_data = ? WHERE flow_id = ?',
              (flow_json, flow_id))
    if c.rowcount == 0:
        c.execute('INSERT INTO flows (flow_id, flow_data) VALUES (?, ?)',
                  (flow_id, flow_json))

    conn.commit()
    conn.close()

    return jsonify({'status': 'ok'})


@app.route('/get_flows')
def get_flows():
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()

    c.execute('SELECT flow_data FROM flows')
    rows = c.fetchall()
    conn.close()

    flows = [json.loads(row[0]) for row in rows]
    simple_flows = [{"id": f["flow_id"], "nodeCount": len(
        f.get("nodes", []))} for f in flows]

    return jsonify({'flows': simple_flows})


@app.route('/get_flow/<flow_id>')
def get_flow(flow_id):
    print(f"Getting flow with ID: {flow_id}")
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        c.execute('SELECT flow_data FROM flows WHERE flow_id = ?', (flow_id,))
        row = c.fetchone()
        conn.close()

        if row:
            flow = json.loads(row[0])
            return jsonify(flow)
        else:
            return jsonify({"error": "not found"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/save_config', methods=['POST'])
def save_config():
    data = request.json

    flow_id = data.get('flow_id')
    node_id = data.get('node_id')
    config = data.get('config', {})

    result_list = []

    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()

    # 下面都不需要写那么复杂了，直接删除node_id对应的所有记录，然后将最新送来的存进去就行了
    c.execute('DELETE FROM node_configs WHERE node_id = ?', (node_id,))
    c.executemany('''
        INSERT INTO node_configs (flow_id, node_id, config_name, config_param)
        VALUES (?, ?, ?, ?)
    ''', [(flow_id, node_id, config_name, config_param) for config_name, config_param in config.items()])

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
        # 查询配置路径（来自 configs 表）
        # 如果 node_id 对应的记录有多个，则返回多个
        c.execute("""
            SELECT config_name, config_param FROM node_configs 
            WHERE node_id = ?
        """, (node_id,))
        config_rows = c.fetchall()
        if not config_rows:
            return jsonify({
            })

        # 将得到的 config_rows 转换为 {config_name: config_param} 的格式
        config_dict = {row[0]: row[1] for row in config_rows}

        return jsonify(config_dict)

    finally:
        conn.close()


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


@app.route('/preview_data', methods=['POST'])
def preview_data():
    data = request.json
    print(f"{data['flow_id']}")
    print(f"{data['node_id']}")
    print(f"{data}")

    from dag_util import build_flowchart_data, execute_dag

    flowchart_data = build_flowchart_data(
        flow_id=data['flow_id']
    )

    res = execute_dag(
        nodes=flowchart_data["nodes"],
        edges=flowchart_data["edges"],
        backend_name="pandas"  # 👈 可以切换为 "polars"
    )

    print("flowchart_data", flowchart_data)
    print("res", res)
    if data['node_id'] in res:
        res_data = res[data['node_id']].head(5).to_dict(orient='records')
    else:
        print(f"{data['node_id']} is not in res")
        res_data = []

    # return jsonify({'status': 'ok'})
    return jsonify(res_data)


@app.route('/compute_node', methods=['POST'])
def compute_node():
    data = request.json

    from dag_util import build_flowchart_data, execute_dag
    flowchart_data = build_flowchart_data(
        flow_id="43cd13c7-25b3-42f3-8d89-6ea353ac5daa",
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
