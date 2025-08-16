from unittest.mock import patch
from uuid import UUID

import httpx
import pytest

from mandoline import AsyncMandoline
from mandoline.config import CONNECT_TIMEOUT, MANDOLINE_API_BASE_URL, RWP_TIMEOUT
from mandoline.models import Evaluation, EvaluationCreate, Metric, MetricCreate


@pytest.fixture
def api_key():
    return "test_api_key"


@pytest.fixture
def api_base_url():
    return "https://test.api.com"


@pytest.fixture
def async_mandoline_client(api_key):
    return AsyncMandoline(api_key=api_key)


@pytest.fixture
def async_mandoline_client_custom(api_key, api_base_url):
    return AsyncMandoline(api_key=api_key, api_base_url=api_base_url)


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


def test_async_mandoline_client_initialization(
    async_mandoline_client_custom, api_key, api_base_url
):
    assert async_mandoline_client_custom.api_key == api_key
    assert async_mandoline_client_custom.request_config.api_base_url == api_base_url


def test_async_mandoline_client_default_config(async_mandoline_client):
    assert async_mandoline_client.request_config.api_base_url == MANDOLINE_API_BASE_URL
    assert async_mandoline_client.request_config.connect_timeout == CONNECT_TIMEOUT
    assert async_mandoline_client.request_config.rwp_timeout == RWP_TIMEOUT


def test_async_mandoline_client_initialization_with_env_vars(monkeypatch):
    env_api_key = "env_test_api_key"
    env_api_base_url = "https://env.test.api.com"
    monkeypatch.setenv("MANDOLINE_API_KEY", env_api_key)
    monkeypatch.setenv("MANDOLINE_API_BASE_URL", env_api_base_url)

    client = AsyncMandoline()
    assert client.api_key == env_api_key
    assert client.request_config.api_base_url == env_api_base_url


def test_get_auth_header(async_mandoline_client, api_key):
    auth_header = async_mandoline_client._get_auth_header()
    assert auth_header == {"X-API-KEY": api_key}


def test_get_auth_header_no_api_key():
    client = AsyncMandoline(api_key="")
    with pytest.raises(ValueError):
        client._get_auth_header()


@pytest.mark.asyncio
@patch("mandoline.async_connection_manager.make_async_request_with_timeout")
async def test_create_metric(
    mock_make_request, async_mandoline_client, mock_httpx_response, mock_metric_data
):
    mock_make_request.return_value = mock_httpx_response

    metric = await async_mandoline_client.create_metric(
        name="Test Metric", description="A test metric", tags=["test"]
    )

    assert isinstance(metric, Metric)
    assert metric.name == mock_metric_data["name"]
    assert metric.description == mock_metric_data["description"]
    assert metric.tags == mock_metric_data["tags"]

    mock_make_request.assert_called_once()


@pytest.mark.asyncio
@patch("mandoline.async_connection_manager.make_async_request_with_timeout")
async def test_get_metric(
    mock_make_request, async_mandoline_client, mock_httpx_response, mock_metric_data
):
    mock_make_request.return_value = mock_httpx_response

    metric_id = UUID(mock_metric_data["id"])
    metric = await async_mandoline_client.get_metric(metric_id=metric_id)

    assert isinstance(metric, Metric)
    assert metric.id == metric_id

    mock_make_request.assert_called_once()


@pytest.mark.asyncio
@patch("mandoline.async_connection_manager.make_async_request_with_timeout")
async def test_get_metrics(mock_make_request, async_mandoline_client):
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

    metrics = await async_mandoline_client.get_metrics(skip=0, limit=10, tags=["test"])

    assert len(metrics) == 2
    assert all(isinstance(metric, Metric) for metric in metrics)

    mock_make_request.assert_called_once()


