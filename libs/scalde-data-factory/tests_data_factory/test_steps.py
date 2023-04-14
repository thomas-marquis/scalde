import re
from unittest.mock import MagicMock

import pytest

from data_factory.exceptions import PipelineDefinitionError, PipelineProcessError
from data_factory.steps import ParallelSteps, Step
from easy_testing import DataFrameBuilder, assert_frame_equals


class TestParallelSteps:
    @pytest.fixture
    def fake_dataset(self):
        return DataFrameBuilder().build()

    class TestProcess:
        def test_should_process_data_with_single_step(self, fake_dataset):
            # Given
            data_after_step1 = DataFrameBuilder().with_columns(["col1", "col2"]).with_row((1, 2)).build()
            step = MagicMock(spec=Step)
            step.process.return_value = data_after_step1
            parallel = ParallelSteps(step)

            # When
            res = parallel.process(fake_dataset)

            # Then
            assert step.process.call_count == 1
            assert len(step.process.call_args_list[0].args) == 1
            assert len(step.process.call_args_list[0].kwargs) == 0
            assert_frame_equals(step.process.call_args_list[0].args[0], fake_dataset)
            assert_frame_equals(res, data_after_step1)

        def test_should_process_data_with_multiple_steps(self, fake_dataset):
            # Given
            data_after_step1 = DataFrameBuilder().with_columns(["col1", "col2"]).with_row((1, 2)).build()
            step1 = MagicMock(spec=Step)
            step1.process.return_value = data_after_step1

            data_after_step2 = DataFrameBuilder().with_columns(["col1", "col2"]).with_row((3, 4)).build()
            step2 = MagicMock(spec=Step)
            step2.process.return_value = data_after_step2

            expected_data = DataFrameBuilder().with_columns(["col1", "col2"]).with_row((1, 2)).with_row((3, 4)).build()

            parallel = ParallelSteps(step1, step2)

            # When
            res = parallel.process(fake_dataset)

            # Then
            assert_frame_equals(res, expected_data, check_row_order=False)
            assert_frame_equals(step1.process.call_args_list[0].args[0], fake_dataset)
            assert_frame_equals(step2.process.call_args_list[0].args[0], fake_dataset)

        def test_should_raise_pipeline_error_when_proceed_columns_are_different(self, fake_dataset):
            # Given
            data_after_step1 = DataFrameBuilder().with_columns(["col1", "col2"]).with_row((1, 2)).build()
            step1 = MagicMock(spec=Step)
            step1.process.return_value = data_after_step1

            data_after_step2 = DataFrameBuilder().with_columns(["col1", "col2", "col3"]).with_row((3, 4, 5)).build()
            step2 = MagicMock(spec=Step)
            step2.process.return_value = data_after_step2

            parallel = ParallelSteps(step1, step2)

            # When
            with pytest.raises(PipelineProcessError, match=re.escape("Proceed columns are different between steps")):
                parallel.process(fake_dataset)

        def test_should_raise_definition_error_when_no_steps_are_given(self):
            # When & Then
            with pytest.raises(
                PipelineDefinitionError, match=re.escape("At least one step must be provided to Parallel execution")
            ):
                ParallelSteps()

        def test_should_apply_last_step_output_dtypes(self, fake_dataset):
            # Given
            data_after_step1 = DataFrameBuilder().with_columns(["col1", "col2"]).with_row((1, 2)).build()
            step1 = MagicMock(spec=Step)
            step1.process.return_value = data_after_step1
            step1.get_dtypes.return_value = {"col1": "object", "col2": "float64"}

            data_after_step2 = DataFrameBuilder().with_columns(["col1", "col2"]).with_row((3, 4)).build()
            step2 = MagicMock(spec=Step)
            step2.process.return_value = data_after_step2
            step2.get_dtypes.return_value = {"col1": "string", "col2": "float64"}

            expected_data = (
                DataFrameBuilder()
                .with_columns(["col1", "col2"])
                .with_dtypes(col1="string", col2="float64")
                .with_row((1, 2))
                .with_row((3, 4))
                .build()
            )

            parallel = ParallelSteps(step1, step2)

            # When
            res = parallel.process(fake_dataset)

            # Then
            assert_frame_equals(res, expected_data, check_dtype=True)

    class TestGetName:
        def test_should_concatenate_all_steps_names(self):
            # Given
            step1 = MagicMock(spec=Step)
            step1.get_name.return_value = "step1"

            step2 = MagicMock(spec=Step)
            step2.get_name.return_value = "step2"

            parallel = ParallelSteps(step1, step2)

            # When
            res = parallel.get_name()

            # Then
            assert res == "step1_step2"
