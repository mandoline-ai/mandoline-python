from datetime import datetime, timezone
from uuid import UUID

import pytest

from mandoline.models import EvaluationBase, Metric, MetricUpdate
from mandoline.types import NotGiven
from mandoline.utils import NOT_GIVEN

# Metric tests


def create_metric(tags):
    return Metric(
        id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        name="Test Metric",
        description="A test metric",
        tags=tags,
        created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
    )


def test_metric_with_not_given_tags():
    tags = NOT_GIVEN
    metric = create_metric(tags=tags)
    assert isinstance(metric.tags, NotGiven)
    serialized = metric.model_dump()
    assert "tags" not in serialized


def test_metric_with_null_tags():
    metric = create_metric(tags=None)
    assert metric.tags is None
    serialized = metric.model_dump()
    assert "tags" in serialized
    assert serialized["tags"] is None


def test_metric_with_string_list_tags():
    tags = ["tag1", "tag2"]
    metric = create_metric(tags=tags)
    assert metric.tags == tags
    serialized = metric.model_dump()
    assert "tags" in serialized
    assert serialized["tags"] == tags


# MetricUpdate tests


def test_metric_update_with_not_given():
    data = {"name": NOT_GIVEN, "description": "foo", "tags": None}
    metric_update = MetricUpdate.model_validate(obj=data, strict=True)
    assert isinstance(metric_update.name, NotGiven)
    assert metric_update.name == NOT_GIVEN
    assert metric_update.description == "foo"
    assert metric_update.tags is None


def test_metric_update_serialization():
    data = {"name": NOT_GIVEN, "description": "foo", "tags": None}
    metric_update = MetricUpdate.model_validate(obj=data, strict=True)
    serialized = metric_update.model_dump()
    assert "name" not in serialized
    assert serialized == {"description": "foo", "tags": None}


# NOT_GIVEN utility test


def test_not_given_behavior():
    assert bool(NOT_GIVEN) is False
    assert str(NOT_GIVEN) == "NOT_GIVEN"
    assert repr(NOT_GIVEN) == "NOT_GIVEN"


# EvaluationBase validation tests


def test_evaluation_base_invalid_no_response():
    with pytest.raises(
        ValueError, match="Either response or response_image must be provided"
    ):
        EvaluationBase(
            metric_id=UUID("123e4567-e89b-12d3-a456-426614174000"), prompt="Test prompt"
        )


def test_evaluation_base_invalid_image_format():
    with pytest.raises(ValueError, match="Image must start with data:image/"):
        EvaluationBase(
            metric_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            prompt="Test prompt",
            response="Test response",
            prompt_image="invalid_format",
        )


def test_evaluation_base_invalid_image_not_base64():
    with pytest.raises(ValueError, match="Image must be base64 encoded"):
        EvaluationBase(
            metric_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            prompt="Test prompt",
            response="Test response",
            prompt_image="data:image/png,not_base64",
        )


# EvaluationBase functionality tests


def test_evaluation_base_mixed_response():
    eval = EvaluationBase(
        metric_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        prompt="Test prompt",
        response="Test response",
        prompt_image="data:image/png;base64,abc123",
    )
    assert eval.response == "Test response"
    assert eval.prompt_image == "data:image/png;base64,abc123"


def test_evaluation_base_valid_both_image_types():
    eval = EvaluationBase(
        metric_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        prompt="Test prompt",
        prompt_image="data:image/png;base64,abc123",
        response_image="data:image/jpeg;base64,def456",
    )
    assert eval.prompt_image == "data:image/png;base64,abc123"
    assert eval.response_image == "data:image/jpeg;base64,def456"


def test_evaluation_base_serialization():
    eval = EvaluationBase(
        metric_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        prompt="Test prompt",
        response="Test response",
        properties={"key": "value"},
    )
    serialized = eval.model_dump()
    assert serialized["prompt"] == "Test prompt"
    assert serialized["response"] == "Test response"
    assert serialized["properties"] == {"key": "value"}
