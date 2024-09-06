from unittest.mock import patch
from uuid import UUID

import httpx
import pytest

from mandoline import Mandoline
from mandoline.errors import (
    GenericErrorDetails,
    MandolineError,
    MandolineErrorType,
    handle_error,
)


@pytest.fixture
def api_key():
    return "test_api_key"


@pytest.fixture
def mandoline_client(api_key):
    return Mandoline(api_key=api_key, connect_timeout=1, rwp_timeout=1)


@patch("mandoline.connection_manager.make_request_with_timeout")
def test_api_error_handling(mock_make_request, mandoline_client):
    mock_make_request.side_effect = httpx.HTTPStatusError(
        "API Error",
        request=httpx.Request("GET", "https://test.api.com/metrics/123"),
        response=httpx.Response(
            404, request=httpx.Request("GET", "https://test.api.com/metrics/123")
        ),
    )

    with pytest.raises(MandolineError):
        mandoline_client.get_metric(
            metric_id=UUID("123e4567-e89b-12d3-a456-426614174000")
        )


def test_rate_limit_error_handling(mandoline_client):
    with patch(
        "mandoline.connection_manager.make_request_with_timeout"
    ) as mock_make_request:
        mock_response = httpx.Response(
            status_code=429,
            json={
                "detail": {
                    "type": "RateLimitExceeded",
                    "message": "Rate limit exceeded",
                }
            },
            request=httpx.Request("GET", "https://test.api.com/metrics/"),
        )
        mock_make_request.side_effect = httpx.HTTPStatusError(
            "Rate limit exceeded", request=mock_response.request, response=mock_response
        )

        with pytest.raises(MandolineError) as exc_info:
            mandoline_client.get_metrics()

        assert exc_info.value.details.type == MandolineErrorType.RateLimitExceeded
        assert "Rate limit exceeded" in str(exc_info.value)


def test_validation_error_handling(mandoline_client):
    with patch(
        "mandoline.connection_manager.make_request_with_timeout"
    ) as mock_make_request:
        mock_response = httpx.Response(
            status_code=422,
            json={
                "detail": {
                    "type": "ValidationError",
                    "message": "Validation error occurred",
                    "additional_info": {"errors": "Invalid input data"},
                }
            },
            request=httpx.Request("POST", "https://test.api.com/metrics/"),
        )
        mock_make_request.side_effect = httpx.HTTPStatusError(
            "Validation error", request=mock_response.request, response=mock_response
        )

        with pytest.raises(MandolineError) as exc_info:
            mandoline_client.create_metric(name="", description="Invalid metric")

        assert exc_info.value.details.type == MandolineErrorType.ValidationError
        assert "Validation error occurred" in str(exc_info.value)
        assert exc_info.value.details.errors == "Invalid input data"


def test_handle_error_with_generic_exception():
    error = ValueError("Some unexpected error")
    result = handle_error(err=error)

    assert isinstance(result, MandolineError)
    assert isinstance(result.details, GenericErrorDetails)
    assert result.details.message == "Some unexpected error"


def test_handle_error_with_non_exception():
    error = "Just a string error"
    result = handle_error(err=error)

    assert isinstance(result, MandolineError)
    assert isinstance(result.details, GenericErrorDetails)
    assert result.details.message == "Just a string error"
