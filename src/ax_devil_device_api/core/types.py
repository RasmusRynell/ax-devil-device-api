from typing import TypeVar, Generic, Optional, Any, Dict, Union
from dataclasses import dataclass, field
from requests import Response as RequestsResponse
from ..utils.errors import BaseError, FeatureError

T = TypeVar('T')

@dataclass(frozen=True)
class FeatureResponse(Generic[T]):
    """High-level response from a feature operation.
    
    This class is part of Layer 2 (Feature Layer) and handles feature-specific
    success/failure and typed response data.
    
    Type Parameters:
        T: The type of the response data
    """
    
    _data: Optional[T] = None
    _error: Optional[BaseError] = None

    def __post_init__(self):
        """Validate response state."""
        if self._data is not None and self._error is not None:
            raise ValueError("FeatureResponse cannot have both data and error")

    @property
    def is_success(self) -> bool:
        """Whether the feature operation succeeded."""
        return self._error is None

    @property
    def data(self) -> Optional[T]:
        """Access the response data."""
        return self._data

    @property
    def error(self) -> Optional[BaseError]:
        """Access the error."""
        return self._error

    @classmethod
    def ok(cls, data: T) -> 'FeatureResponse[T]':
        """Create a successful response with data."""
        return cls(_data=data)

    @classmethod
    def create_error(cls, error: BaseError) -> 'FeatureResponse[T]':
        """Create an error response."""
        return cls(_error=error)