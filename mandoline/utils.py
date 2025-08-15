import json
from typing import Any, Dict, Optional, Union
from uuid import UUID

from mandoline.config import DEFAULT_INCLUDE_EVALUATION_CONTENT
from mandoline.types import (
    NotGiven,
    NullableSerializableDict,
    NullableStringArray,
    SerializableDict,
)

NOT_GIVEN = NotGiven()  # singleton


def make_serializable(*, data: dict) -> SerializableDict:
    serializable_data = {}
    for k, v in data.items():
        if isinstance(v, NotGiven):
            continue
        elif isinstance(v, UUID):
            serializable_data[k] = str(v)
        else:
            serializable_data[k] = v
    return serializable_data


def safe_json_parse(*, json_string: str) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(json_string)
    except:
        return None


def process_get_options(
    *,
    skip: int,
    limit: int,
    tags: Union[NullableStringArray, NotGiven] = NOT_GIVEN,
    metric_id: Union[UUID, NotGiven] = NOT_GIVEN,
    include_content: Union[bool, NotGiven] = NOT_GIVEN,
    properties: Union[NullableSerializableDict, NotGiven] = NOT_GIVEN,
    filters: Union[SerializableDict, NotGiven] = NOT_GIVEN,
) -> SerializableDict:
    """Helper function for processing get options for both sync and async clients."""
    params: SerializableDict = {"skip": skip, "limit": limit}

    if include_content == (not DEFAULT_INCLUDE_EVALUATION_CONTENT):
        params["include_content"] = include_content

    _filters: SerializableDict = {}

    if tags != NOT_GIVEN:
        _filters["tags"] = tags

    if metric_id != NOT_GIVEN:
        _filters["metric_id"] = str(metric_id)

    if properties != NOT_GIVEN:
        _filters["properties"] = properties

    if filters != NOT_GIVEN:
        if not isinstance(filters, dict):
            raise ValueError("filters must be a dictionary")
        _filters.update(filters)

    if _filters:
        params["filters"] = json.dumps(_filters)

    return params
