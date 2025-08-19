from datetime import datetime
from typing import Any, Dict, Union
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
    model_config = dict(extra="forbid", arbitrary_types_allowed=True)

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
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
    tags: Union[NullableStringArray, NotGiven] = Field(
        default_factory=lambda: NOT_GIVEN
    )


class MetricCreate(MetricBase):
    pass


class MetricUpdate(MandolineBase, AtLeastOneFieldGivenMixin):
    name: Union[str, NotGiven] = Field(default_factory=lambda: NOT_GIVEN)
    description: Union[str, NotGiven] = Field(default_factory=lambda: NOT_GIVEN)
    tags: Union[NullableStringArray, NotGiven] = Field(
        default_factory=lambda: NOT_GIVEN
    )


class Metric(MetricBase, IDAndTimestampsMixin):
    pass


class EvaluationBase(MandolineBase):
    metric_id: UUID
    prompt: Union[str, None, NotGiven] = Field(default_factory=lambda: NOT_GIVEN)
    prompt_image: Union[str, None, NotGiven] = Field(default_factory=lambda: NOT_GIVEN)
    response: Union[str, None, NotGiven] = Field(default_factory=lambda: NOT_GIVEN)
    response_image: Union[str, None, NotGiven] = Field(
        default_factory=lambda: NOT_GIVEN
    )
    properties: Union[NullableSerializableDict, NotGiven] = Field(
        default_factory=lambda: NOT_GIVEN
    )


class EvaluationCreate(EvaluationBase):
    @model_validator(mode="before")
    def validate_response_fields(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        prompt_image = values.get("prompt_image")
        response = values.get("response")
        response_image = values.get("response_image")

        # Validate response requirements
        if response is None and response_image is None:
            raise ValueError("Either response or response_image must be provided")

        # Ensure response is None only with images
        if response is None and not (prompt_image or response_image):
            raise ValueError("Response can only be None when images are provided")

        # Must be a data URI of the form: f"data:image/{media_type};base64,{base64_encoded_data}"
        for img in (prompt_image, response_image):
            if img is not None:
                if not isinstance(img, str):
                    raise ValueError("Image must be a string")
                if not img.startswith("data:image/"):
                    raise ValueError("Image must start with data:image/")
                if ";base64," not in img:
                    raise ValueError("Image must be base64 encoded")

        return values


class EvaluationUpdate(MandolineBase, AtLeastOneFieldGivenMixin):
    properties: Union[NullableSerializableDict, NotGiven] = Field(
        default_factory=lambda: NOT_GIVEN
    )


class Evaluation(EvaluationBase, IDAndTimestampsMixin):
    score: float
