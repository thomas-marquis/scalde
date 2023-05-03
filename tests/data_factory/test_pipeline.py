import re
from unittest.mock import MagicMock

import pytest
from scalde.data_factory import DataPipeline, DataValidation, DataValidationError, Exporter, Loader, ParallelSteps, Step

from scalde.easy_testing import DataFrameBuilder, assert_called_once_with_frame


class TestDataPipeline:
    @pytest.fixture
    def fake_dataset(self):
        return DataFrameBuilder().build()

    @pytest.fixture
    def mock_loader(self, fake_dataset):
        mock = MagicMock(spec=Loader)
        mock.load.return_value = fake_dataset
        return mock

    @pytest.fixture
    def mock_exporter(self):
        return MagicMock(spec=Exporter)

    class TestRun:
        def test_should_import_data_from_loader_and_export_it_without_steps(
            self, fake_dataset, mock_loader, mock_exporter
        ):
            # Given
            pipeline = DataPipeline(loader=mock_loader, steps=[], exporter=mock_exporter)

            # When
            pipeline.run()

            # Then
            assert_called_once_with_frame(mock_exporter.export, fake_dataset)

        def test_should_apply_1_step_and_1_validation(self, fake_dataset, mock_loader, mock_exporter):
            # Given
            mock_validation = MagicMock(spec=DataValidation)
            mock_validation.is_valid.return_value = True

            fake_dataset_after_step = DataFrameBuilder().with_columns(["a"]).build()
            mock_step = MagicMock(spec=Step)
            mock_step.process.return_value = fake_dataset_after_step

            pipeline = DataPipeline(
                loader=mock_loader, steps=[mock_step], exporter=mock_exporter, validations=[mock_validation]
            )

            # When
            pipeline.run()

            # Then
            assert_called_once_with_frame(mock_step.process, fake_dataset)
            assert_called_once_with_frame(mock_exporter.export, fake_dataset_after_step)

        def test_should_process_copy_of_dataset(self, fake_dataset, mock_loader, mock_exporter):
            # Given
            mock_step = MagicMock(spec=Step)

            pipeline = DataPipeline(loader=mock_loader, steps=[mock_step], exporter=mock_exporter)

            # When
            pipeline.run()

            # Then
            assert mock_step.process.call_args_list[0].args[0] is not fake_dataset

        def test_should_apply_2_steps_in_correct_order(self, fake_dataset, mock_loader, mock_exporter):
            # Given
            fake_dataset_after_step_1 = DataFrameBuilder().with_columns(["a"]).build()
            mock_step1 = MagicMock(spec=Step)
            mock_step1.process.return_value = fake_dataset_after_step_1

            fake_dataset_after_step_2 = DataFrameBuilder().with_columns(["a", "b"]).build()
            mock_step2 = MagicMock(spec=Step)
            mock_step2.process.return_value = fake_dataset_after_step_2

            pipeline = DataPipeline(loader=mock_loader, steps=[mock_step1, mock_step2], exporter=mock_exporter)

            # When
            pipeline.run()

            # Then
            assert_called_once_with_frame(mock_step1.process, fake_dataset)
            assert_called_once_with_frame(mock_step2.process, fake_dataset_after_step_1)
            assert_called_once_with_frame(mock_exporter.export, fake_dataset_after_step_2)

        def test_should_process_copy_of_dataset_after_each_step(self, fake_dataset, mock_loader, mock_exporter):
            # Given
            fake_dataset_after_step_1 = DataFrameBuilder().with_columns(["a"]).build()
            mock_step1 = MagicMock(spec=Step)
            mock_step1.process.return_value = fake_dataset_after_step_1

            mock_step2 = MagicMock(spec=Step)

            pipeline = DataPipeline(loader=mock_loader, steps=[mock_step1, mock_step2], exporter=mock_exporter)

            # When
            pipeline.run()

            # Then
            assert mock_step1.process.call_args_list[0].args[0] is not fake_dataset
            assert mock_step2.process.call_args_list[0].args[0] is not fake_dataset_after_step_1

        def test_should_apply_3_steps_in_correct_order_and_2_validations(
            self, fake_dataset, mock_loader, mock_exporter
        ):
            # Given
            mock_validation_1 = MagicMock(spec=DataValidation)
            mock_validation_1.is_valid.return_value = True

            mock_validation_2 = MagicMock(spec=DataValidation)
            mock_validation_2.is_valid.return_value = True

            fake_dataset_after_step_1 = DataFrameBuilder().with_columns(["a"]).build()
            mock_step1 = MagicMock(spec=Step)
            mock_step1.process.return_value = fake_dataset_after_step_1

            fake_dataset_after_step_2 = DataFrameBuilder().with_columns(["a", "b"]).build()
            mock_step2 = MagicMock(spec=Step)
            mock_step2.process.return_value = fake_dataset_after_step_2

            fake_dataset_after_step_3 = DataFrameBuilder().with_columns(["a", "b", "c"]).build()
            mock_step3 = MagicMock(spec=Step)
            mock_step3.process.return_value = fake_dataset_after_step_3

            pipeline = DataPipeline(
                loader=mock_loader,
                steps=[mock_step1, mock_step2, mock_step3],
                exporter=mock_exporter,
                validations=[mock_validation_1, mock_validation_2],
            )

            # When
            pipeline.run()

            # Then
            assert_called_once_with_frame(mock_step1.process, fake_dataset)
            assert_called_once_with_frame(mock_step2.process, fake_dataset_after_step_1)
            assert_called_once_with_frame(mock_step3.process, fake_dataset_after_step_2)
            assert_called_once_with_frame(mock_exporter.export, fake_dataset_after_step_3)

        def test_should_apply_parallel_step_with_same_dataset_input(self, mock_loader, mock_exporter):
            # Given
            fake_dataset = DataFrameBuilder().build()
            parallel_step = MagicMock(spec=ParallelSteps)
            parallel_step.process.return_value = fake_dataset

            pipeline = DataPipeline(loader=mock_loader, steps=[parallel_step], exporter=mock_exporter)

            # When
            pipeline.run()

            # Then
            assert_called_once_with_frame(parallel_step.process, fake_dataset)

        def test_should_apply_all_steps_dtypes_at_the_end_of_processing(self, mock_loader, mock_exporter):
            # Given
            input_dataset = (
                DataFrameBuilder()
                .with_columns(["name", "age"])
                .with_row(name="toto", age=12)
                .with_row(name="lolo", age=13)
                .build()
            )

            mock_step_1 = MagicMock(spec=Step)
            mock_step_1.get_dtypes.return_value = {"name": "string", "age": "float64"}
            df_builder_1 = (
                DataFrameBuilder()
                .with_columns(["name", "age"])
                .with_row(name="Toto", age=12.0)
                .with_row(name="Lolo", age=13.0)
            )
            mock_step_1.process.return_value = df_builder_1.build()

            mock_step_2 = MagicMock(spec=Step)
            mock_step_2.get_dtypes.return_value = {"job": "category"}
            df_builder_2 = (
                DataFrameBuilder()
                .with_columns(["name", "age", "job"])
                .with_row(name="Toto", age=12.0, job="student")
                .with_row(name="Lolo", age=13.0, job="photographer")
            )
            mock_step_2.process.return_value = df_builder_2.build()

            mock_step_3 = MagicMock(spec=Step)
            mock_step_3.get_dtypes.return_value = {"job": "category", "salary": "float64"}
            df_builder_3 = (
                DataFrameBuilder()
                .with_columns(["name", "job", "salary"])
                .with_row(name="Toto", job="student", salary=1000.0)
                .with_row(name="Lolo", job="photographer", salary=2000.0)
            )
            mock_step_3.process.return_value = df_builder_3.build()

            mock_loader.load.return_value = input_dataset

            pipeline = DataPipeline(
                steps=[mock_step_1, mock_step_2, mock_step_3], loader=mock_loader, exporter=mock_exporter
            )

            # When
            pipeline.run()

            # Then
            assert_called_once_with_frame(
                mock_exporter.export,
                df_builder_3.with_dtypes(name="string", job="category", salary="float64").build(),
            )

        def test_should_raise_validation_error_when_validations_present_and_invalid_output_data(
            self, mock_loader, mock_exporter
        ):
            # Given
            mock_validation = MagicMock(spec=DataValidation)
            mock_validation.get_name.return_value = "my_validation"
            mock_validation.is_valid.return_value = False

            input_dataset = DataFrameBuilder().with_columns(["name", "age"]).build()
            mock_loader = MagicMock(spec=Loader)
            mock_loader.load.return_value = input_dataset

            mock_step = MagicMock(spec=Step)
            mock_step.get_dtypes.return_value = {}
            final_dataset = DataFrameBuilder().with_columns(["name", "age"]).build()
            mock_step.process.return_value = final_dataset

            pipeline = DataPipeline(
                steps=[mock_step], loader=mock_loader, exporter=mock_exporter, validations=[mock_validation]
            )

            # When & Then
            with pytest.raises(DataValidationError, match=re.escape("Validation my_validation failed")):
                pipeline.run()

            assert_called_once_with_frame(mock_validation.is_valid, final_dataset)
