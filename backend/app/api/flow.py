from flask import Blueprint, request, jsonify
import json

from services.flow_service import FlowService

flow_bp = Blueprint('flow', __name__)
flow_service = FlowService()


@flow_bp.route('/save_flow', methods=['POST'])
def save_flow():
    data = request.json
    flow_service.save_flow(data)
    return jsonify({'status': 'ok'})


@flow_bp.route('/delete_flow', methods=['POST'])
def delete_flow():
    data = request.json
    flow_id = data.get('flow_id')
    flow_service.delete_flow(flow_id)
    return jsonify({'status': 'ok'})


@flow_bp.route('/get_flows')
def get_flows():
    flows = flow_service.get_all_flows()
    return jsonify({'flows': flows})


@flow_bp.route('/get_flow/<flow_id>')
def get_flow(flow_id):
    flow = flow_service.get_flow(flow_id)
    if flow:
        return jsonify(flow)
    return jsonify({"error": "not found"}), 200


@flow_bp.route('/test')
def test():
    return 'Blueprint works!'
