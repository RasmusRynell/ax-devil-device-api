from typing import TypeVar, Generic, Optional, Any, Dict, Union
from dataclasses import dataclass, field
from requests import Response as RequestsResponse
from ..utils.errors import BaseError, FeatureError

T = TypeVar('T')

@dataclass(frozen=True)
class TransportError:
    """Immutable transport-level error information."""
    code: str
    message: str
    original_error: Optional[Exception] = None
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class TransportResponse:
    """Low-level response from the device API.
    
    This class is part of Layer 1 (Communications Layer) and should not contain
    any feature-specific logic. It only handles transport-level success/failure
    and raw response data.
    """
    
    raw_response: Optional[RequestsResponse] = None
    error: Optional[BaseError] = None

    def __post_init__(self):
        """Validate response state."""
        if self.raw_response is not None and self.error is not None:
            raise ValueError("TransportResponse cannot have both response and error")

    @property
    def is_transport_success(self) -> bool:
        """Whether the transport-level request succeeded."""
        return self.error is None

    @classmethod
    def from_response(cls, response: RequestsResponse) -> 'TransportResponse':
        """Create successful transport response."""
        return cls(raw_response=response)

    @classmethod
    def from_error(cls, error: BaseError) -> 'TransportResponse':
        """Create a response from an error."""
        return cls(error=error)

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
    def success(self) -> bool:
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

    @classmethod
    def from_transport(cls, response: TransportResponse) -> 'FeatureResponse[T]':
        """Create a feature response from a transport response."""
        if not response.is_transport_success:
            return cls.create_error(response.error)
        return cls()