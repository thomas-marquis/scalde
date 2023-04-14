from abc import ABC, abstractmethod
from typing import Any

import pandas as pd

from .exceptions import PipelineDefinitionError, PipelineProcessError


class Step(ABC):
    @abstractmethod
    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_dtypes(self) -> dict[str, Any]:
        pass

    def get_name(self) -> str:
        return self.__class__.__name__


class ParallelSteps(Step):
    def __init__(self, *steps: Step) -> None:
        if not steps:
            raise PipelineDefinitionError("At least one step must be provided to Parallel execution")

        self._steps = steps

    def process(self, dataset: pd.DataFrame) -> pd.DataFrame:
        processing_results: list[pd.DataFrame] = []
        df: pd.DataFrame | None = None
        for step in self._steps:
            df = step.process(dataset.copy())
            processing_results.append(df)

        first_step_cols = list(processing_results[0].columns)
        for result in processing_results:
            if list(result.columns) != first_step_cols:
                raise PipelineProcessError("Proceed columns are different between steps")

        final_df = pd.concat(processing_results, axis=0).reset_index(drop=True)

        return final_df.astype(self.get_dtypes())

    def get_dtypes(self) -> dict[str, Any]:
        return self._steps[-1].get_dtypes()

    def get_name(self) -> str:
        return "_".join([step.get_name() for step in self._steps])
