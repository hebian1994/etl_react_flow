from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

CONFIG_FILE = 'node_configs.txt'

@app.route('/save_config', methods=['POST'])
def save_config():
    data = request.json
    with open(CONFIG_FILE, 'a') as f:
        f.write(f"{data['nodeId']}:{data['config']['path']}\n")
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

if __name__ == '__main__':
    print("Starting server...")
    app.run(debug=True)


