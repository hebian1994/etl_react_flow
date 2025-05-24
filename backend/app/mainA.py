# from sqlalchemy.exc import SQLAlchemyError
# from datetime import datetime
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import os
# import json
# from db import SessionLocal
# from models.config import NodeConfig, NodeConfigStatus, NodeSchema, NodeConfigOptions
# from models.flow import Flow
# from models.node import Node, Dependency
#
# # from models import Flow, Node, NodeConfig, Dependency
#
#
# app = Flask(__name__)
# CORS(app)
#
#
# def save_flow_to_db(data):
#     with SessionLocal() as db:
#         flow = db.query(Flow).filter(Flow.flow_id == data['flow_id']).first()
#         print(f"flow: {flow}")
#         flow_name = data['flow_name']
#         flow_json = json.dumps(data)
#         print(f"flow_json: {flow_json}")
#         if flow:
#             flow.flow_data = flow_json
#             flow.flow_name = flow_name
#             # 更新flow
#             db.commit()
#         else:
#             print(f"flow_id: {data['flow_id']}")
#             flow = Flow(flow_id=data['flow_id'],
#                         flow_data=flow_json, flow_name=flow_name)
#             # 添加flow
#             db.add(flow)
#             db.commit()
#
#
# # Save Flow
#
#
# @app.route('/save_flow', methods=['POST'])
# def save_flow():
#     data = request.json
#     save_flow_to_db(data)
#
#     return jsonify({'status': 'ok'})
#
#
# # Delete Flow
# @app.route('/delete_flow', methods=['POST'])
# def delete_flow():
#     data = request.json
#     flow_id = data.get('flow_id')
#     with SessionLocal() as db:
#         # 查找出FLOW，解释出包含的所有NODE_ID，然后删除
#         flow = db.query(Flow).filter(Flow.flow_id == flow_id).first()
#         if flow:
#             nodes_array = json.loads(flow.flow_data)['nodes']
#             node_ids = [node['id'] for node in nodes_array]
#             for node_id in node_ids:
#                 db.query(Node).filter(Node.id == node_id).delete()
#                 db.commit()
#             db.query(Flow).filter(Flow.flow_id == flow_id).delete()
#             db.commit()
#             # 删除该FLOW中所有节点，节点配置，节点配置状态，节点依赖，节点schema
#             db.query(Node).filter(Node.id.in_(node_ids)).delete()
#             db.commit()
#             db.query(NodeConfig).filter(NodeConfig.flow_id == flow_id).delete()
#             db.commit()
#             db.query(NodeConfigStatus).filter(
#                 NodeConfigStatus.flow_id == flow_id).delete()
#             db.commit()
#             db.query(Dependency).filter(Dependency.source.in_(
#                 node_ids) | Dependency.target.in_(node_ids)).delete()
#             db.commit()
#             db.query(NodeSchema).filter(
#                 NodeSchema.node_id.in_(node_ids)).delete()
#             db.commit()
#     return jsonify({'status': 'ok'})
#
#
# # Get All Flows
#
#
# @app.route('/get_flows')
# def get_flows():
#     with SessionLocal() as db:
#         flows = db.query(Flow).all()
#         parsed_flows = [json.loads(flow.flow_data) for flow in flows]
#         simple_flows = [{"id": f["flow_id"], "nodeCount": len(
#             f.get("nodes", [])), "flowName": f.get("flow_name", "")} for f in parsed_flows]
#     return jsonify({'flows': simple_flows})
#
#
# # Get Single Flow
#
#
# @app.route('/get_flow/<flow_id>')
# def get_flow(flow_id):
#     res = {}
#     with SessionLocal() as db:
#         flow = db.query(Flow).filter(Flow.flow_id == flow_id).first()
#         if flow:
#             # 如果是File Input 节点，将配置中的path从NodeConfig查出来设置成一个参数，这样前端可以拿来展示文件名
#             flow_data = json.loads(flow.flow_data)
#             node_with_new_label = []
#             for node in flow_data['nodes']:
#                 print(f"node: {node}")
#                 print(f"node['data']['type']: {node['data']['type']}")
#                 if node['data']['type'] == 'File Input':
#                     print(f'type is File Input')
#                     # 从文件路径中提取出文件名字
#                     r = db.query(NodeConfig).filter(
#                         NodeConfig.node_id == node['id'], NodeConfig.config_name == 'path').first()
#                     if r:
#                         file_name = os.path.basename(r.config_param)
#                     else:
#                         file_name = ''
#                     node['data']['label'] = file_name
#                     print(f"node['data']['label']: {node['data']['label']}")
#                 node_with_new_label.append(node)
#             flow_data['nodes'] = node_with_new_label
#
#             res['flow_name'] = flow.flow_name
#             res['flow_data'] = flow_data
#
#             return jsonify(res)
#     return jsonify({"error": "not found"}), 200
#
#
# # Save Config
#
#
# @app.route('/save_node_config', methods=['POST'])
# def save_node_config():
#     data = request.json
#     flow_id = data.get('flow_id')
#     node_id = data.get('node_id')
#     print(f"data: {data}")
#     config = data.get('config', {})
#     configForm = config.get('configForm', {})
#     # 转成JSON字符串
#     node_schema = config.get('node_schema', [])
#     node_schema = json.dumps(node_schema)
#     print(f"configForm: {configForm}")
#     print(f"node_schema: {node_schema}")
#
#     response = {}
#
#     # 检查该节点的节点类型所需要的配置项是否都填好了
#     with SessionLocal() as db:
#         node_type = db.query(Node).filter(Node.id == node_id).first().type
#         if node_type:
#             # 从node_config_options中查出node_type的配置选项
#             node_config_options = db.query(NodeConfigOptions).filter(
#                 NodeConfigOptions.node_type == node_type).all()
#             print(f"node_config_options: {node_config_options}")
#
#             for node_config_option in node_config_options:
#                 print(f"node_config_option: {node_config_option}")
#                 print(
#                     f"node_config_option.node_config_option: {node_config_option.node_config_option}")
#                 cur_config_option = node_config_option.node_config_option
#                 if cur_config_option and cur_config_option != 'NA' and cur_config_option not in configForm:
#                     return jsonify({"status": "error", "node_config_status": f"{cur_config_option} is required"}), 200
#                 else:
#                     if configForm[cur_config_option] == '':
#                         return jsonify({"status": "error", "node_config_status": f"{cur_config_option} is empty"}), 200
#         else:
#             raise Exception(f"node_type {node_type} is not supported")
#
#         # 所有的数据更改应该在同一个事务内
#         try:
#             # 删除旧配置
#             db.query(NodeConfig).filter(NodeConfig.node_id == node_id).delete()
#             db.commit()
#
#             # 添加新配置
#             for config_name, config_param in configForm.items():
#                 print(
#                     f"config_name: {config_name}, config_param: {config_param}")
#                 if isinstance(config_param, list):
#                     config_param = json.dumps(config_param)
#                 new_config = NodeConfig(
#                     flow_id=flow_id,
#                     node_id=node_id,
#                     config_name=config_name,
#                     config_param=config_param
#                 )
#                 db.add(new_config)
#             db.commit()
#
#             # 如果前端已经传了有效的node_schema，那么就直接删除原来的，再存入前端传来的就行了，不需要退点
#             db.query(NodeSchema).filter(
#                 NodeSchema.node_id == node_id).delete()
#             db.commit()
#             if len(node_schema) > 0:
#                 new_node_schema = NodeSchema(
#                     node_id=node_id, node_schema=node_schema, created_at=datetime.now().isoformat(),
#                     updated_at=datetime.now().isoformat())
#                 db.add(new_node_schema)
#                 db.commit()
#             else:
#                 # 推断 schema
#                 print('config changed , infer schema from flowchart_data')
#                 infer_schema_from_flowchart_data(
#                     flow_id, node_id)
#                 db.commit()
#
#             # 更新配置状态
#             db.query(NodeConfigStatus).filter(
#                 NodeConfigStatus.flow_id == flow_id,
#                 NodeConfigStatus.node_id == node_id
#             ).update({'config_status': 'ok'})
#
#             db.commit()
#             print("All operations committed successfully.")
#
#             # 获取node_schema
#             response['status'] = 'ok'
#             node_schema = get_node_schema_from_db(flow_id, node_id)
#             response['node_schema'] = node_schema
#
#             # 获取preview_data
#             preview_data = get_preview_data(flow_id, node_id)
#             response['preview_data'] = preview_data
#
#         except SQLAlchemyError as e:
#             db.rollback()
#             print(f"Transaction failed: {e}")
#             response['status'] = 'error'
#             response['message'] = str('system error')
#
#     return jsonify(response), 200
#
#
# def get_node_config_from_db(flow_id, node_id):
#     with SessionLocal() as db:
#         node = db.query(Node).filter(Node.id == node_id).first()
#         if not node:
#             return jsonify({"error": "Node not found"}), 404
#
#         config_rows = db.query(NodeConfig).filter(
#             NodeConfig.node_id == node_id).all()
#         # config_param本来可能是个list，需要转换为list，但也可能不是list,不是就不转。应该用try catch
#         config_dict = {}
#         for row in config_rows:
#             try:
#                 config_dict[row.config_name] = json.loads(row.config_param)
#             except:
#                 config_dict[row.config_name] = row.config_param
#
#         # 如果config_dict是空的，且节点类型是File Input，那么就默认是空字符串
#         # type要从node_config中查
#         if not config_dict:
#             with SessionLocal() as db:
#                 node_type = db.query(Node).filter(
#                     Node.id == node_id).first().type
#                 if node_type == 'File Input':
#                     config_dict['path'] = ''
#         return config_dict
#
#
# # Get Node Config
#
#
# @app.route('/get_node_config', methods=['POST'])
# def get_node_config():
#     data = request.json
#     node_id = data.get('node_id')
#     if not node_id:
#         return jsonify({"error": "Missing node_id"}), 400
#
#     return get_node_config_from_db(data['flow_id'], node_id)
#
#
# # Get Node Edges
# @app.route('/get_node_edges', methods=['POST'])
# def get_node_edges():
#     data = request.json
#     node_id = data.get('node_id')
#     with SessionLocal() as db:
#         # 返回source或者target是node_id的边
#         edges = db.query(Dependency).filter(
#             (Dependency.source == node_id) | (Dependency.target == node_id)).all()
#         # 查询到的应该是多行数据，那么需要转成数组
#         res = []
#         for edge in edges:
#             print(f"edge: {edge}")
#             print(f"edge.source: {edge.source}")
#             print(f"edge.target: {edge.target}")
#             res.append({"source": edge.source, "target": edge.target})
#
#         return jsonify({"edges": res})
#
#
# # Add Dependency
#
#
# @app.route('/add_dependency', methods=['POST'])
# def add_dependency():
#     data = request.json
#     source = data.get('source')
#     target = data.get('target')
#     if not source or not target:
#         return jsonify({"status": "error", "message": "Missing source or target"}), 400
#
#     with SessionLocal() as db:
#         if not db.query(Dependency).filter(
#                 Dependency.source == source, Dependency.target == target).first():
#             db.add(Dependency(source=source, target=target))
#             db.commit()
#
#     return jsonify({"status": "ok"}), 200
#
#
# # Delete Node Dependencies
#
#
# @app.route('/delete_node_dependencies', methods=['POST'])
# def delete_node_dependencies():
#     data = request.json
#     node_id = data.get('nodeId')
#     if not node_id:
#         return jsonify({"status": "error", "message": "Missing nodeId"}), 400
#
#     with SessionLocal() as db:
#         deleted = db.query(Dependency).filter(
#             (Dependency.source == node_id) | (Dependency.target == node_id)).delete()
#     return jsonify({"status": "deleted", "deleted_rows": deleted}), 200
#
#
# # Delete Dependency
#
#
# @app.route('/delete_dependency', methods=['POST'])
# def delete_dependency():
#     data = request.json
#     source = data.get('source')
#     target = data.get('target')
#     if not source or not target:
#         return jsonify({"status": "error", "message": "Missing source or target"}), 400
#
#     with SessionLocal() as db:
#         deleted = db.query(Dependency).filter(
#             Dependency.source == source, Dependency.target == target).delete()
#         db.commit()
#     return jsonify({"status": "deleted", "deleted_rows": deleted}), 200
#
#
# # check flow all nodes config status
#
#
# @app.route('/check_flow_all_nodes_config_status', methods=['POST'])
# def check_flow_all_nodes_config_status():
#     data = request.json
#     flow_id = data.get('flow_id')
#     with SessionLocal() as db:
#         flow_all_nodes_config_status = db.query(NodeConfigStatus).filter(
#             NodeConfigStatus.flow_id == flow_id).all()
#         print(f"flow_all_nodes_config_status: {flow_all_nodes_config_status}")
#         # 如果node_config_status为空，那么就返回ok
#         if not flow_all_nodes_config_status:
#             return jsonify({"status": "ok", "node_config_status": "ok"}), 200
#         else:
#             # 如果存在节点的config_status不是ok，那么就返回error
#             for node_config_status in flow_all_nodes_config_status:
#                 if node_config_status.config_status != 'ok':
#                     return jsonify(
#                         {"status": "error", "node_config_status": "more than one node config status is not ok"}), 200
#             return jsonify({"status": "ok", "node_config_status": "ok"}), 200
#
#
# # check 1 node config status
# @app.route('/check_node_config_status', methods=['POST'])
# def check_node_config_status():
#     data = request.json
#     flow_id = data.get('flow_id')
#     with SessionLocal() as db:
#         # 如果node_id不为空，那么就查询该节点的node_config_status
#         node_config_status = db.query(NodeConfigStatus).filter(
#             NodeConfigStatus.flow_id == flow_id,
#             NodeConfigStatus.node_id == data.get('node_id'))
#         # 如果没查到该节点的配置状态就直接告知可以添加
#         if not node_config_status:
#             return jsonify({"status": "ok", "node_config_status": "ok"}), 200
#         else:
#             # 如果查到了，那么只能有一条，并且config_status是ok，否则就告知前端不能添加新的
#             # TypeError: object of type 'Query' has no len()
#             if node_config_status.count() > 1:
#                 return jsonify({"status": "error", "node_config_status": "more than one node config status"}), 200
#             elif node_config_status.first().config_status != 'ok':
#                 return jsonify({"status": "waiting", "node_config_status": "node config status is not ok"}), 200
#             else:
#                 return jsonify({"status": "ok", "node_config_status": node_config_status.first().config_status}), 200
#
#
# # handle node double click
# @app.route('/handle_node_double_click', methods=['POST'])
# def handle_node_double_click():
#     data = request.json
#     node_id = data.get('node_id')
#     res = {}
#     with SessionLocal() as db:
#         node = db.query(Node).filter(Node.id == node_id).first()
#         node_type = node.type
#         if node_type != 'File Input':
#             # 校验连线
#             edges = db.query(Dependency).filter(
#                 Dependency.target == node_id).all()
#             if len(edges) == 0:
#                 return jsonify({"status": "error", "error_code": "no_edges", "message": "请先建立连线"}), 200
#             elif node_type == 'Left Join':
#                 if len(edges) < 2:
#                     return jsonify({"status": "error", "error_code": "left_join_not_enough_edges",
#                                     "message": "Left Join节点需要至少2个连线"}), 200
#         # 获取节点的配置状态
#         node_config_status = db.query(NodeConfigStatus).filter(
#             NodeConfigStatus.node_id == node_id).first()
#         if node_config_status.config_status != 'ok':
#             return jsonify({"status": "error", "error_code": "node_config_not_ok", "message": "节点配置未完成"}), 200
#         res['status'] = 'ok'
#         # 获取节点的配置
#         res['node_config'] = get_node_config_from_db(data['flow_id'], node_id)
#         # 获取节点的schema
#         res['node_schema'] = get_node_schema_from_db(data['flow_id'], node_id)
#         # 获取preview_data,参照preview_data接口
#         res['preview_data'] = get_preview_data(data['flow_id'], node_id)
#
#         return jsonify(res)
#
#
# # Save Node
#
#
# @app.route('/save_node', methods=['POST'])
# def save_node():
#     data = request.json
#     with SessionLocal() as db:
#         node = db.query(Node).filter(Node.id == data['id']).first()
#         if node:
#             node.type = data.get('type')
#             node.created_at = data.get('created_at')
#         else:
#             node = Node(id=data['id'], type=data.get('type'),
#                         created_at=data.get('created_at'))
#             db.add(node)
#             db.commit()
#         # 新增node_config_status
#         if data.get('type') == 'Data Viewer':
#             config_status = 'ok'
#         else:
#             config_status = 'waiting'
#         new_node_config_status = NodeConfigStatus(
#             flow_id=data['flow_id'], node_id=data['id'], config_status=config_status,
#             created_at=datetime.now().isoformat(), updated_at=datetime.now().isoformat())
#         db.add(new_node_config_status)
#         db.commit()
#     return jsonify({'status': 'saved'})
#
#
# # delete node
#
#
# @app.route('/delete_node', methods=['POST'])
# def delete_node():
#     data = request.json
#     with SessionLocal() as db:
#         # 删除node
#         db.query(Node).filter(Node.id == data['nodeId']).delete()
#         db.commit()
#         # 删除node_config_status
#         db.query(NodeConfigStatus).filter(
#             NodeConfigStatus.node_id == data['nodeId']).delete()
#         db.commit()
#         # 删除node_schema
#         db.query(NodeSchema).filter(
#             NodeSchema.node_id == data['nodeId']).delete()
#         db.commit()
#         # 删除node_dependencies,source或者target是data['nodeId']的都删除
#         db.query(Dependency).filter(
#             (Dependency.source == data['nodeId']) | (Dependency.target == data['nodeId'])).delete()
#         db.commit()
#         # 删除node_config
#         db.query(NodeConfig).filter(
#             NodeConfig.node_id == data['nodeId']).delete()
#         db.commit()
#     return jsonify({'status': 'deleted'})
#
#
# def infer_schema_from_flowchart_data(flow_id, node_id):
#     with SessionLocal() as db:
#         from utils.dag_util import build_flowchart_data
#
#         flowchart_data = build_flowchart_data(
#             flow_id=flow_id
#         )
#
#         from utils.dag_util import infer_schema_dag
#         schema_results = infer_schema_dag(
#             nodes=flowchart_data["nodes"],
#             edges=flowchart_data["edges"],
#             target_node_id=node_id
#         )
#
#         print("schema_results", schema_results)
#
#         # 删除node_schema
#         db.query(NodeSchema).filter(
#             NodeSchema.node_id == node_id).delete()
#         db.commit()
#         # 添加新的node_schema
#         new_node_schema = NodeSchema(
#             node_id=node_id, node_schema=json.dumps(schema_results), created_at=datetime.now().isoformat(),
#             updated_at=datetime.now().isoformat())
#         db.add(new_node_schema)
#         db.commit()
#
#     return schema_results
#
#
# @app.route('/get_node_schema', methods=['POST'])
# def get_node_schema():
#     data = request.json
#     node_id = data.get('node_id')
#     if not node_id:
#         return jsonify({"error": "Missing node_id"}), 400
#
#     return get_node_schema_from_db(data['flow_id'], node_id)
#
#
# def get_node_schema_from_db(flow_id, node_id):
#     with SessionLocal() as db:
#         node_schema = db.query(NodeSchema).filter(
#             NodeSchema.node_id == node_id).first()
#         # 如果能查出数据，那么就直接返回。查出来的是个json字符串，需要转换为dict
#         if node_schema and len(node_schema.node_schema) > 0:
#             node_schema_dict = json.loads(node_schema.node_schema)
#             if len(node_schema_dict) > 0:
#                 print(len(node_schema_dict))
#                 print(f'get node schema from db')
#                 print(f'node_schema: {node_schema_dict}')
#                 return node_schema_dict
#
#     print(f'no node schema in db, infer from flowchart_data')
#
#     # 查找node_config，查看config_name=path是否已经配置
#     with SessionLocal() as db:
#         # 从nodes查出node的type
#         node_type = db.query(Node).filter(
#             Node.id == node_id).first().type
#         need_infer_schema = False
#         if node_type == 'File Input':
#             node_config = db.query(NodeConfig).filter(
#                 NodeConfig.config_name == 'path',
#                 NodeConfig.node_id == node_id).first()
#             if not node_config:
#                 print("path is not in node_config,unable to infer schema")
#                 schema_results = []
#             else:
#                 print('11111111111')
#                 need_infer_schema = True
#         elif node_type == 'Left Join':
#             print('22222222222')
#             node_config = db.query(NodeConfig).filter(
#                 NodeConfig.config_name == 'left_join_on',
#                 NodeConfig.node_id == node_id).first()
#             if not node_config:
#                 print("left_join_on is not in node_config,unable to infer schema")
#                 schema_results = []
#             else:
#                 need_infer_schema = True
#         elif node_type == 'Aggregate':
#             print('33333333333')
#             node_config = db.query(NodeConfig).filter(
#                 NodeConfig.config_name == 'groupBy',
#                 NodeConfig.node_id == node_id).first()
#             if not node_config:
#                 print("groupBy is not in node_config,unable to infer schema")
#                 schema_results = []
#             else:
#                 need_infer_schema = True
#         else:
#             need_infer_schema = True
#
#         if need_infer_schema:
#             print("path is in node_config, infer schema from flowchart_data")
#
#             schema_results = infer_schema_from_flowchart_data(
#                 flow_id=flow_id, node_id=node_id)
#         return schema_results
#
#
# def get_preview_data(flow_id, node_id):
#     # 如果没有定义node_schema，那么就从flowchart_data中推断
#     with SessionLocal() as db:
#         node_schema = db.query(NodeSchema).filter(
#             NodeSchema.node_id == node_id).first()
#         if not node_schema:
#             print(f'undefined node schema, unable to preview data')
#             return jsonify([])
#
#     from utils.dag_util import build_flowchart_data, execute_dag
#
#     flowchart_data = build_flowchart_data(
#         flow_id=flow_id
#     )
#
#     res = execute_dag(
#         nodes=flowchart_data["nodes"],
#         edges=flowchart_data["edges"],
#         backend_name="polars",
#         target_node_id=node_id
#     )
#
#     print("flowchart_data", flowchart_data)
#     print("res", res)
#     if node_id in res:
#         # polars 的 head 方法返回的是一个 DataFrame
#         # 需要转换为字典列表
#         print(f"res[data['node_id']]: {res[node_id]}")
#         node_df = res[node_id]
#         res_data = node_df.head(5).to_dicts()
#         res_data_cols = node_df.columns
#         print(f"res_data: {res_data}")
#         response = {
#             "data": res_data,
#             "cols": res_data_cols
#         }
#     else:
#         print(f"{node_id} is not in res")
#         res_data = []
#         res_data_cols = []
#         response = {
#             "data": res_data,
#             "cols": res_data_cols
#         }
#
#     return response
#
#
# # Create database tables
# # Base.metadata.create_all(bind=engine)
#
# if __name__ == '__main__':
#     app.run(debug=True)
