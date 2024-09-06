from typing import Any, Dict, Literal, Optional
from urllib.parse import urlencode

from httpx import Client, Response, Timeout
from pydantic import BaseModel

from mandoline.config import MandolineRequestConfig
from mandoline.errors import handle_error
from mandoline.logger import get_logger
from mandoline.types import Headers, SerializableDict
from mandoline.utils import make_serializable

logger = get_logger(__name__)


def process_url(
    *, api_base_url: str, endpoint: str, params: Optional[SerializableDict] = None
) -> str:
    if not params:
        return f"{api_base_url}/{endpoint}"

    serializable_params = make_serializable(data=params)
    query_string = urlencode(query=serializable_params, doseq=True)
    return f"{api_base_url}/{endpoint}?{query_string}"


def process_request_body(*, data: Optional[SerializableDict] = None) -> Dict[str, Any]:
    if not data:
        return {}

    serializable_data = make_serializable(data=data)
    return {"json": serializable_data}


def make_request_with_timeout(
    *,
    config: MandolineRequestConfig,
    method: str,
    url: str,
    headers: Dict[str, str],
    body: Dict[str, Any],
) -> Response:
    timeout = Timeout(
        connect=config.connect_timeout,
        read=config.rwp_timeout,
        write=config.rwp_timeout,
        pool=config.rwp_timeout,
    )
    with Client(timeout=timeout) as client:
        response = client.request(method=method, url=url, headers=headers, **body)
        return response


def process_response(*, response: Response) -> Any:
    response.raise_for_status()
    if response.status_code == 204:
        return None  # No content to process for 204 responses
    return response.json()


class RequestOptions(BaseModel):
    method: Literal["GET", "POST", "PUT", "DELETE"]
    endpoint: str
    auth_header: Headers
    params: Optional[SerializableDict] = None
    data: Optional[SerializableDict] = None


def make_request(*, config: MandolineRequestConfig, options: RequestOptions) -> Any:
    url = process_url(
        api_base_url=config.api_base_url,
        endpoint=options.endpoint,
        params=options.params,
    )
    headers = {**options.auth_header, "Content-Type": "application/json"}
    body = process_request_body(data=options.data)

    try:
        response = make_request_with_timeout(
            config=config,
            method=options.method,
            url=url,
            headers=headers,
            body=body,
        )
        return process_response(response=response)
    except Exception as error:
        raise handle_error(err=error)
