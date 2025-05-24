from core.dag import infer_schema_from_flowchart_data
from models.config import NodeConfig, NodeConfigStatus, NodeSchema, NodeConfigOptions
from models.node import Dependency, Node

import json
from datetime import datetime

from utils.db_utils import get_db_session


class NodeService:
    def save_node(self, data):
        with get_db_session() as db:
            node = Node(
                id=data['id'],
                type=data['type'],
                created_at=datetime.now().isoformat()
            )
            db.add(node)
            db.commit()

    def delete_node(self, data):
        with get_db_session() as db:
            node_id = data.get('node_id')
            flow_id = data.get('flow_id')

            # Delete related data
            db.query(NodeConfig).filter(NodeConfig.node_id == node_id).delete()
            db.query(NodeConfigStatus).filter(NodeConfigStatus.node_id == node_id).delete()
            db.query(Dependency).filter(
                (Dependency.source == node_id) | (Dependency.target == node_id)
            ).delete()
            db.query(NodeSchema).filter(NodeSchema.node_id == node_id).delete()

            # Delete node
            db.query(Node).filter(Node.id == node_id).delete()
            db.commit()

    def get_node_config(self, data):
        with get_db_session() as db:
            node_id = data.get('node_id')
            flow_id = data.get('flow_id')

            configs = db.query(NodeConfig).filter(
                NodeConfig.node_id == node_id,
                NodeConfig.flow_id == flow_id
            ).all()

            return {
                'config': {
                    'configForm': {c.config_name: c.config_param for c in configs}
                }
            }

    def save_node_config(self, data):
        with get_db_session() as db:
            flow_id = data.get('flow_id')
            node_id = data.get('node_id')
            config = data.get('config', {})
            config_form = config.get('configForm', {})
            node_schema = json.dumps(config.get('node_schema', []))

            # Validate required configs
            node_type = db.query(Node).filter(Node.id == node_id).first().type
            if node_type:
                required_configs = db.query(NodeConfigOptions).filter(
                    NodeConfigOptions.node_type == node_type
                ).all()

                for req_config in required_configs:
                    if req_config.node_config_option not in config_form:
                        return False
                    if not config_form[req_config.node_config_option]:
                        return False

            # Delete old configs
            db.query(NodeConfig).filter(NodeConfig.node_id == node_id).delete()

            # Add new configs
            for config_name, config_param in config_form.items():
                if isinstance(config_param, list):
                    config_param = json.dumps(config_param)
                new_config = NodeConfig(
                    flow_id=flow_id,
                    node_id=node_id,
                    config_name=config_name,
                    config_param=config_param
                )
                db.add(new_config)

            # Update node schema
            db.query(NodeSchema).filter(NodeSchema.node_id == node_id).delete()
            if len(node_schema) > 0:
                schema = NodeSchema(
                    node_id=node_id,
                    node_schema=node_schema,
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                )
                db.add(schema)
                db.commit()
            else:
                # 推断 schema
                print('config changed , infer schema from flowchart_data')
                infer_schema_from_flowchart_data(
                    flow_id, node_id)
                db.commit()

            # 更新配置状态
            db.query(NodeConfigStatus).filter(
                NodeConfigStatus.flow_id == flow_id,
                NodeConfigStatus.node_id == node_id
            ).update({'config_status': 'ok'})

            db.commit()
            print("All operations committed successfully.")

            # 获取node_schema
            response = {}
            response['status'] = 'ok'
            node_schema = self.get_node_schema_from_db(flow_id, node_id)
            response['node_schema'] = node_schema

            # 获取preview_data
            preview_data = self.get_preview_data_by_dag(flow_id, node_id)
            response['preview_data'] = preview_data

            return response

    def get_node_schema(self, data):
        with get_db_session() as db:
            node_id = data.get('node_id')
            flow_id = data.get('flow_id')

            schema = db.query(NodeSchema).filter(NodeSchema.node_id == node_id).first()
            if schema:
                return {'node_schema': json.loads(schema.node_schema)}

            # If no schema exists, infer it
            inferred_schema = infer_schema_from_flowchart_data(flow_id, node_id)
            if inferred_schema:
                return {'node_schema': inferred_schema}

            return {'node_schema': []}

    def get_preview_data(self, data):
        with get_db_session() as db:
            node_id = data.get('node_id')
            flow_id = data.get('flow_id')

            self.get_preview_data_by_dag(flow_id, node_id)
            return {'preview_data': []}

    def handle_node_double_click(self, data):
        node_id = data.get('node_id')
        res = {}
        with get_db_session() as db:
            node = db.query(Node).filter(Node.id == node_id).first()
            node_type = node.type
            if node_type != 'File Input':
                # 校验连线
                edges = db.query(Dependency).filter(
                    Dependency.target == node_id).all()
                if len(edges) == 0:
                    return {"status": "error", "error_code": "no_edges", "message": "请先建立连线"}
                elif node_type == 'Left Join':
                    if len(edges) < 2:
                        return {"status": "error", "error_code": "left_join_not_enough_edges",
                                "message": "Left Join节点需要至少2个连线"}
            # 获取节点的配置状态
            node_config_status = db.query(NodeConfigStatus).filter(
                NodeConfigStatus.node_id == node_id).first()
            if node_config_status.config_status != 'ok':
                return {"status": "error", "error_code": "node_config_not_ok", "message": "节点配置未完成"}
            res['status'] = 'ok'
            # 获取节点的配置
            res['node_config'] = self.get_node_config_from_db(data['flow_id'], node_id)
            # 获取节点的schema
            res['node_schema'] = self.get_node_schema_from_db(data['flow_id'], node_id)
            # 获取preview_data,参照preview_data接口
            res['preview_data'] = self.get_preview_data_by_dag(data['flow_id'], node_id)

            return res

    def get_node_schema_from_db(self, flow_id, node_id):
        with get_db_session() as db:
            node_schema = db.query(NodeSchema).filter(
                NodeSchema.node_id == node_id).first()
            # 如果能查出数据，那么就直接返回。查出来的是个json字符串，需要转换为dict
            if node_schema and len(node_schema.node_schema) > 0:
                node_schema_dict = json.loads(node_schema.node_schema)
                if len(node_schema_dict) > 0:
                    print(len(node_schema_dict))
                    print(f'get node schema from db')
                    print(f'node_schema: {node_schema_dict}')
                    return node_schema_dict

        print(f'no node schema in db, infer from flowchart_data')

        # 查找node_config，查看config_name=path是否已经配置
        with get_db_session() as db:
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
                    flow_id=flow_id, node_id=node_id)
            return schema_results

    def get_node_config_from_db(self, flow_id, node_id):
        with get_db_session() as db:
            node = db.query(Node).filter(Node.id == node_id).first()

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
                with get_db_session() as db:
                    node_type = db.query(Node).filter(
                        Node.id == node_id).first().type
                    if node_type == 'File Input':
                        config_dict['path'] = ''
            return config_dict

    def get_preview_data_by_dag(self, flow_id, node_id):
        # 如果没有定义node_schema，那么就从flowchart_data中推断
        with get_db_session() as db:
            node_schema = db.query(NodeSchema).filter(
                NodeSchema.node_id == node_id).first()

        from utils.dag_util import build_flowchart_data, execute_dag

        flowchart_data = build_flowchart_data(
            flow_id=flow_id
        )

        res = execute_dag(
            nodes=flowchart_data["nodes"],
            edges=flowchart_data["edges"],
            backend_name="polars",
            target_node_id=node_id
        )

        print("flowchart_data", flowchart_data)
        print("res", res)
        if node_id in res:
            # polars 的 head 方法返回的是一个 DataFrame
            # 需要转换为字典列表
            print(f"res[data['node_id']]: {res[node_id]}")
            node_df = res[node_id]
            res_data = node_df.head(5).to_dicts()
            res_data_cols = node_df.columns
            print(f"res_data: {res_data}")
            response = {
                "data": res_data,
                "cols": res_data_cols
            }
        else:
            print(f"{node_id} is not in res")
            res_data = []
            res_data_cols = []
            response = {
                "data": res_data,
                "cols": res_data_cols
            }

        return response
