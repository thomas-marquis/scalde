from abc import ABC, abstractmethod

import pandas as pd


class DataValidation(ABC):
    @abstractmethod
    def is_valid(self, data: pd.DataFrame) -> bool:
        pass

    def get_name(self) -> str:
        return self.__class__.__name__
