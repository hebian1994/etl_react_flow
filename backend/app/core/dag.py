from datetime import datetime

from models.config import NodeSchema
from models.node import Dependency

import json

from utils.db_utils import get_db_session


def get_node_dependencies(node_id, flow_id):
    """获取节点的所有依赖关系"""
    with get_db_session() as db:
        dependencies = db.query(Dependency).filter(
            Dependency.target == node_id
        ).all()
        return [dep.source for dep in dependencies]


def get_node_schema_from_db(node_id):
    """从数据库获取节点的schema"""
    with get_db_session() as db:
        schema = db.query(NodeSchema).filter(NodeSchema.node_id == node_id).first()
        if schema:
            return json.loads(schema.node_schema)
        return None


def infer_schema_from_flowchart_data(flow_id, node_id):
    with get_db_session() as db:
        from utils.dag_util import build_flowchart_data

        flowchart_data = build_flowchart_data(
            flow_id=flow_id
        )

        from utils.dag_util import infer_schema_dag
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
            node_id=node_id, node_schema=json.dumps(schema_results), created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat())
        db.add(new_node_schema)
        db.commit()

    return schema_results
