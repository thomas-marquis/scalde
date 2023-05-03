from scalde.easy_testing.builders import DataFrameBuilder


class TestDataFrameBuilder:
    def test_should_build_empty_dataframe(self):
        df = DataFrameBuilder.a_dataframe().build()
        assert df.empty

    def test_should_build_dataframe_with_columns(self):
        df = DataFrameBuilder.a_dataframe().with_columns(["a", "b"]).build()
        assert df.columns.tolist() == ["a", "b"]

    def test_should_build_dataframe_with_1_row(self):
        df = DataFrameBuilder.a_dataframe().with_columns(["a", "b"]).with_row((1, 2)).build()
        assert df.values.tolist() == [[1, 2]]
        assert df.shape == (1, 2)

    def test_should_build_dataframe_with_2_rows(self):
        df = DataFrameBuilder.a_dataframe().with_columns(["a", "b"]).with_row((1, 2)).with_row((3, 4)).build()
        assert df.values.tolist() == [[1, 2], [3, 4]]
        assert df.shape == (2, 2)

    def test_should_build_dataframe_with_dtypes(self):
        df = (
            DataFrameBuilder.a_dataframe()
            .with_columns(["a", "b"])
            .with_row((1, 2))
            .with_dtypes(a="int64", b="float64")
            .build()
        )
        assert df.dtypes.tolist() == ["int64", "float64"]

    def test_should_build_dataframe_with_1_row_with_kwargs_style(self):
        df = DataFrameBuilder.a_dataframe().with_columns(["a", "b"]).with_row(a=1, b=2).build()
        assert df.values.tolist() == [[1, 2]]
        assert df.shape == (1, 2)

    def test_should_build_dataframe_with_unordered_row_data_kwargs_style(self):
        df = DataFrameBuilder.a_dataframe().with_columns(["a", "b"]).with_row(b=2, a=1).build()
        assert df.values.tolist() == [[1, 2]]
        assert df.shape == (1, 2)
