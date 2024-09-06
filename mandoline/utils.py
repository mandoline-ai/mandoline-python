import json
from typing import Any, Dict, Optional
from uuid import UUID

from mandoline.types import NotGiven, SerializableDict

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
