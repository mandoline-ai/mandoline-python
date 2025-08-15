import asyncio
from typing import Any, Dict, List

from httpx import AsyncClient, Response, Timeout

from mandoline.config import MandolineRequestConfig
from mandoline.connection_manager import (
    RequestOptions,
    process_request_body,
    process_response,
    process_url,
)
from mandoline.errors import handle_error
from mandoline.logger import get_logger

logger = get_logger(__name__)


async def make_async_request_with_timeout(
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
    async with AsyncClient(timeout=timeout) as client:
        response = await client.request(method=method, url=url, headers=headers, **body)
        return response


async def make_async_request(
    *, config: MandolineRequestConfig, options: RequestOptions
) -> Any:
    url = process_url(
        api_base_url=config.api_base_url,
        endpoint=options.endpoint,
        params=options.params,
    )
    headers = {**options.auth_header, "Content-Type": "application/json"}
    body = process_request_body(data=options.data)

    try:
        response = await make_async_request_with_timeout(
            config=config,
            method=options.method,
            url=url,
            headers=headers,
            body=body,
        )
        return process_response(response=response)
    except Exception as error:
        raise handle_error(err=error)


async def make_concurrent_requests(
    *,
    config: MandolineRequestConfig,
    requests: List[RequestOptions],
) -> List[Any]:
    """Make multiple requests concurrently."""
    tasks = [
        make_async_request(config=config, options=request_options)
        for request_options in requests
    ]
    return await asyncio.gather(*tasks)
