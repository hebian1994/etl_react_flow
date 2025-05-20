from models import NodeSchema
from file_utils import read_csv
from lark import Lark, Transformer
import polars as pl
from db import SessionLocal  # 你创建 SQLAlchemy Session 的方法
from models import Flow, Node, NodeConfig  # 你需要确保这些模型存在
from sqlalchemy.orm import Session
from db import DATABASE_FILE
import sqlite3
import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os
from ETLBackend import PandasBackend, PolarsBackend
from ETLBackend import ETLBackend

# ========== 操作调度器 ==========


class ETLOperator:
    def __init__(self, backend: ETLBackend):
        self.backend = backend
        self.dispatch = {
            "read_csv": self.backend.read_csv,
            "File Input": self.backend.read_csv,
            "Filter": self.backend.filter,
            "Left Join": self.backend.left_join,
            "aggregate": self.backend.aggregate,
            "Aggregate": self.backend.aggregate,
            "output": self.backend.output,
            "Data Viewer": self.backend.output,
        }

    def run(self, op_name, input_df, params):
        print(f"run op_name: {op_name}")
        print(f"run input_df: {input_df}")
        print(f"run params: {params}")
        return self.dispatch[op_name](input_df, params)

    def run_left_join(self, op_name, input_df1, input_df2, params):
        return self.dispatch[op_name](input_df1, input_df2, params)

# ========== DAG 执行器 ==========


def execute_dag(nodes, edges, backend_name="pandas", target_node_id=None):
    if backend_name == "pandas":
        backend = PandasBackend()
    elif backend_name == "polars":
        backend = PolarsBackend()
    else:
        raise ValueError(f"Unsupported backend: {backend_name}")

    operator = ETLOperator(backend)

    G = nx.DiGraph()
    for node in nodes:
        G.add_node(node["id"], op=node["type"], params=node["params"])
    for edge in edges:
        G.add_edge(edge["source"], edge["target"])

    if target_node_id:
        if target_node_id not in G.nodes:
            raise ValueError(f"Target node '{target_node_id}' not in DAG")
        # 获取所有祖先 + 目标节点本身
        required_nodes = nx.ancestors(G, target_node_id)
        required_nodes.add(target_node_id)
        subgraph = G.subgraph(required_nodes).copy()
        sorted_nodes = list(nx.topological_sort(subgraph))
    else:
        sorted_nodes = list(nx.topological_sort(G))

    results = {}

    for node_id in sorted_nodes:
        op = G.nodes[node_id]["op"]
        params = G.nodes[node_id]["params"]
        preds = list(G.predecessors(node_id))
        inputs = [results[p] for p in preds] if preds else [None]

        print(f"executing node: {node_id}, inputs: {inputs}")
        if len(inputs) == 2:
            result = operator.run_left_join(op, inputs[0], inputs[1], params)
        else:
            result = operator.run(op, inputs[0], params)
        results[node_id] = result

    print(f"results: {results}")
    return results


