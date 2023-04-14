import pandas as pd


class DataFrameBuilder:
    def __init__(self):
        self.columns = []
        self.rows = []
        self.dtypes = {}

    @classmethod
    def a_dataframe(cls):
        return cls()

    def with_columns(self, columns: list[str]) -> "DataFrameBuilder":
        self.columns = columns
        return self

    def with_row(self, row: tuple | None = None, **kwargs) -> "DataFrameBuilder":
        if row:
            self.rows.append(row)
        elif kwargs:
            self.rows.append(tuple(kwargs.get(column) for column in self.columns))

        return self

    def with_dtypes(self, **kwargs) -> "DataFrameBuilder":
        self.dtypes |= kwargs
        return self

    def build(self) -> pd.DataFrame:
        df = pd.DataFrame(columns=self.columns, data=self.rows)
        if self.dtypes:
            df = df.astype(self.dtypes)
        return df
