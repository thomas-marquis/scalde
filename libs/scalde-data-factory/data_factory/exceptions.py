class DataFactoryBaseException(Exception):
    """Base class for all DataFactory exceptions."""


class PipelineProcessError(DataFactoryBaseException):
    """Raised when a pipeline process fails."""


class PipelineDefinitionError(DataFactoryBaseException):
    """Raised when a pipeline definition is invalid."""


class DataValidationError(DataFactoryBaseException):
    """Raised when a data validation fails."""