def infer_schema_dag(nodes, edges, target_node_id=None, backend_name="polars"):
    G = nx.DiGraph()
    node_map = {node["id"]: node for node in nodes}

    for node in nodes:
        G.add_node(node["id"], op=node["type"], params=node["params"])
    for edge in edges:
        G.add_edge(edge["source"], edge["target"])

    if target_node_id:
        if target_node_id not in G.nodes:
            raise ValueError(f"Target node '{target_node_id}' not in DAG")
        required_nodes = nx.ancestors(G, target_node_id)
        required_nodes.add(target_node_id)
        subgraph = G.subgraph(required_nodes).copy()
        sorted_nodes = list(nx.topological_sort(subgraph))
    else:
        sorted_nodes = list(nx.topological_sort(G))

    schema_results = {}

    print("sorted_nodes", sorted_nodes)

    for node_id in sorted_nodes:
        node = node_map[node_id]
        op = node["type"]
        params = node["params"]
        print("node", node)
        preds = list(G.predecessors(node_id))
        input_schemas = [schema_results[p] for p in preds] if preds else []

        # 推断 schema
        if op == "File Input":
            # 从 params 中取文件路径，读取前几行获取 schema（伪代码/示例）
            from file_utils import get_file_schema
            schema = get_file_schema(params, backend_name)

        elif op == "Filter":
            # 不改变 schema
            schema = input_schemas[0]

        elif op == "Select":
            # 只保留指定列
            selected_columns = params.get("columns", [])
            schema = [col for col in input_schemas[0]
                      if col["name"] in selected_columns]

        elif op == "Aggregate":
            # {'id': '2e8e4f5b-0e1a-4726-9e5f-b9f363e8b282', 'type': 'Aggregate', 'params': {'groupBy': '["name", "country"]', 'aggregations': '[{"column": "age", "operation": "sum"}, {"column": "salary", "operation": "avg"}]'}}
            # [{"name": "sum_sales", "dtype": "float"}]
            group_by_cols = params.get("groupBy")
            agg_config = params.get("aggregations")
            group_by_cols = json.loads(group_by_cols)  # ['name', 'country']
            agg_cols = []
            for kv in json.loads(agg_config):
                agg_cols.append(kv['column'])

            total_cols = group_by_cols+agg_cols

            schema = [col for col in input_schemas[0]
                      if col["name"] in total_cols]

        elif op == "Left Join":
            left_schema = input_schemas[0]
            right_schema = input_schemas[1]
            print("left_schema", left_schema)
            print("right_schema", right_schema)

            # 加上前缀避免列名冲突（可以更精细地处理）
            right_prefixed = [
                {"name": f"right_{col['name']}", "dtype": col["dtype"]} for col in right_schema
                if col["name"] not in {col["name"] for col in left_schema}
            ]
            print("right_prefixed", right_prefixed)
            schema = left_schema + right_prefixed

        else:
            # 默认传递上一个 schema
            schema = input_schemas[0] if input_schemas else []

        schema_results[node_id] = schema

    return schema_results[target_node_id] if target_node_id else schema_results

# ========== 可视化 ==========


def draw_dag(G):
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G)
    labels = {n: f"{n}: {G.nodes[n]['op']}" for n in G.nodes}
    nx.draw(G, pos, with_labels=True, labels=labels, node_color='lightgreen',
            node_size=2000, font_size=10, arrows=True, arrowsize=20)
    plt.title("ETL 执行 DAG 图")
    plt.tight_layout()
    plt.show()


def build_flowchart_data(flow_id):
    print(f"flow_id: {flow_id}")

    session: Session = SessionLocal()

    try:
        # ① 获取指定 flow_id 的 flow_data
        flow_entry = session.query(Flow).filter(
            Flow.flow_id == flow_id).first()
        if not flow_entry:
            raise ValueError(f"Flow ID {flow_id} not found.")

        # 转成字典
        target_flow = json.loads(flow_entry.flow_data)

        # ② 获取所有节点类型
        node_type_map = {
            node.id: node.type for node in session.query(Node).all()}

        # ③ 获取所有节点配置
        node_config_map = {}
        configs = session.query(NodeConfig).all()
        for config in configs:
            node_id = config.node_id
            if node_id not in node_config_map:
                node_config_map[node_id] = []
            node_config_map[node_id].append(
                {config.config_name: config.config_param})

        print(f"node_config_map: {node_config_map}")

        # ④ 构建 nodes 数据
        nodes = []
        print(f"target_flow: {target_flow}")
        for node in target_flow['nodes']:
            node_id = node['id']
            node_type = node_type_map.get(node_id, "unknown")
            config_param_arr = node_config_map.get(node_id, [])
            print(f"config_param_arr: {config_param_arr}")

            params = {'node_id': node_id}
            if node_type == "File Input":
                for config in config_param_arr:
                    if 'path' in config:
                        params["path"] = config['path']
            elif node_type == "Filter":
                for config in config_param_arr:
                    if 'condition' in config:
                        params["condition"] = config['condition']
            elif node_type == "Left Join":
                for config in config_param_arr:
                    if 'left_join_on' in config:
                        params["left_join_on"] = config['left_join_on']
            elif node_type == "Aggregate":
                for config in config_param_arr:
                    if 'groupBy' in config:
                        params["groupBy"] = config['groupBy']
                    if 'aggregations' in config:
                        params["aggregations"] = config['aggregations']
            elif node_type == "Data Viewer":
                params = {'node_id': node_id}
            else:
                raise ValueError(f"Unknown node type: {node_type}")

            nodes.append({
                "id": node_id,
                "type": node_type,
                "params": params
            })

        print("nodes", nodes)

        # ⑤ 构建 edges 数据
        edges = [
            {"source": edge['source'], "target": edge['target']}
            for edge in target_flow.get('edges', [])
        ]

        return {"nodes": nodes, "edges": edges}

    finally:
        session.close()
