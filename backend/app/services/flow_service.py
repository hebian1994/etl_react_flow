from models.config import NodeConfig, NodeConfigStatus, NodeSchema
from models.flow import Flow
from models.node import Dependency, Node
import json
import os

from utils.db_utils import get_db_session


class FlowService:
    def save_flow(self, data):
        with get_db_session() as db:
            flow = db.query(Flow).filter(Flow.flow_id == data['flow_id']).first()
            flow_name = data['flow_name']
            flow_json = json.dumps(data)
            
            if flow:
                flow.flow_data = flow_json
                flow.flow_name = flow_name
            else:
                flow = Flow(flow_id=data['flow_id'],
                          flow_data=flow_json,
                          flow_name=flow_name)
                db.add(flow)
            db.commit()

    def delete_flow(self, flow_id):
        with get_db_session() as db:
            flow = db.query(Flow).filter(Flow.flow_id == flow_id).first()
            if flow:
                nodes_array = json.loads(flow.flow_data)['nodes']
                node_ids = [node['id'] for node in nodes_array]
                
                # Delete related data
                db.query(Node).filter(Node.id.in_(node_ids)).delete()
                db.query(NodeConfig).filter(NodeConfig.flow_id == flow_id).delete()
                db.query(NodeConfigStatus).filter(NodeConfigStatus.flow_id == flow_id).delete()
                db.query(Dependency).filter(Dependency.source.in_(node_ids) | Dependency.target.in_(node_ids)).delete()
                db.query(NodeSchema).filter(NodeSchema.node_id.in_(node_ids)).delete()
                
                # Delete flow
                db.query(Flow).filter(Flow.flow_id == flow_id).delete()
                db.commit()

    def get_all_flows(self):
        with get_db_session() as db:
            flows = db.query(Flow).all()
            parsed_flows = [json.loads(flow.flow_data) for flow in flows]
            return [{"id": f["flow_id"], 
                    "nodeCount": len(f.get("nodes", [])), 
                    "flowName": f.get("flow_name", "")} 
                    for f in parsed_flows]

    def get_flow(self, flow_id):
        with get_db_session() as db:
            flow = db.query(Flow).filter(Flow.flow_id == flow_id).first()
            if flow:
                flow_data = json.loads(flow.flow_data)
                node_with_new_label = []
                
                for node in flow_data['nodes']:
                    if node['data']['type'] == 'File Input':
                        r = db.query(NodeConfig).filter(
                            NodeConfig.node_id == node['id'],
                            NodeConfig.config_name == 'path'
                        ).first()
                        if r:
                            file_name = os.path.basename(r.config_param)
                            node['data']['label'] = file_name
                    node_with_new_label.append(node)
                
                flow_data['nodes'] = node_with_new_label
                return {
                    'flow_name': flow.flow_name,
                    'flow_data': flow_data
                }
            return None 