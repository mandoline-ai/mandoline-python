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
    prompt: str
    response: str
    properties: Union[NullableSerializableDict, NotGiven] = Field(
        default_factory=lambda: NOT_GIVEN
    )


class EvaluationCreate(EvaluationBase):
    pass


class EvaluationUpdate(MandolineBase, AtLeastOneFieldGivenMixin):
    properties: Union[NullableSerializableDict, NotGiven] = Field(
        default_factory=lambda: NOT_GIVEN
    )


class Evaluation(EvaluationBase, IDAndTimestampsMixin):
    score: float
