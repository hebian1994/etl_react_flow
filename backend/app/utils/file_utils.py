import os
import polars as pl
import pandas as pd


def get_file_schema(params, backend_name="polars"):
    nrows = 2

    df = read_csv(params["path"], backend=backend_name, nrows=nrows)

    if backend_name == "polars":

        schema = []
        for col in df.columns:
            col_data = df[col].cast(str)

            try:
                col_data.cast(pl.Int64)
                dtype = "int"
            except pl.exceptions.InvalidOperationError:
                try:
                    col_data.cast(pl.Float64)
                    dtype = "float"
                except pl.exceptions.InvalidOperationError:
                    dtype = "str"

            schema.append({"name": col, "dtype": dtype})

    return schema


def read_csv(fp, backend, nrows=None):
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
    if backend == 'polars':
        dtype_map = {
            # 'int64': pl.Int64,
            'int': pl.Int64,
            # 'float64': pl.Float64,
            'float': pl.Float64,
            'str': pl.Utf8,
            # 'string': pl.Utf8,
            # 'bool': pl.Boolean
        }
    elif backend == 'pandas':
        dtype_map = {
            'int': 'int64',
            'float': 'float64',
            'str': 'str',
        }

    dtypes = {
        name: dtype_map.get(dtype.strip(), pl.Utf8)
        for name, dtype in zip(field_names, field_types_str)
    }

    if nrows:
        if backend == 'polars':
            # polars 读取前 nrows 行
            df = pl.read_csv(fp, skip_rows=2, has_header=False,
                             new_columns=field_names, dtypes=dtypes).head(nrows)
        elif backend == 'pandas':
            # pandas 读取前 nrows 行
            df = pd.read_csv(fp, header=2, dtype=dtypes,
                             names=field_names, nrows=nrows)
    else:
        if backend == 'polars':
            df = pl.read_csv(fp, skip_rows=2, has_header=False,
                             new_columns=field_names, dtypes=dtypes)
        elif backend == 'pandas':
            df = pd.read_csv(fp, header=2, dtype=dtypes, names=field_names)

    return df
