from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy.dialects.sqlite import insert
import pandas as pd
import os
import json
import sqlite3
from db import DATABASE_FILE
from flask_sqlalchemy import SQLAlchemy
from db import SessionLocal
from models import Flow, Node, NodeConfig, Dependency


app = Flask(__name__)
CORS(app)


# Save Flow
@app.route('/save_flow', methods=['POST'])
def save_flow():
    data = request.json
    with SessionLocal() as db:
        flow = db.query(Flow).filter(Flow.flow_id == data['flow_id']).first()
        print(f"flow: {flow}")
        flow_json = json.dumps(data)
        print(f"flow_json: {flow_json}")
        if flow:
            flow.flow_data = flow_json
            # 更新flow
            db.commit()
        else:
            print(f"flow_id: {data['flow_id']}")
            flow = Flow(flow_id=data['flow_id'], flow_data=flow_json)
            # 添加flow
            db.add(flow)
            db.commit()
    return jsonify({'status': 'ok'})

# Get All Flows


@app.route('/get_flows')
def get_flows():
    with SessionLocal() as db:
        flows = db.query(Flow).all()
        parsed_flows = [json.loads(flow.flow_data) for flow in flows]
        simple_flows = [{"id": f["flow_id"], "nodeCount": len(
            f.get("nodes", []))} for f in parsed_flows]
    return jsonify({'flows': simple_flows})

# Get Single Flow


@app.route('/get_flow/<flow_id>')
def get_flow(flow_id):
    with SessionLocal() as db:
        flow = db.query(Flow).filter(Flow.flow_id == flow_id).first()
        if flow:
            # 如果是File Input 节点，将配置中的path从NodeConfig查出来设置成一个参数，这样前端可以拿来展示文件名
            flow_data = json.loads(flow.flow_data)
            node_with_new_label = []
            for node in flow_data['nodes']:
                print(f"node: {node}")
                print(f"node['data']['type']: {node['data']['type']}")
                if node['data']['type'] == 'File Input':
                    print(f'type is File Input')
                    # 从文件路径中提取出文件名字
                    r = db.query(NodeConfig).filter(
                        NodeConfig.node_id == node['id'], NodeConfig.config_name == 'path').first()
                    if r:
                        file_name = os.path.basename(r.config_param)
                    else:
                        file_name = ''
                    node['data']['label'] = file_name
                    print(f"node['data']['label']: {node['data']['label']}")
                node_with_new_label.append(node)
            flow_data['nodes'] = node_with_new_label

            return jsonify(flow_data)
    return jsonify({"error": "not found"}), 200


# Save Config
@app.route('/save_config', methods=['POST'])
def save_config():
    data = request.json
    flow_id = data.get('flow_id')
    node_id = data.get('node_id')
    config = data.get('config', {})

    with SessionLocal() as db:
        db.query(NodeConfig).filter(NodeConfig.node_id == node_id).delete()
        db.commit()
        for config_name, config_param in config.items():
            new_config = NodeConfig(flow_id=flow_id, node_id=node_id,
                                    config_name=config_name, config_param=config_param)
            db.add(new_config)
            db.commit()

    return jsonify({"status": "saved"}), 200

# Get Node Config


@app.route('/get_node_config', methods=['POST'])
def get_node_config():
    data = request.json
    node_id = data.get('node_id')
    if not node_id:
        return jsonify({"error": "Missing node_id"}), 400

    with SessionLocal() as db:
        node = db.query(Node).filter(Node.id == node_id).first()
        if not node:
            return jsonify({"error": "Node not found"}), 404

        config_rows = db.query(NodeConfig).filter(
            NodeConfig.node_id == node_id).all()
        config_dict = {
            row.config_name: row.config_param for row in config_rows}
        return jsonify(config_dict)

# Add Dependency


@app.route('/add_dependency', methods=['POST'])
def add_dependency():
    data = request.json
    source = data.get('source')
    target = data.get('target')
    if not source or not target:
        return jsonify({"status": "error", "message": "Missing source or target"}), 400

    with SessionLocal() as db:
        if not db.query(Dependency).filter(
                Dependency.source == source, Dependency.target == target).first():
            db.add(Dependency(source=source, target=target))
            db.commit()

    return jsonify({"status": "ok"}), 200

# Delete Node Dependencies


@app.route('/delete_node_dependencies', methods=['POST'])
def delete_node_dependencies():
    data = request.json
    node_id = data.get('nodeId')
    if not node_id:
        return jsonify({"status": "error", "message": "Missing nodeId"}), 400

    with SessionLocal() as db:
        deleted = db.query(Dependency).filter(
            (Dependency.source == node_id) | (Dependency.target == node_id)).delete()
    return jsonify({"status": "deleted", "deleted_rows": deleted}), 200

# Save Node


@app.route('/save_node', methods=['POST'])
def save_node():
    data = request.json
    with SessionLocal() as db:
        node = db.query(Node).filter(Node.id == data['id']).first()
        if node:
            node.type = data.get('type')
            node.created_at = data.get('created_at')
        else:
            node = Node(id=data['id'], type=data.get('type'),
                        created_at=data.get('created_at'))
            db.add(node)
            db.commit()
    return jsonify({'status': 'saved'})


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
        backend_name="polars",
        target_node_id=data['node_id']
    )

    print("flowchart_data", flowchart_data)
    print("res", res)
    if data['node_id'] in res:
        # polars 的 head 方法返回的是一个 DataFrame
        # 需要转换为字典列表
        res_data = res[data['node_id']].head(5).to_dicts()
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
    res_data = res[data['node_id']].head(5).to_dicts()

    # return jsonify({'status': 'ok'})
    return jsonify(res_data)


if __name__ == '__main__':
    print("Starting server...")
    app.run(debug=True)
