import pandas as pd
import rich
from rich.progress import Progress

from .exceptions import DataValidationError
from .exporter import Exporter
from .loader import Loader
from .steps import Step
from .validations import DataValidation


class DataPipeline:
    def __init__(
        self,
        steps: list[Step],
        loader: Loader,
        exporter: Exporter,
        name: str = "Unnamed pipeline",
        validations: list[DataValidation] | None = None,
    ) -> None:
        self.exporter = exporter
        self.loader = loader
        self.name = name

        self._steps = steps
        self._validations = validations or []

    def run(self) -> None:
        rich.print(f"\n\nRunning pipeline: [bold green]{self.name}[/bold green]")
        dataset = self.loader.load()

        with Progress() as progress:
            for step in progress.track(self._steps, description="Apply steps..."):
                dataset = step.process(dataset.copy())

                progress.console.print(
                    f"Step [bold]{step.get_name()}[/bold] done with "
                    f"data shape: {dataset.shape[0]} rows, {dataset.shape[1]} columns"
                )

        output_data = self._apply_all_dtypes(dataset)

        self._validate_data(output_data)

        self.exporter.export(output_data)

    def _validate_data(self, output_data: pd.DataFrame) -> None:
        if not self._validations:
            rich.print("No validation to apply, skipping...")
            return

        rich.print(f"Validating data with {len(self._validations)} validation(s)...")

        with Progress() as progress:
            for validation in progress.track(self._validations, description="Apply validations..."):
                if not validation.is_valid(output_data):
                    raise DataValidationError(f"Validation {validation.get_name()} failed")
                rich.print(f"Validation [bold]{validation.get_name()}[/bold] [green]passed[/green]")

    def _apply_all_dtypes(self, data: pd.DataFrame) -> pd.DataFrame:
        dtypes = {}
        for step in self._steps:
            dtypes |= step.get_dtypes()

        dtypes = {column: dtype for column, dtype in dtypes.items() if column in data.columns}
        return data.astype(dtypes)
