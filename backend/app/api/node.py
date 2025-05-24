from flask import Blueprint, request, jsonify
import json

from services.node_service import NodeService

node_bp = Blueprint('node', __name__)
node_service = NodeService()


@node_bp.route('/save_node', methods=['POST'])
def save_node():
    data = request.json
    node_service.save_node(data)
    return jsonify({'status': 'ok'})


@node_bp.route('/delete_node', methods=['POST'])
def delete_node():
    data = request.json
    node_service.delete_node(data)
    return jsonify({'status': 'ok'})


@node_bp.route('/get_node_config', methods=['POST'])
def get_node_config():
    data = request.json
    config = node_service.get_node_config(data)
    return jsonify(config)


@node_bp.route('/save_node_config', methods=['POST'])
def save_node_config():
    data = request.json
    node_service.save_node_config(data)
    return jsonify({'status': 'ok'})


@node_bp.route('/get_node_schema', methods=['POST'])
def get_node_schema():
    data = request.json
    schema = node_service.get_node_schema(data)
    return jsonify(schema)


@node_bp.route('/preview_data', methods=['POST'])
def preview_data():
    data = request.json
    preview = node_service.get_preview_data(data)
    return jsonify(preview)


@node_bp.route('/handle_node_double_click', methods=['POST'])
def handle_node_double_click():
    data = request.json
    res = node_service.handle_node_double_click(data)

    return jsonify(res)
