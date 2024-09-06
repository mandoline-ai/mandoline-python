from datetime import datetime, timezone
from uuid import UUID

from mandoline.models import Metric, MetricUpdate
from mandoline.types import NotGiven
from mandoline.utils import NOT_GIVEN


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


def test_not_given_behavior():
    assert bool(NOT_GIVEN) is False
    assert str(NOT_GIVEN) == "NOT_GIVEN"
    assert repr(NOT_GIVEN) == "NOT_GIVEN"
