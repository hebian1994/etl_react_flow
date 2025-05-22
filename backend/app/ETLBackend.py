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

# ========== 后端基类接口 ==========


class ETLBackend:
    def read_csv(self, params): raise NotImplementedError
    def filter(self, df, params): raise NotImplementedError
    def left_join(self, df1, df2, params): raise NotImplementedError
    def aggregate(self, df, params): raise NotImplementedError
    def output(self, df, params): return df  # 默认直接返回


class PolarsBackend(ETLBackend):
    def read_csv(self, _, params):
        if "path" not in params:
            print("path is not in params")
            return pl.DataFrame()
        fp = params["path"].strip('"')

        # 获取node_id
        node_id = params.get("node_id", None)
        # 从db中获取node_schema
        with SessionLocal() as db:
            node_schema = db.query(NodeSchema).filter(
                NodeSchema.node_id == node_id).first()
            if node_schema:
                node_schema = json.loads(node_schema.node_schema)
                # [{"dtype": "str", "name": "name"}, {"dtype": "int", "name": "age"}, {"dtype": "str", "name": "country"}, {"dtype": "float", "name": "salary"}]
                print(f"node_schema: {node_schema}")
                # 解析node_schema，得到读取的列以及列的数据类型
                read_cols = []
                read_dtypes = {}
                for col in node_schema:
                    read_cols.append(col["name"])
                    read_dtypes[col["name"]] = col["dtype"]
                print(f"read_cols: {read_cols}")
                print(f"read_dtypes: {read_dtypes}")
                dtype_map = {
                    # 'int64': pl.Int64,
                    'int': pl.Int64,
                    # 'float64': pl.Float64,
                    'float': pl.Float64,
                    'str': pl.Utf8,
                    # 'string': pl.Utf8,
                    # 'bool': pl.Boolean
                }
                read_dtypes = {k: dtype_map[v]
                               for k, v in read_dtypes.items()}
                print(f"read_dtypes: {read_dtypes}")

                # 根据read_cols和read_dtypes，读取csv
                df = pl.read_csv(fp, skip_rows=2, has_header=False,
                                 new_columns=read_cols, dtypes=read_dtypes)
                print(f"df: {df}")
                return df
            else:
                print(f"no node schema, unable to read csv")
                raise ValueError(f"no node schema, unable to read csv")

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
            #
            left_cols = df1.columns
            right_cols = df2.columns
            right_final = left_cols
            for col in right_cols:
                if col not in left_cols:
                    right_final.append(col)
            df_joined = df_joined.select(right_final)
            return df_joined
        except Exception as e:
            print(f"Join failed: {e}")
            return df1

    def aggregate(self, df, params):
        # sample :
        # aggregate params: {'groupBy': '["name", "country"]', 'aggregations': '[{"column": "age", "operation": "sum"}, {"column": "salary", "operation": "avg"}]'}
        # 解析aggregate params
        print(f"aggregate params: {params}")
        group_by_cols = params.get("groupBy")
        agg_config = params.get("aggregations")
        group_by_cols = json.loads(group_by_cols)  # ['name', 'country']
        agg_config = json.loads(agg_config)  # list of dicts
        print(f"group_by_cols: {group_by_cols}")
        print(f"agg_config: {agg_config}")

        if not group_by_cols:
            print("Group by column missing")
            return df

        agg_exprs = []
        for agg in agg_config:
            print(f"agg: {agg}")
            col = agg['column']
            op = agg['operation']

            if op == "sum":
                agg_exprs.append(pl.col(col).sum().alias(f"{col}_sum"))
            elif op == "avg":
                agg_exprs.append(pl.col(col).mean().alias(f"{col}_avg"))
            elif op == "min":
                agg_exprs.append(pl.col(col).min().alias(f"{col}_min"))
            elif op == "max":
                agg_exprs.append(pl.col(col).max().alias(f"{col}_max"))
            elif op == "count":
                agg_exprs.append(pl.col(col).count().alias(f"{col}_count"))
            else:
                raise ValueError(f"Unsupported aggregation operation: {op}")

        # Step 3: 执行聚合
        result = df.group_by(group_by_cols).agg(agg_exprs)

        return result


class PandasBackend(ETLBackend):
    def read_csv(self, _, params):
        print(params)
        print(_)
        # 获取文件第一行和第二行的内容，然后根据逗号切割得到字段名和数据类型,注意去掉结尾的换行符
        if "path" not in params:
            print("path is not in params")
            return pd.DataFrame()
        fp = params["path"].strip('"')
        df = read_csv(fp, backend='pandas')

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
