import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# ========== 后端基类接口 ==========


class ETLBackend:
    def read_csv(self, params): raise NotImplementedError
    def filter(self, df, params): raise NotImplementedError
    def aggregate(self, df, params): raise NotImplementedError
    def output(self, df, params): return df  # 默认直接返回

# ========== Pandas 实现 ==========


class PandasBackend(ETLBackend):
    def read_csv(self, _, params):
        print(params)
        print(_)
        df = pd.read_csv(params["path"])
        df["name"] = df["name"]
        df["age"] = df["age"].astype(int)
        df["country"] = df["country"]
        df["salary"] = df["salary"].astype(float)
        return df

    def filter(self, df, params):
        return df[df[params["col"]] > params["value"]]

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
            "filter": self.backend.filter,
            "aggregate": self.backend.aggregate,
            "output": self.backend.output
        }

    def run(self, op_name, input_df, params):
        return self.dispatch[op_name](input_df, params)

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

        result = operator.run(op, inputs[0] if inputs else None, params)
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


# ========== 测试数据结构 ==========
flowchart_data = {
    "nodes": [
        {"id": "1", "type": "read_csv", "params": {"path": "file.csv"}},
        {"id": "2", "type": "filter", "params": {
            "col": "age", "op": ">", "value": 30}},
        {"id": "3", "type": "aggregate", "params": {
            "by": "country", "agg": "mean"}},
        {"id": "4", "type": "output", "params": {}}
    ],
    "edges": [
        {"source": "1", "target": "2"},
        {"source": "2", "target": "3"},
        {"source": "3", "target": "4"}
    ]
}

# ========== 执行 ==========
res = execute_dag(
    nodes=flowchart_data["nodes"],
    edges=flowchart_data["edges"],
    backend_name="pandas"  # 👈 可以切换为 "polars"
)

print("最终结果：")
print(res["4"])
