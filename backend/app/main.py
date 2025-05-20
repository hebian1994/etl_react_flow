from datetime import datetime
from models import NodeSchema
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
    print(f"data: {data}")
    config = data.get('config', {})
    configForm = config.get('configForm', {})
    # 转成JSON字符串
    node_schema = config.get('node_schema', [])
    node_schema = json.dumps(node_schema)
    print(f"configForm: {configForm}")
    print(f"node_schema: {node_schema}")

    with SessionLocal() as db:
        db.query(NodeConfig).filter(NodeConfig.node_id == node_id).delete()
        db.commit()
        print(f"delete old node config")
        for config_name, config_param in configForm.items():
            print(f"config_name: {config_name}, config_param: {config_param}")
            # config_param 是list，需要转换为str
            if isinstance(config_param, list):
                config_param = json.dumps(config_param)
            new_config = NodeConfig(flow_id=flow_id, node_id=node_id,
                                    config_name=config_name, config_param=config_param)
            db.add(new_config)
            db.commit()
            print(f"add new node config")

        #
        print('config changed , infer schema from flowchart_data')
        schema_results = infer_schema_from_flowchart_data(flow_id, node_id)
        node_schema = json.dumps(schema_results)

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
        # config_param本来可能是个list，需要转换为list，但也可能不是list,不是就不转。应该用try catch
        config_dict = {}
        for row in config_rows:
            try:
                config_dict[row.config_name] = json.loads(row.config_param)
            except:
                config_dict[row.config_name] = row.config_param

        # 如果config_dict是空的，且节点类型是File Input，那么就默认是空字符串
        # type要从node_config中查
        if not config_dict:
            with SessionLocal() as db:
                node_type = db.query(Node).filter(
                    Node.id == node_id).first().type
                if node_type == 'File Input':
                    config_dict['path'] = ''

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

# Delete Dependency


@app.route('/delete_dependency', methods=['POST'])
def delete_dependency():
    data = request.json
    source = data.get('source')
    target = data.get('target')
    if not source or not target:
        return jsonify({"status": "error", "message": "Missing source or target"}), 400

    with SessionLocal() as db:
        deleted = db.query(Dependency).filter(
            Dependency.source == source, Dependency.target == target).delete()
        db.commit()
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

# get node schema


def infer_schema_from_flowchart_data(flow_id, node_id):
    with SessionLocal() as db:
        from dag_util import build_flowchart_data, execute_dag

        flowchart_data = build_flowchart_data(
            flow_id=flow_id
        )

        from dag_util import infer_schema_dag
        schema_results = infer_schema_dag(
            nodes=flowchart_data["nodes"],
            edges=flowchart_data["edges"],
            target_node_id=node_id
        )

        print("schema_results", schema_results)

        # 删除node_schema
        db.query(NodeSchema).filter(
            NodeSchema.node_id == node_id).delete()
        db.commit()
        # 添加新的node_schema
        new_node_schema = NodeSchema(
            node_id=node_id, node_schema=json.dumps(schema_results), created_at=datetime.now().isoformat(), updated_at=datetime.now().isoformat())
        db.add(new_node_schema)
        db.commit()

    return schema_results


@app.route('/get_node_schema', methods=['POST'])
def get_node_schema():
    data = request.json
    node_id = data.get('node_id')
    if not node_id:
        return jsonify({"error": "Missing node_id"}), 400

    with SessionLocal() as db:
        node_schema = db.query(NodeSchema).filter(
            NodeSchema.node_id == node_id).first()
        # 如果能查出数据，那么就直接返回。查出来的是个json字符串，需要转换为dict
        if node_schema and len(node_schema.node_schema) > 0:
            node_schema_dict = json.loads(node_schema.node_schema)
            if len(node_schema_dict) > 0:
                print(len(node_schema_dict))
                print(f'get node schema from db')
                print(f'node_schema: {node_schema_dict}')
                return jsonify(node_schema_dict)

    print(f'no node schema in db, infer from flowchart_data')

    # 查找node_config，查看config_name=path是否已经配置
    with SessionLocal() as db:
        # 从nodes查出node的type
        node_type = db.query(Node).filter(
            Node.id == node_id).first().type
        need_infer_schema = False
        if node_type == 'File Input':
            node_config = db.query(NodeConfig).filter(
                NodeConfig.config_name == 'path',
                NodeConfig.node_id == node_id).first()
            if not node_config:
                print("path is not in node_config,unable to infer schema")
                schema_results = []
            else:
                print('11111111111')
                need_infer_schema = True
        elif node_type == 'Left Join':
            print('22222222222')
            node_config = db.query(NodeConfig).filter(
                NodeConfig.config_name == 'left_join_on',
                NodeConfig.node_id == node_id).first()
            if not node_config:
                print("left_join_on is not in node_config,unable to infer schema")
                schema_results = []
            else:
                need_infer_schema = True
        elif node_type == 'Aggregate':
            print('33333333333')
            node_config = db.query(NodeConfig).filter(
                NodeConfig.config_name == 'groupBy',
                NodeConfig.node_id == node_id).first()
            if not node_config:
                print("groupBy is not in node_config,unable to infer schema")
                schema_results = []
            else:
                need_infer_schema = True
        else:
            need_infer_schema = True

        if need_infer_schema:
            print("path is in node_config, infer schema from flowchart_data")

            schema_results = infer_schema_from_flowchart_data(
                data['flow_id'], node_id)

    return jsonify(schema_results)


@app.route('/preview_data', methods=['POST'])
def preview_data():
    data = request.json
    print(f"{data['flow_id']}")
    print(f"{data['node_id']}")
    print(f"{data}")

    # 如果没有定义node_schema，那么就从flowchart_data中推断
    with SessionLocal() as db:
        node_schema = db.query(NodeSchema).filter(
            NodeSchema.node_id == data['node_id']).first()
        if not node_schema:
            print(f'undefined node schema, unable to preview data')
            return jsonify([])

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
