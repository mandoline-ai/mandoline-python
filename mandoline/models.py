from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from mandoline.types import (
    NotGiven,
    NullableSerializableDict,
    NullableStringArray,
    SerializableDict,
)
from mandoline.utils import NOT_GIVEN


class MandolineBase(BaseModel):
    model_config = {"extra": "forbid", "arbitrary_types_allowed": True}

    def model_dump(self, *args, **kwargs) -> dict[str, Any]:
        """Omit fields with a value of NotGiven"""
        dump = super().model_dump(*args, **kwargs)
        return {k: v for k, v in dump.items() if v != str(NOT_GIVEN)}


class AtLeastOneFieldGivenMixin:
    """Prevents unneeded update requests"""

    @model_validator(mode="before")
    def check_at_least_one_field_given(
        cls, values: SerializableDict
    ) -> SerializableDict:
        given_fields = [
            field for field, value in values.items() if not isinstance(value, NotGiven)
        ]
        if not given_fields:
            raise ValueError("At least one field must be provided")
        return values


class IDAndTimestampsMixin(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime


class MetricBase(MandolineBase):
    name: str
    description: str
    tags: NullableStringArray | NotGiven = Field(default_factory=lambda: NOT_GIVEN)


class MetricCreate(MetricBase):
    pass


class MetricUpdate(MandolineBase, AtLeastOneFieldGivenMixin):
    name: str | NotGiven = Field(default_factory=lambda: NOT_GIVEN)
    description: str | NotGiven = Field(default_factory=lambda: NOT_GIVEN)
    tags: NullableStringArray | NotGiven = Field(default_factory=lambda: NOT_GIVEN)


class Metric(MetricBase, IDAndTimestampsMixin):
    pass


class EvaluationBase(MandolineBase):
    metric_id: UUID
    prompt: str | None | NotGiven = Field(default_factory=lambda: NOT_GIVEN)
    prompt_image: str | None | NotGiven = Field(default_factory=lambda: NOT_GIVEN)
    response: str | None | NotGiven = Field(default_factory=lambda: NOT_GIVEN)
    response_image: str | None | NotGiven = Field(default_factory=lambda: NOT_GIVEN)
    properties: NullableSerializableDict | NotGiven = Field(
        default_factory=lambda: NOT_GIVEN
    )


def validate_evaluation_fields(values: dict[str, Any]) -> dict[str, Any]:
    """Validate evaluation fields according to the rules:
    - Either prompt or prompt_image must be provided
    - Either response or response_image must be provided
    - Images must be valid data URIs
    """
    prompt = values.get("prompt")
    prompt_image = values.get("prompt_image")
    response = values.get("response")
    response_image = values.get("response_image")

    # Check prompt requirements
    if prompt is None and prompt_image is None:
        raise ValueError("Either prompt or prompt_image must be provided")

    # Check response requirements
    if response is None and response_image is None:
        raise ValueError("Either response or response_image must be provided")

    # Validate image data URI format
    for field_name, img in [
        ("prompt_image", prompt_image),
        ("response_image", response_image),
    ]:
        if img is not None:
            if not isinstance(img, str):
                raise ValueError(f"{field_name} must be a string")
            if not img.startswith("data:image/"):
                raise ValueError(f"{field_name} must start with data:image/")
            if ";base64," not in img:
                raise ValueError(f"{field_name} must be base64 encoded")

    return values


class EvaluationCreate(EvaluationBase):
    @model_validator(mode="before")
    def validate_response_fields(cls, values: dict[str, Any]) -> dict[str, Any]:
        return validate_evaluation_fields(values)


class EvaluationUpdate(MandolineBase, AtLeastOneFieldGivenMixin):
    properties: NullableSerializableDict | NotGiven = Field(
        default_factory=lambda: NOT_GIVEN
    )


class Evaluation(EvaluationBase, IDAndTimestampsMixin):
    score: float
