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

# ========== 后端基类接口 ==========


class ETLBackend:
    def read_csv(self, params): raise NotImplementedError
    def filter(self, df, params): raise NotImplementedError
    def left_join(self, df1, df2, params): raise NotImplementedError
    def aggregate(self, df, params): raise NotImplementedError
    def output(self, df, params): return df  # 默认直接返回

# ========== Pandas 实现 ==========


class PandasBackend(ETLBackend):
    def read_csv(self, _, params):
        print(params)
        print(_)
        # 获取文件第一行和第二行的内容，然后根据逗号切割得到字段名和数据类型,注意去掉结尾的换行符
        if "path" not in params:
            print("path is not in params")
            return pd.DataFrame()
        fp = params["path"].strip('"')
        if not os.path.exists(fp):
            print(f"File not found: {fp}")
            return pd.DataFrame()
        with open(fp, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            second_line = f.readline().strip()
        print(f"first_line: {first_line}")
        print(f"second_line: {second_line}")
        # 根据逗号切割得到字段名和数据类型
        field_names = first_line.split(',')
        field_types = second_line.split(',')

        # 文件的第一行为表头，第二行为数据类型，第三行开始为数据
        # 需要根据第二行的指定数据类型读取
        # 需要指定列名
        df = pd.read_csv(fp, header=2, dtype=dict(
            zip(field_names, field_types)), names=field_names)

        return df

    def filter(self, df, params):
        print(f"filter params: {params}")
        if params["condition"] == "":
            print("condition is empty")
            return df
        else:
            return df.query(params["condition"])

    def left_join(self, df1, df2, params):
        print(f"left_join params: {params}")
        if 'left_join_on' not in params:
            print("left_join_on is empty")
            return df1
        else:
            print(f"left_join_on: {params['left_join_on']}")
            # will get join condition as "name=name and age=age"
            # will get join condition as "name=name and age=age"
            join_condition = params["left_join_on"].split(" and ")
            # can use left_on and right_on to specify the join condition
            left_on_arr = []
            right_on_arr = []
            for condition in join_condition:
                left_on, right_on = condition.split("=")
                left_on_arr.append(left_on)
                right_on_arr.append(right_on)
            df1 = df1.merge(df2, left_on=left_on_arr,
                            right_on=right_on_arr, how="left")

            df1 = df1.fillna("")

            return df1

    def aggregate(self, df, params):
        return df.groupby(params["by"]).agg({"age": "mean"}).reset_index(drop=False)


class PolarsBackend(ETLBackend):
    def read_csv(self, _, params):
        if "path" not in params:
            print("path is not in params")
            return pl.DataFrame()
        fp = params["path"].strip('"')
        if not os.path.exists(fp):
            print(f"File not found: {fp}")
            return pl.DataFrame()

        with open(fp, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            second_line = f.readline().strip()

        print(f"first_line: {first_line}")
        print(f"second_line: {second_line}")

        field_names = first_line.split(',')
        field_types_str = second_line.split(',')

        # 类型映射（可扩展）
        dtype_map = {
            'int64': pl.Int64,
            'int': pl.Int64,
            'float64': pl.Float64,
            'str': pl.Utf8,
            'string': pl.Utf8,
            'bool': pl.Boolean
        }

        dtypes = {
            name: dtype_map.get(dtype.strip(), pl.Utf8)
            for name, dtype in zip(field_names, field_types_str)
        }

        df = pl.read_csv(fp, skip_rows=2, has_header=False,
                         new_columns=field_names, dtypes=dtypes)
        return df

    def filter(self, df, params):
        condition = params.get("condition", "").strip()
        print(f"filter condition: {condition}")
        if not condition:
            return df

        from lark_util import parser
        print(f"parser: {parser}")
        expr = parser.parse(condition)
        print(f"expr: {expr}")
        filtered = df.filter(expr)
        return filtered

    def left_join(self, df1, df2, params):
        if 'left_join_on' not in params:
            print("left_join_on is missing")
            return df1

        join_condition = params["left_join_on"].split(" and ")
        left_on = []
        right_on = []

        for cond in join_condition:
            l, r = cond.split("=")
            left_on.append(l.strip())
            right_on.append(r.strip())

        try:
            df_joined = df1.join(df2, left_on=left_on,
                                 right_on=right_on, how="left")
            return df_joined
        except Exception as e:
            print(f"Join failed: {e}")
            return df1

    def aggregate(self, df, params):
        by_cols = params.get("by")
        agg_col = params.get("agg_col", "age")  # 默认聚合 age
        agg_func = params.get("agg_func", "mean")

        if not by_cols:
            print("Group by column missing")
            return df

        try:
            if agg_func == "mean":
                agg_expr = pl.col(agg_col).mean().alias(f"{agg_col}_mean")
            elif agg_func == "sum":
                agg_expr = pl.col(agg_col).sum().alias(f"{agg_col}_sum")
            elif agg_func == "count":
                agg_expr = pl.count().alias("count")
            else:
                print(f"Unsupported aggregation function: {agg_func}")
                return df

            result = df.groupby(by_cols).agg([agg_expr])
            return result
        except Exception as e:
            print(f"Aggregation failed: {e}")
            return df


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

        # ④ 构建 nodes 数据
        nodes = []
        print(f"target_flow: {target_flow}")
        for node in target_flow['nodes']:
            node_id = node['id']
            node_type = node_type_map.get(node_id, "unknown")
            config_param_arr = node_config_map.get(node_id, [])

            params = {}
            if node_type == "File Input":
                for config in config_param_arr:
                    if 'path' in config:
                        params = {"path": config['path']}
            elif node_type == "Filter":
                for config in config_param_arr:
                    if 'condition' in config:
                        params = {"condition": config['condition']}
            elif node_type == "Left Join":
                for config in config_param_arr:
                    if 'left_join_on' in config:
                        params = {"left_join_on": config['left_join_on']}

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
