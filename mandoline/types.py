from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, model_serializer

Headers = Dict[str, str]


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


SerializableDict = Dict[str, Any]
NullableSerializableDict = Optional[SerializableDict]

StringArray = List[str]
NullableStringArray = Optional[StringArray]
