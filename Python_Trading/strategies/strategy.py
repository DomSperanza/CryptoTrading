from abc import ABC, abstractproperty, abstractmethod
import numpy as np
import pandas as pd

class Strategy(ABC):
    """
    The Abstract Class defines a template method that contains a skeleton of
    some algorithm, composed of calls to (usually) abstract primitive
    operations.

    Concrete subclasses should implement these operations, but leave the
    template method itself intact.
    """
    
    def template_method(self) -> None:
        """
        The template method defines the skeleton of an algorithm.
        """
        self.crossabove()
        self.crossbelow()
        self.applyindicators()
        self.base_operation3()
        self.hook2()

    # These operations already have implementations.

    def crossabove(self, fast: pd.DataFrame, slow: pd.DataFrame) -> pd.Series:
        series = pd.Series(np.where(fast > slow, 1, 0))
        series = series.diff()
        series = np.where(series == 1, 1, 0)
        return series


    def crossbelow(self, fast: pd.DataFrame, slow: pd.DataFrame) -> pd.Series:
        series = pd.Series(np.where(fast < slow, 1, 0))
        series = series.diff()
        series = np.where(series == 1, 1, 0)
        return series

    # These operations have to be implemented in subclasses.

    @abstractmethod
    def applyindicators(self) -> None:
        '''Apply the indicators of the given strategy'''

    @abstractmethod
    def required_operations2(self) -> None:
        pass

    # These are "hooks." Subclasses may override them, but it's not mandatory
    # since the hooks already have default (but empty) implementation. Hooks
    # provide additional extension points in some crucial places of the
    # algorithm.

    def hook1(self) -> None:
        pass

    def hook2(self) -> None:
        pass

    