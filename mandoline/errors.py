from enum import Enum
from typing import Any, Dict, Literal, Optional, Union

import httpx
from pydantic import BaseModel

from mandoline.logger import get_logger
from mandoline.utils import safe_json_parse

logger = get_logger(__name__)


class MandolineErrorType(str, Enum):
    ValidationError = "ValidationError"
    RateLimitExceeded = "RateLimitExceeded"
    TimeoutError = "TimeoutError"
    HTTPError = "HTTPError"
    RequestError = "RequestError"
    GenericError = "GenericError"


class BaseErrorDetails(BaseModel):
    type: MandolineErrorType
    message: str


class ValidationErrorDetails(BaseErrorDetails):
    type: Literal[MandolineErrorType.ValidationError] = (
        MandolineErrorType.ValidationError
    )
    errors: str


class RateLimitExceededErrorDetails(BaseErrorDetails):
    type: Literal[MandolineErrorType.RateLimitExceeded] = (
        MandolineErrorType.RateLimitExceeded
    )


class TimeoutErrorDetails(BaseErrorDetails):
    type: Literal[MandolineErrorType.TimeoutError] = MandolineErrorType.TimeoutError


class HTTPErrorDetails(BaseErrorDetails):
    type: Literal[MandolineErrorType.HTTPError] = MandolineErrorType.HTTPError
    status_code: int
    status_text: str
    response_text: str
    response_json: Optional[Dict[str, Any]] = None


class RequestErrorDetails(BaseErrorDetails):
    type: Literal[MandolineErrorType.RequestError] = MandolineErrorType.RequestError
    request: Dict[str, str]


class GenericErrorDetails(BaseErrorDetails):
    type: Literal[MandolineErrorType.GenericError] = MandolineErrorType.GenericError
    status_code: Optional[int] = None
    errors: Optional[str] = None
    stack: Optional[str] = None


MandolineErrorDetails = Union[
    ValidationErrorDetails,
    RateLimitExceededErrorDetails,
    TimeoutErrorDetails,
    HTTPErrorDetails,
    RequestErrorDetails,
    GenericErrorDetails,
]


class MandolineError(Exception):
    def __init__(self, *, details: MandolineErrorDetails):
        super().__init__(details.message)
        self.details: MandolineErrorDetails = details


def handle_error(*, err: Any) -> MandolineError:
    if isinstance(err, MandolineError):
        return err

    error_details: MandolineErrorDetails

    if isinstance(err, httpx.HTTPStatusError):
        error_details = create_http_error_details(response=err.response)
    elif isinstance(err, Exception):
        error_details = create_error_details(error=err)
    else:
        error_details = create_generic_error_details(err=err)

    if error_details.message:
        logger.error(f"Error: {error_details}")

    return MandolineError(details=error_details)


def create_http_error_details(*, response: httpx.Response) -> MandolineErrorDetails:
    response_text = response.text
    response_json = safe_json_parse(json_string=response_text)
    detail = response_json.get("detail", {}) if response_json else {}

    if isinstance(detail, str):
        return HTTPErrorDetails(
            message=f"Unexpected error: {detail}",
            status_code=response.status_code,
            status_text=response.reason_phrase,
            response_text=response_text,
            response_json=response_json,
        )

    error_type = detail.get("type", "")
    message = detail.get("message", "")
    additional_info = detail.get("additional_info", {})

    if error_type == MandolineErrorType.ValidationError:
        return ValidationErrorDetails(
            message=message or "Validation error",
            errors=additional_info.get("errors", "Unknown validation error"),
        )
    elif error_type == MandolineErrorType.RateLimitExceeded:
        return RateLimitExceededErrorDetails(message=message or "Rate limit exceeded")
    elif error_type == MandolineErrorType.RequestError:
        return RequestErrorDetails(
            message=message or "Request error occurred",
            request={
                "url": additional_info.get("request", {}).get("url", str(response.url)),
                "method": additional_info.get("request", {}).get(
                    "method", response.request.method
                ),
            },
        )
    else:
        return HTTPErrorDetails(
            message=message
            or f"HTTP Error: {response.status_code} {response.reason_phrase}",
            status_code=response.status_code,
            status_text=response.reason_phrase,
            response_text=response_text,
            response_json=response_json,
        )


def create_error_details(*, error: Exception) -> MandolineErrorDetails:
    if isinstance(error, (httpx.ConnectTimeout, httpx.ReadTimeout, TimeoutError)):
        return TimeoutErrorDetails(
            message="The request timed out. The API might be slow or unresponsive. Please try again later."
        )
    else:
        return GenericErrorDetails(
            message=str(error),
            stack=str(error.__traceback__.tb_frame) if error.__traceback__ else None,
        )


def create_generic_error_details(*, err: Any) -> MandolineErrorDetails:
    return GenericErrorDetails(message=str(err))
