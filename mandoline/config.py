from typing import Final

from pydantic import BaseModel, Field

MANDOLINE_API_BASE_URL: Final[str] = "https://mandoline-api.fly.dev/v1"

DEFAULT_GET_LIMIT: Final[int] = 100
MAX_GET_LIMIT: Final[int] = 1000

CONNECT_TIMEOUT: Final[float] = 10.0
RWP_TIMEOUT: Final[float] = 300.0

DEFAULT_INCLUDE_EVALUATION_CONTENT: bool = True


class MandolineRequestConfig(BaseModel):
    """Configuration for Mandoline API requests."""

    api_base_url: str = Field(
        default=MANDOLINE_API_BASE_URL,
        description="The base URL for the Mandoline API.",
    )
    connect_timeout: float = Field(
        default=CONNECT_TIMEOUT,
        description="The timeout (in seconds) for establishing a connection to the API.",
    )
    rwp_timeout: float = Field(
        default=RWP_TIMEOUT,
        description="The timeout (in seconds) for the entire request-response cycle.",
    )


class MandolineClientOptions(MandolineRequestConfig):
    """Options for initializing the Mandoline client."""

    api_key: str | None = Field(
        default=None,
        description="The API key for authenticating with the Mandoline API.",
    )
