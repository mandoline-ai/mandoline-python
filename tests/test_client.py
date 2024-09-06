from datetime import datetime, timezone
from unittest.mock import patch
from uuid import UUID

import httpx
import pytest

from mandoline import Mandoline
from mandoline.config import CONNECT_TIMEOUT, MANDOLINE_API_BASE_URL, RWP_TIMEOUT
from mandoline.models import Evaluation, Metric


@pytest.fixture
def api_key():
    return "test_api_key"


@pytest.fixture
def api_base_url():
    return "https://test.api.com"


@pytest.fixture
def mandoline_client(api_key):
    return Mandoline(api_key=api_key)


@pytest.fixture
def mandoline_client_custom(api_key, api_base_url):
    return Mandoline(api_key=api_key, api_base_url=api_base_url)


@pytest.fixture
def mock_metric_data():
    return {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "name": "Test Metric",
        "description": "A test metric",
        "tags": ["test"],
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_evaluation_data():
    return {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "metric_id": "234e5678-e89b-12d3-a456-426614174000",
        "prompt": "Test prompt",
        "response": "Test response",
        "properties": {"key": "value"},
        "score": 0.42,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_httpx_response(mock_metric_data):
    return httpx.Response(
        status_code=200,
        json=mock_metric_data,
        request=httpx.Request("POST", "https://test.api.com/metrics/"),
    )


def test_mandoline_client_initialization(
    mandoline_client_custom, api_key, api_base_url
):
    assert mandoline_client_custom.api_key == api_key
    assert mandoline_client_custom.request_config.api_base_url == api_base_url


def test_mandoline_client_default_config(mandoline_client):
    assert mandoline_client.request_config.api_base_url == MANDOLINE_API_BASE_URL
    assert mandoline_client.request_config.connect_timeout == CONNECT_TIMEOUT
    assert mandoline_client.request_config.rwp_timeout == RWP_TIMEOUT


def test_mandoline_client_initialization_with_env_vars(monkeypatch):
    env_api_key = "env_test_api_key"
    env_api_base_url = "https://env.test.api.com"
    monkeypatch.setenv("MANDOLINE_API_KEY", env_api_key)
    monkeypatch.setenv("MANDOLINE_API_BASE_URL", env_api_base_url)

    client = Mandoline()
    assert client.api_key == env_api_key
    assert client.request_config.api_base_url == env_api_base_url


def test_get_auth_header(mandoline_client, api_key):
    auth_header = mandoline_client._get_auth_header()
    assert auth_header == {"X-API-KEY": api_key}


def test_get_auth_header_no_api_key():
    client = Mandoline(api_key="")
    with pytest.raises(ValueError):
        client._get_auth_header()


@patch("mandoline.connection_manager.make_request_with_timeout")
def test_create_metric(
    mock_make_request, mandoline_client, mock_httpx_response, mock_metric_data
):
    mock_make_request.return_value = mock_httpx_response

    metric = mandoline_client.create_metric(
        name="Test Metric", description="A test metric", tags=["test"]
    )

    assert isinstance(metric, Metric)
    assert metric.name == mock_metric_data["name"]
    assert metric.description == mock_metric_data["description"]
    assert metric.tags == mock_metric_data["tags"]

    mock_make_request.assert_called_once()


@patch("mandoline.connection_manager.make_request_with_timeout")
def test_get_metric(
    mock_make_request, mandoline_client, mock_httpx_response, mock_metric_data
):
    mock_make_request.return_value = mock_httpx_response

    metric_id = UUID(mock_metric_data["id"])
    metric = mandoline_client.get_metric(metric_id=metric_id)

    assert isinstance(metric, Metric)
    assert metric.id == metric_id

    mock_make_request.assert_called_once()


@patch("mandoline.connection_manager.make_request_with_timeout")
def test_get_metrics(mock_make_request, mandoline_client):
    mock_response = httpx.Response(
        status_code=200,
        json=[
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Test Metric 1",
                "description": "A test metric",
                "tags": ["test"],
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
            },
            {
                "id": "223e4567-e89b-12d3-a456-426614174000",
                "name": "Test Metric 2",
                "description": "Another test metric",
                "tags": ["test", "another"],
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
            },
        ],
        request=httpx.Request("GET", "https://test.api.com/metrics/"),
    )
    mock_make_request.return_value = mock_response

    metrics = mandoline_client.get_metrics(skip=0, limit=10, tags=["test"])

    assert len(metrics) == 2
    assert all(isinstance(metric, Metric) for metric in metrics)

    mock_make_request.assert_called_once()


def test_update_metric(mandoline_client):
    with patch(
        "mandoline.connection_manager.make_request_with_timeout"
    ) as mock_make_request:
        mock_response = httpx.Response(
            status_code=200,
            json={
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Updated Metric",
                "description": "An updated test metric",
                "tags": ["test", "updated"],
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-02T00:00:00Z",
            },
            request=httpx.Request(
                "PUT",
                "https://test.api.com/metrics/123e4567-e89b-12d3-a456-426614174000",
            ),
        )
        mock_make_request.return_value = mock_response

        metric_id = UUID("123e4567-e89b-12d3-a456-426614174000")
        updated_metric = mandoline_client.update_metric(
            metric_id=metric_id,
            name="Updated Metric",
            description="An updated test metric",
            tags=["test", "updated"],
        )

        assert updated_metric.name == "Updated Metric"
        assert updated_metric.description == "An updated test metric"
        assert updated_metric.tags == ["test", "updated"]


def test_delete_metric(mandoline_client):
    with patch(
        "mandoline.connection_manager.make_request_with_timeout"
    ) as mock_make_request:
        mock_response = httpx.Response(
            status_code=204,
            request=httpx.Request(
                "DELETE",
                "https://test.api.com/metrics/123e4567-e89b-12d3-a456-426614174000",
            ),
        )
        mock_make_request.return_value = mock_response

        metric_id = UUID("123e4567-e89b-12d3-a456-426614174000")
        mandoline_client.delete_metric(metric_id=metric_id)

        mock_make_request.assert_called_once()


@patch("mandoline.connection_manager.make_request_with_timeout")
def test_evaluate(mock_make_request, mandoline_client):
    mock_responses = [
        httpx.Response(
            status_code=200,
            json={
                "id": f"123e4567-e89b-12d3-a456-42661417400{i}",
                "metric_id": f"234e5678-e89b-12d3-a456-42661417400{i}",
                "prompt": "Test prompt",
                "response": "Test response",
                "properties": {"key": "value"},
                "score": 0.42,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
            },
            request=httpx.Request("POST", "https://test.api.com/evaluations/"),
        )
        for i in range(2)
    ]
    mock_make_request.side_effect = mock_responses

    metrics = [
        Metric(
            id=UUID(f"234e5678-e89b-12d3-a456-42661417400{i}"),
            name=f"Metric {i}",
            description="Test metric",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        for i in range(2)
    ]

    evaluations = mandoline_client.evaluate(
        metrics=metrics,
        prompt="Test prompt",
        response="Test response",
        properties={"key": "value"},
    )

    assert len(evaluations) == 2
    assert all(isinstance(eval, Evaluation) for eval in evaluations)

    assert mock_make_request.call_count == 2


@patch("mandoline.connection_manager.make_request_with_timeout")
def test_create_evaluation(mock_make_request, mandoline_client, mock_evaluation_data):
    mock_response = httpx.Response(
        status_code=200,
        json=mock_evaluation_data,
        request=httpx.Request("POST", "https://test.api.com/evaluations/"),
    )
    mock_make_request.return_value = mock_response

    metric_id = UUID(mock_evaluation_data["metric_id"])
    evaluation = mandoline_client.create_evaluation(
        metric_id=metric_id,
        prompt=mock_evaluation_data["prompt"],
        response=mock_evaluation_data["response"],
        properties=mock_evaluation_data["properties"],
    )

    assert isinstance(evaluation, Evaluation)
    assert evaluation.prompt == mock_evaluation_data["prompt"]
    assert evaluation.response == mock_evaluation_data["response"]
    assert evaluation.properties == mock_evaluation_data["properties"]

    mock_make_request.assert_called_once()


def test_get_evaluation(mandoline_client):
    with patch(
        "mandoline.connection_manager.make_request_with_timeout"
    ) as mock_make_request:
        mock_response = httpx.Response(
            status_code=200,
            json={
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "metric_id": "234e5678-e89b-12d3-a456-426614174000",
                "prompt": "Test prompt",
                "response": "Test response",
                "properties": {"key": "value"},
                "score": 0.75,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
            },
            request=httpx.Request(
                "GET",
                "https://test.api.com/evaluations/123e4567-e89b-12d3-a456-426614174000",
            ),
        )
        mock_make_request.return_value = mock_response

        evaluation_id = UUID("123e4567-e89b-12d3-a456-426614174000")
        evaluation = mandoline_client.get_evaluation(evaluation_id=evaluation_id)

        assert evaluation.id == UUID("123e4567-e89b-12d3-a456-426614174000")
        assert evaluation.metric_id == UUID("234e5678-e89b-12d3-a456-426614174000")
        assert evaluation.score == 0.75


def test_get_evaluations(mandoline_client):
    with patch(
        "mandoline.connection_manager.make_request_with_timeout"
    ) as mock_make_request:
        mock_response = httpx.Response(
            status_code=200,
            json=[
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "metric_id": "234e5678-e89b-12d3-a456-426614174000",
                    "prompt": "Test prompt 1",
                    "response": "Test response 1",
                    "properties": {"key": "value1"},
                    "score": 0.75,
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                },
                {
                    "id": "223e4567-e89b-12d3-a456-426614174000",
                    "metric_id": "234e5678-e89b-12d3-a456-426614174000",
                    "prompt": "Test prompt 2",
                    "response": "Test response 2",
                    "properties": {"key": "value2"},
                    "score": 0.85,
                    "created_at": "2023-01-02T00:00:00Z",
                    "updated_at": "2023-01-02T00:00:00Z",
                },
            ],
            request=httpx.Request("GET", "https://test.api.com/evaluations/"),
        )
        mock_make_request.return_value = mock_response

        evaluations = mandoline_client.get_evaluations(
            skip=0, limit=10, metric_id=UUID("234e5678-e89b-12d3-a456-426614174000")
        )

        assert len(evaluations) == 2
        assert all(isinstance(eval, Evaluation) for eval in evaluations)
        assert evaluations[0].score == 0.75
        assert evaluations[1].score == 0.85


def test_update_evaluation(mandoline_client):
    with patch(
        "mandoline.connection_manager.make_request_with_timeout"
    ) as mock_make_request:
        mock_response = httpx.Response(
            status_code=200,
            json={
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "metric_id": "234e5678-e89b-12d3-a456-426614174000",
                "prompt": "Test prompt",
                "response": "Test response",
                "properties": {"key": "updated_value"},
                "score": 0.75,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-02T00:00:00Z",
            },
            request=httpx.Request(
                "PUT",
                "https://test.api.com/evaluations/123e4567-e89b-12d3-a456-426614174000",
            ),
        )
        mock_make_request.return_value = mock_response

        evaluation_id = UUID("123e4567-e89b-12d3-a456-426614174000")
        updated_evaluation = mandoline_client.update_evaluation(
            evaluation_id=evaluation_id, properties={"key": "updated_value"}
        )

        assert updated_evaluation.properties == {"key": "updated_value"}


def test_delete_evaluation(mandoline_client):
    with patch(
        "mandoline.connection_manager.make_request_with_timeout"
    ) as mock_make_request:
        mock_response = httpx.Response(
            status_code=204,
            request=httpx.Request(
                "DELETE",
                "https://test.api.com/evaluations/123e4567-e89b-12d3-a456-426614174000",
            ),
        )
        mock_make_request.return_value = mock_response

        evaluation_id = UUID("123e4567-e89b-12d3-a456-426614174000")
        mandoline_client.delete_evaluation(evaluation_id=evaluation_id)

        mock_make_request.assert_called_once()


def test_get_with_limit_exceeding_max(mandoline_client):
    with pytest.raises(ValueError):
        mandoline_client._get(endpoint="test_endpoint", params={"limit": 1000000})
