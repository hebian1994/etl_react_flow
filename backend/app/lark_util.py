from lark import Lark, Transformer
import polars as pl

# 支持基本比较、逻辑 and/or
grammar = r"""
    ?start: expr

    ?expr: expr "and" term   -> and_expr
         | expr "or" term    -> or_expr
         | term

    ?term: col COMP_OP value                     -> comp_expr
         | col "in" "(" value_list ")"           -> in_expr
         | col "not" "in" "(" value_list ")"     -> not_in_expr
         | "(" expr ")"

    col: CNAME
    value: SIGNED_NUMBER | ESCAPED_STRING
    value_list: value ("," value)*

    %import common.CNAME
    %import common.SIGNED_NUMBER
    %import common.ESCAPED_STRING
    %import common.WS
    %ignore WS

    COMP_OP: "==" | "!=" | ">" | "<" | ">=" | "<="
"""


# 语法树转换为 polars 表达式


class ExprTransformer(Transformer):
    def number(self, n):
        return int(n[0]) if '.' not in n[0] else float(n[0])

    def col(self, name):
        return pl.col(str(name[0]))

    def value(self, v):
        val = v[0]
        if isinstance(val, str) and val.startswith('"'):
            return val.strip('"')
        elif isinstance(val, str) and val.startswith("'"):
            return val.strip("'")
        else:
            return int(val) if '.' not in val else float(val)

    def value_list(self, items):
        return items

    def comp_expr(self, items):
        col, op, val = items
        return {
            "==": col == val,
            "!=": col != val,
            ">": col > val,
            "<": col < val,
            ">=": col >= val,
            "<=": col <= val
        }[str(op)]

    def in_expr(self, items):
        col, vals = items
        return col.is_in(vals)

    def not_in_expr(self, items):
        col, vals = items
        return ~col.is_in(vals)

    def and_expr(self, items):
        return items[0] & items[1]

    def or_expr(self, items):
        return items[0] | items[1]


def filter_df(df, condition: str):
    parser = Lark(grammar, parser='lalr', transformer=ExprTransformer())
    try:
        expr = parser.parse(condition)
        return df.filter(expr)
    except Exception as e:
        print(f"Error parsing condition: {condition}")
        print(e)
        return df


df = pl.DataFrame({
    "age": [20, 30, 40],
    "salary": [3000, 5000, 7000]
})

# filtered_df = filter_df(df, "age > 25 and salary < 6000")
filtered_df = filter_df(df, "age>25")
print(filtered_df)


df = pl.DataFrame({
    "age": [20, 25, 30, 35],
    "name": ["Alice", "Bob", "Charlie", "Alice"]
})

parser = Lark(grammar, parser='lalr', transformer=ExprTransformer())

# 示例：in + and + not in
condition = 'age in (25, 30) and name not in ("Alice", "Charlie")'
expr = parser.parse(condition)

filtered = df.filter(expr)
print(filtered)
