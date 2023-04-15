from typing import Any, Iterable
from unittest.mock import MagicMock

import pandas as pd


class AssertFrame:
    def __init__(self, data: pd.DataFrame, **kwargs) -> None:
        self.data = data
        self.kwargs = kwargs


def assert_called_once_with_frame(mock: MagicMock, *args, **kwargs) -> None:
    if not mock.call_count == 1:
        raise AssertionError(f"Expected to be called once but was called {mock.call_count} times")

    call_args, call_kwargs = mock.call_args

    if len(call_args) != len(args):
        raise AssertionError(f"Expected {len(args)} argument(s) but got {len(call_args)}")

    if (expected_kwargs := kwargs.keys()) != (actual_kwargs := call_kwargs.keys()):
        raise AssertionError(
            f"Expected keyword argument(s) {', '.join(expected_kwargs)} but got {', '.join(actual_kwargs)}"
        )

    for arg, call_arg in zip(args, call_args):
        _assert_frame_equals_in_args(arg, call_arg)

    for (actual_kwarg, actual_value), (expected_kwarg, expected_value) in zip(call_kwargs.items(), kwargs.items()):
        _assert_frame_equals_in_kwargs(actual_kwarg, actual_value, expected_kwarg, expected_value)


def assert_contains_line(data: pd.DataFrame, line: Iterable) -> None:
    columns = data.columns

    if not _is_contains_line(data, line):
        msg = f"Expected line {_render_line(columns, line)} not found in dataframe"
        raise AssertionError(msg)


def assert_contains_lines(data: pd.DataFrame, lines: Iterable[Iterable]) -> None:
    mismatches = []
    for line in lines:
        if not _is_contains_line(data, line):
            mismatches.append(line)

    if not mismatches:
        return None

    columns = data.columns
    if len(mismatches) == 1:
        msg = f"Expected line {_render_line(columns, mismatches[0])} not found in dataframe"
    else:
        lines_str = ", ".join([_render_line(columns, line) for line in mismatches])
        msg = f"Expected lines {lines_str} not found in dataframe"
    raise AssertionError(msg)


def assert_frame_partially_equals(
    dataframe_left: pd.DataFrame,
    dataframe_right: pd.DataFrame,
    columns: Iterable[str],
    check_row_order: bool = True,
    **kwargs,
) -> None:
    _check_columns(dataframe_left, columns, "left")
    _check_columns(dataframe_right, columns, "right")

    df_left, df_right = dataframe_left[columns].copy(), dataframe_right[columns].copy()
    if not check_row_order:
        df_left, df_right = df_left.sort_values(columns).reset_index(drop=True), df_right.sort_values(
            columns
        ).reset_index(drop=True)

    pd.testing.assert_frame_equal(df_left, df_right, **kwargs)


def assert_frame_equals(
    dataframe_left: pd.DataFrame,
    dataframe_right: pd.DataFrame,
    check_row_order: bool = True,
    check_columns_order: bool = True,
    **kwargs,
) -> None:
    """Compare two dataframes acording to their values.

    Args:
        dataframe_left (pd.DataFrame)
        dataframe_right (pd.DataFrame)
        check_row_order (bool, optional): Defaults to True.
        check_columns_order (bool, optional): Defaults to True.
        **kwargs: pd.testing.assert_frame_equal kwargs

    Raises:
        AssertionError: when dataframes are not equals
    """

    if not (left_cols := sorted(list(dataframe_left.columns))) == (right_cols := sorted(list(dataframe_right.columns))):
        raise AssertionError(
            f"Columns are different. "
            f"left ones are {_format_columns_as_string(left_cols)} "
            f"and right ones are {_format_columns_as_string(right_cols)}"
        )

    columns = list(dataframe_left.columns)

    df_left, df_right = dataframe_left.copy(), dataframe_right.copy()

    if not check_columns_order:
        df_left = df_left[columns]
        df_right = df_right[columns]

    if not check_row_order:
        df_left = df_left.sort_values(columns).reset_index(drop=True)
        df_right = df_right.sort_values(columns).reset_index(drop=True)

    pd.testing.assert_frame_equal(df_left, df_right, **kwargs)


def _format_columns_as_string(columns: Iterable[str]) -> str:
    col_list = ", ".join([f"'{col}'" for col in columns])
    return f"[{col_list}]"


def _render_line(columns: Iterable[str], line: Iterable) -> str:
    line_str = ", ".join([f"{col}={val}" for col, val in zip(columns, line)])
    return f"<{line_str}>"


def _is_contains_line(data: pd.DataFrame, line: Iterable) -> bool:
    columns = data.columns
    if (expected := len(columns)) != (got := len(line)):
        raise ValueError(f"Line size mismatch: expected {expected}, got {got}")

    mask = None
    for col, expected_value in zip(columns, line):
        if mask is None:
            mask = data[col] == expected_value
        else:
            mask = mask & (data[col] == expected_value)

    nb_matches = data.loc[mask, columns].shape[0]

    return nb_matches > 0


def _check_columns(dataframe: pd.DataFrame, columns: Iterable[str], side: str) -> None:
    missing_columns = set(columns) - set(dataframe.columns)
    if missing_columns:
        missing_columns_msg = ", ".join([f"'{col}'" for col in missing_columns])
        raise ValueError(f"Column(s) {missing_columns_msg} not found in {side} dataframe")


def _assert_frame_equals_in_kwargs(
    actual_kwarg: dict, actual_value: Any, expected_kwarg: dict, expected_value: Any
) -> None:
    if isinstance(expected_value, pd.DataFrame):
        assert_frame_equals(actual_value, expected_value)
    elif isinstance(expected_value, AssertFrame):
        assert_frame_equals(actual_value, expected_value.data, **expected_value.kwargs)
    else:
        if expected_value != actual_value:
            raise AssertionError(f"Expected {expected_kwarg}={expected_value} but got {actual_kwarg}={actual_value}")


def _assert_frame_equals_in_args(arg: list, call_arg: list) -> None:
    if isinstance(arg, pd.DataFrame):
        assert_frame_equals(call_arg, arg)
    elif isinstance(arg, AssertFrame):
        assert_frame_equals(call_arg, arg.data, **arg.kwargs)
    else:
        if arg != call_arg:
            raise AssertionError(f"Expected {arg} but got {call_arg}")
