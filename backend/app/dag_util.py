from DB import DATABASE_FILE
import sqlite3
import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

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
        with open(params["path"].strip('"'), 'r', encoding='utf-8') as f:
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
        df = pd.read_csv(params["path"].strip(
            '"'), header=2, dtype=dict(zip(field_names, field_types)), names=field_names)

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

# ========== Polars 示例（可选） ==========
# import polars as pl
# class PolarsBackend(ETLBackend):
#     def read_csv(self, params):
#         return pl.read_csv(params["path"])
#     def filter(self, df, params):
#         return df.filter(pl.col(params["col"]) > params["value"])
#     def aggregate(self, df, params):
#         return df.groupby(params["by"]).agg(pl.col("age").mean())

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
        return self.dispatch[op_name](input_df, params)

    def run_left_join(self, op_name, input_df1, input_df2, params):
        return self.dispatch[op_name](input_df1, input_df2, params)

# ========== DAG 执行器 ==========


def execute_dag(nodes, edges, backend_name="pandas"):
    if backend_name == "pandas":
        backend = PandasBackend()
    # elif backend_name == "polars":
    #     backend = PolarsBackend()
    else:
        raise ValueError(f"Unsupported backend: {backend_name}")

    operator = ETLOperator(backend)

    G = nx.DiGraph()
    for node in nodes:
        G.add_node(node["id"], op=node["type"], params=node["params"])
    for edge in edges:
        G.add_edge(edge["source"], edge["target"])

    # draw_dag(G)

    sorted_nodes = list(nx.topological_sort(G))
    results = {}

    for node_id in sorted_nodes:
        op = G.nodes[node_id]["op"]
        params = G.nodes[node_id]["params"]
        preds = list(G.predecessors(node_id))
        inputs = [results[p] for p in preds] if preds else [None]

        print(f"inputs: {inputs}")
        # 可能不是只有inputs[0]，而是inputs[0]和inputs[1]
        if len(inputs) == 2:
            # handle left join
            result = operator.run_left_join(op, inputs[0], inputs[1], params)
        else:
            result = operator.run(op, inputs[0], params)
        results[node_id] = result

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

    # ① 从 SQLite 数据库中读取指定 flow_id 的 flow_data
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT flow_data FROM flows WHERE flow_id = ?", (flow_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        raise ValueError(f"Flow ID {flow_id} not found.")

    target_flow = json.loads(row[0])

    # ② 读取 nodes 表
    node_type_map = {}
    c.execute("SELECT id, type FROM nodes")
    for row in c.fetchall():
        node_id, node_type = row
        node_type_map[node_id] = node_type

    # ③ 读取 node_configs 表
    node_config_map = {}
    c.execute("SELECT node_id, config_name, config_param FROM node_configs")
    for row in c.fetchall():
        node_id, config_name, config_param = row
        if node_id not in node_config_map:
            node_config_map[node_id] = []
        node_config_map[node_id].append({config_name: config_param})

    conn.close()

    # ④ 构建 nodes 数据
    nodes = []
    for node in target_flow['nodes']:
        node_id = node['id']
        node_type = node_type_map.get(node_id, "unknown")
        params = {}
        config_param_arr = node_config_map.get(node_id, [])

        if node_type == "File Input":
            for config_param_dict in config_param_arr:
                if 'path' in config_param_dict:
                    params = {"path": config_param_dict['path']}
        elif node_type == "Filter":
            for config_param_dict in config_param_arr:
                if 'condition' in config_param_dict:
                    params = {"condition": config_param_dict['condition']}
        elif node_type == "Left Join":
            for config_param_dict in config_param_arr:
                if 'left_join_on' in config_param_dict:
                    params = {
                        "left_join_on": config_param_dict['left_join_on']}

        nodes.append({
            "id": node_id,
            "type": node_type,
            "params": params
        })

    print("nodes", nodes)

    # ⑤ 构建 edges 数据
    edges = []
    for edge in target_flow['edges']:
        edges.append({
            "source": edge['source'],
            "target": edge['target']
        })

    return {"nodes": nodes, "edges": edges}

# flowchart_data = build_flowchart_data(
#     flow_id="43cd13c7-25b3-42f3-8d89-6ea353ac5daa",
# )
# print(flowchart_data)


# ========== 测试数据结构 ==========
# flowchart_data = build_flowchart_data(
#     flow_id='2789aec8-d8c0-40c5-bbcb-1023d15a81c1',
# )

# res = execute_dag(
#     nodes=flowchart_data["nodes"],
#     edges=flowchart_data["edges"],
#     backend_name="pandas"  # 👈 可以切换为 "polars"
# )

# # print("最终结果：")
# print(res)
