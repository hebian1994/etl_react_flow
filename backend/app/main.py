from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
import json

app = Flask(__name__)
CORS(app)

CONFIG_FILE = 'node_configs.txt'


@app.route('/save_flow', methods=['POST'])
def save_flow():
    data = request.json
    flow_id = data['flow_id']

    # read from flows.txt, if the flow_id is already in the file, update the flow
    with open('flows.txt', 'r') as f:
        for line in f:
            if flow_id in line:
                with open('flows.txt', 'w') as f:
                    f.write(json.dumps(data) + '\n')
                return jsonify({'status': 'ok'})
    # if the flow_id is not in the file, append the flow
            else:
                with open('flows.txt', 'a') as f:
                    f.write(json.dumps(data) + '\n')


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
    print(data)
    with open(CONFIG_FILE, 'a') as f:
        f.write(
            f"{data['node_id']}:{data['config']['path']}:{data['config']['name']}\n")
    return jsonify({"status": "saved"}), 200


@app.route('/preview_data', methods=['POST'])
def preview_data():
    data = request.json
    path = data.get('path', '').strip('"')
    print(f"Checking path: {path}")
    print(f"Path exists: {os.path.exists(path)}")
    print(f"Current working directory: {os.getcwd()}")
    if not path or not os.path.exists(path):
        return jsonify({"error": f"File not found at path: {path}"}), 400
    try:
        df = pd.read_csv(path)
        return jsonify(df.head(5).to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


DEPENDENCY_FILE = 'dependencies.txt'


@app.route('/add_dependency', methods=['POST'])
def add_dependency():
    data = request.json
    source = data['source']
    target = data['target']
    with open(DEPENDENCY_FILE, 'a') as f:
        f.write(f"{source} -> {target}\n")
    return jsonify({"status": "ok"})


@app.route('/delete_node_dependencies', methods=['POST'])
def delete_node_dependencies():
    node_id = request.json['nodeId']
    try:
        with open(DEPENDENCY_FILE, 'r') as f:
            lines = f.readlines()
        with open(DEPENDENCY_FILE, 'w') as f:
            for line in lines:
                if node_id not in line.strip().split(" -> "):
                    f.write(line)
        return jsonify({"status": "deleted"})
    except FileNotFoundError:
        return jsonify({"status": "file not found"}), 404


@app.route('/save_node', methods=['POST'])
def save_node():
    data = request.json
    with open('nodes.txt', 'a') as f:
        f.write(f"{data['id']} | {data['type']} | {data['created_at']}\n")
    return jsonify({'status': 'saved'})


@app.route('/compute_node', methods=['POST'])
def compute_node():
    data = request.json
    print(f"{data['node_id']}")
    # read from nodes.txt
    with open('nodes.txt', 'r') as f:
        for line in f:
            if data['node_id'] in line:
                print(line)
                # split by | and get the second element named component name
                component_name = line.split('|')[1].strip()
                # if component_name is Data Viewer, read from dependencies.txt
                if component_name == 'Data Viewer':
                    # use pandas to read the txt file , the col name are source and target
                    df = pd.read_csv(DEPENDENCY_FILE, sep=' -> ', header=None,
                                     names=['source', 'target'], engine='python')
                    df['source'] = df['source'].str.strip()
                    df['target'] = df['target'].str.strip()
                    df = df[df['target'] == data['node_id']]
                    print(df)

    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    print("Starting server...")
    app.run(debug=True)
