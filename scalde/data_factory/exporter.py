import os
from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd


class Exporter(ABC):
    @abstractmethod
    def export(self, data: pd.DataFrame) -> None:
        pass


class CSVExporter(Exporter):
    def __init__(self, filepath: str | Path, **kwargs) -> None:
        self._filepath = Path(filepath)
        self._to_csv_kwargs = kwargs

    def export(self, data: pd.DataFrame) -> None:
        os.makedirs(self._filepath.parent, exist_ok=True)
        data.to_csv(self._filepath, **self._to_csv_kwargs)
        self._logger.log(f"Exported {len(data)} rows to {self._filepath}")
