from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd


class Loader(ABC):
    @abstractmethod
    def load(self) -> pd.DataFrame:
        pass


class CSVLoader(Loader):
    def __init__(self, filepath: str | Path, **kwargs) -> None:
        self._filepath = Path(filepath)
        self._read_csv_kwargs = kwargs

    def load(self) -> pd.DataFrame:
        data = pd.read_csv(self._filepath, **self._read_csv_kwargs)
        self._logger.log(f"Loaded {len(data)} rows from {self._filepath}")
        return data
