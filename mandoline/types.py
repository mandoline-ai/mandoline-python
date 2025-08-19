from typing import Any, Literal

from pydantic import BaseModel, model_serializer

Headers = dict[str, str]


class NotGiven(BaseModel):
    """Distinguish between 'not provided' and 'explicitly set to None'"""

    def __bool__(self) -> Literal[False]:
        return False

    def __repr__(self) -> str:
        return "NOT_GIVEN"

    def __str__(self) -> str:
        return "NOT_GIVEN"

    @model_serializer
    def serialize(self) -> str:
        return str(self)


SerializableDict = dict[str, Any]
NullableSerializableDict = SerializableDict | None

StringArray = list[str]
NullableStringArray = StringArray | None