@pytest.mark.asyncio
async def test_update_metric(async_mandoline_client):
    with patch(
        "mandoline.async_connection_manager.make_async_request_with_timeout"
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
        updated_metric = await async_mandoline_client.update_metric(
            metric_id=metric_id,
            name="Updated Metric",
            description="An updated test metric",
            tags=["test", "updated"],
        )

        assert updated_metric.name == "Updated Metric"
        assert updated_metric.description == "An updated test metric"
        assert updated_metric.tags == ["test", "updated"]


@pytest.mark.asyncio
async def test_delete_metric(async_mandoline_client):
    with patch(
        "mandoline.async_connection_manager.make_async_request_with_timeout"
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
        await async_mandoline_client.delete_metric(metric_id=metric_id)

        mock_make_request.assert_called_once()


@pytest.mark.asyncio
async def test_batch_create_metrics(async_mandoline_client):
    with patch(
        "mandoline.async_connection_manager.make_async_request_with_timeout"
    ) as mock_make_request:
        mock_responses = [
            httpx.Response(
                status_code=200,
                json={
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "Test Metric 1",
                    "description": "A test metric",
                    "tags": ["test"],
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                },
                request=httpx.Request("POST", "https://test.api.com/metrics/"),
            ),
            httpx.Response(
                status_code=200,
                json={
                    "id": "223e4567-e89b-12d3-a456-426614174001",
                    "name": "Test Metric 2",
                    "description": "Another test metric",
                    "tags": ["test", "batch"],
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                },
                request=httpx.Request("POST", "https://test.api.com/metrics/"),
            ),
        ]
        mock_make_request.side_effect = mock_responses

        metrics_to_create = [
            MetricCreate(name="Test Metric 1", description="A test metric", tags=["test"]),
            MetricCreate(
                name="Test Metric 2",
                description="Another test metric",
                tags=["test", "batch"],
            ),
        ]

        metrics = await async_mandoline_client.batch_create_metrics(metrics=metrics_to_create)

        assert len(metrics) == 2
        assert all(isinstance(metric, Metric) for metric in metrics)
        assert metrics[0].name == "Test Metric 1"
        assert metrics[1].name == "Test Metric 2"

        assert mock_make_request.call_count == 2


@pytest.mark.asyncio
@patch("mandoline.async_connection_manager.make_async_request_with_timeout")
async def test_create_evaluation(mock_make_request, async_mandoline_client, mock_evaluation_data):
    mock_response = httpx.Response(
        status_code=200,
        json=mock_evaluation_data,
        request=httpx.Request("POST", "https://test.api.com/evaluations/"),
    )
    mock_make_request.return_value = mock_response

    metric_id = UUID(mock_evaluation_data["metric_id"])
    evaluation = await async_mandoline_client.create_evaluation(
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


@pytest.mark.asyncio
async def test_batch_create_evaluations(async_mandoline_client):
    with patch(
        "mandoline.async_connection_manager.make_async_request_with_timeout"
    ) as mock_make_request:
        mock_responses = [
            httpx.Response(
                status_code=200,
                json={
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "metric_id": "234e5678-e89b-12d3-a456-426614174000",
                    "prompt": "Test prompt 1",
                    "response": "Test response 1",
                    "properties": {"key": "value1"},
                    "score": 0.85,
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                },
                request=httpx.Request("POST", "https://test.api.com/evaluations/"),
            ),
            httpx.Response(
                status_code=200,
                json={
                    "id": "223e4567-e89b-12d3-a456-426614174001",
                    "metric_id": "334e5678-e89b-12d3-a456-426614174001",
                    "prompt": "Test prompt 2",
                    "response": "Test response 2",
                    "properties": {"key": "value2"},
                    "score": 0.92,
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                },
                request=httpx.Request("POST", "https://test.api.com/evaluations/"),
            ),
        ]
        mock_make_request.side_effect = mock_responses

        evaluations_to_create = [
            EvaluationCreate(
                metric_id=UUID("234e5678-e89b-12d3-a456-426614174000"),
                prompt="Test prompt 1",
                response="Test response 1",
                properties={"key": "value1"},
            ),
            EvaluationCreate(
                metric_id=UUID("334e5678-e89b-12d3-a456-426614174001"),
                prompt="Test prompt 2",
                response="Test response 2",
                properties={"key": "value2"},
            ),
        ]

        evaluations = await async_mandoline_client.batch_create_evaluations(
            evaluations=evaluations_to_create
        )

        assert len(evaluations) == 2
        assert all(isinstance(evaluation, Evaluation) for evaluation in evaluations)
        assert evaluations[0].prompt == "Test prompt 1"
        assert evaluations[1].prompt == "Test prompt 2"

        assert mock_make_request.call_count == 2


@pytest.mark.asyncio
async def test_batch_create_evaluations_for_metrics(async_mandoline_client):
    with patch(
        "mandoline.async_connection_manager.make_async_request_with_timeout"
    ) as mock_make_request:
        mock_responses = [
            httpx.Response(
                status_code=200,
                json={
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "metric_id": "234e5678-e89b-12d3-a456-426614174000",
                    "prompt": "Test prompt",
                    "response": "Test response",
                    "properties": {"key": "value"},
                    "score": 0.85,
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                },
                request=httpx.Request("POST", "https://test.api.com/evaluations/"),
            ),
            httpx.Response(
                status_code=200,
                json={
                    "id": "223e4567-e89b-12d3-a456-426614174001",
                    "metric_id": "334e5678-e89b-12d3-a456-426614174001",
                    "prompt": "Test prompt",
                    "response": "Test response",
                    "properties": {"key": "value"},
                    "score": 0.92,
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                },
                request=httpx.Request("POST", "https://test.api.com/evaluations/"),
            ),
        ]
        mock_make_request.side_effect = mock_responses

        metric_ids = [
            UUID("234e5678-e89b-12d3-a456-426614174000"),
            UUID("334e5678-e89b-12d3-a456-426614174001"),
        ]

        evaluations = await async_mandoline_client.batch_create_evaluations_for_metrics(
            metric_ids=metric_ids,
            prompt="Test prompt",
            response="Test response",
            properties={"key": "value"},
        )

        assert len(evaluations) == 2
        assert all(isinstance(evaluation, Evaluation) for evaluation in evaluations)
        assert all(evaluation.prompt == "Test prompt" for evaluation in evaluations)
        assert all(evaluation.response == "Test response" for evaluation in evaluations)

        assert mock_make_request.call_count == 2


@pytest.mark.asyncio
async def test_get_evaluation(async_mandoline_client):
    with patch(
        "mandoline.async_connection_manager.make_async_request_with_timeout"
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
        evaluation = await async_mandoline_client.get_evaluation(evaluation_id=evaluation_id)

        assert evaluation.id == UUID("123e4567-e89b-12d3-a456-426614174000")
        assert evaluation.metric_id == UUID("234e5678-e89b-12d3-a456-426614174000")
        assert evaluation.score == 0.75


@pytest.mark.asyncio
async def test_get_evaluations(async_mandoline_client):
    with patch(
        "mandoline.async_connection_manager.make_async_request_with_timeout"
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

        evaluations = await async_mandoline_client.get_evaluations(
            skip=0, limit=10, metric_id=UUID("234e5678-e89b-12d3-a456-426614174000")
        )

        assert len(evaluations) == 2
        assert all(isinstance(eval, Evaluation) for eval in evaluations)
        assert evaluations[0].score == 0.75
        assert evaluations[1].score == 0.85


@pytest.mark.asyncio
async def test_update_evaluation(async_mandoline_client):
    with patch(
        "mandoline.async_connection_manager.make_async_request_with_timeout"
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
        updated_evaluation = await async_mandoline_client.update_evaluation(
            evaluation_id=evaluation_id, properties={"key": "updated_value"}
        )

        assert updated_evaluation.properties == {"key": "updated_value"}


@pytest.mark.asyncio
async def test_delete_evaluation(async_mandoline_client):
    with patch(
        "mandoline.async_connection_manager.make_async_request_with_timeout"
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
        await async_mandoline_client.delete_evaluation(evaluation_id=evaluation_id)

        mock_make_request.assert_called_once()


@pytest.mark.asyncio
async def test_get_with_limit_exceeding_max(async_mandoline_client):
    with pytest.raises(ValueError):
        await async_mandoline_client._get(endpoint="test_endpoint", params={"limit": 1000000})


@pytest.mark.asyncio
async def test_async_context_manager():
    """Test that AsyncMandoline can be used as an async context manager."""
    async with AsyncMandoline(api_key="test_key") as client:
        assert isinstance(client, AsyncMandoline)
        assert client.api_key == "test_key"


@pytest.mark.asyncio
async def test_async_context_manager_with_api_call():
    """Test async context manager with actual API call (mocked)."""
    with patch(
        "mandoline.async_connection_manager.make_async_request_with_timeout"
    ) as mock_make_request:
        mock_response = httpx.Response(
            status_code=200,
            json=[],
            request=httpx.Request("GET", "https://test.api.com/metrics/"),
        )
        mock_make_request.return_value = mock_response

        async with AsyncMandoline(api_key="test_key") as client:
            metrics = await client.get_metrics()
            assert isinstance(metrics, list)

        mock_make_request.assert_called_once()


@pytest.mark.asyncio
async def test_async_context_manager_backwards_compatibility():
    """Test that direct instantiation still works alongside context manager."""
    # Direct instantiation (original way)
    client = AsyncMandoline(api_key="test_key")
    assert isinstance(client, AsyncMandoline)
    assert client.api_key == "test_key"

    # Context manager (new way)
    async with AsyncMandoline(api_key="test_key") as context_client:
        assert isinstance(context_client, AsyncMandoline)
        assert context_client.api_key == "test_key"

    # Both should work the same way
    assert type(client) == type(context_client)