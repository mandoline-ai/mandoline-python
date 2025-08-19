import os
from typing import Any
from uuid import UUID

from mandoline.async_connection_manager import (
    make_async_request,
    make_concurrent_requests,
)
from mandoline.config import DEFAULT_GET_LIMIT, MAX_GET_LIMIT, MandolineRequestConfig
from mandoline.connection_manager import RequestOptions
from mandoline.models import (
    Evaluation,
    EvaluationCreate,
    EvaluationUpdate,
    Metric,
    MetricCreate,
    MetricUpdate,
)
from mandoline.types import (
    Headers,
    NotGiven,
    NullableSerializableDict,
    NullableStringArray,
    SerializableDict,
)
from mandoline.utils import NOT_GIVEN, process_get_options


class AsyncMandoline:
    """
    Async Mandoline client for interacting with the Mandoline API.

    This class provides async methods to create, retrieve, update, and delete
    metrics and evaluations with true concurrent batch operations.

    Can be used as an async context manager:
        async with AsyncMandoline() as client:
            metrics = await client.get_metrics()
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        api_base_url: str | None = None,
        connect_timeout: float | None = None,
        rwp_timeout: float | None = None,
    ):
        """Creates a new AsyncMandoline client instance."""
        self.api_key = api_key or os.environ.get("MANDOLINE_API_KEY")

        config_dict = {
            "api_base_url": api_base_url or os.environ.get("MANDOLINE_API_BASE_URL"),
            "connect_timeout": connect_timeout,
            "rwp_timeout": rwp_timeout,
        }
        # Remove None values – Pydantic will use default values
        config_dict = {k: v for k, v in config_dict.items() if v is not None}

        self.request_config = MandolineRequestConfig.model_validate(
            obj=config_dict, strict=True
        )

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # Currently no cleanup needed as AsyncClient is created per request
        pass

    def _get_auth_header(self) -> Headers:
        if not self.api_key:
            raise ValueError(
                "Mandoline API key required. Set MANDOLINE_API_KEY environment "
                "variable or create one at https://mandoline.ai/account"
            )
        return {"X-API-KEY": self.api_key}

    async def _get(
        self, *, endpoint: str, params: SerializableDict | None = None
    ) -> Any:
        if params and params.get("limit") and params["limit"] > MAX_GET_LIMIT:
            raise ValueError(
                f"Limit exceeds maximum allowed value of {MAX_GET_LIMIT}. "
                "Please reduce the limit."
            )
        return await make_async_request(
            config=self.request_config,
            options=RequestOptions(
                method="GET",
                endpoint=endpoint,
                auth_header=self._get_auth_header(),
                params=params,
            ),
        )

    async def _post(
        self,
        *,
        endpoint: str,
        data: SerializableDict,
        params: SerializableDict | None = None,
    ) -> Any:
        return await make_async_request(
            config=self.request_config,
            options=RequestOptions(
                method="POST",
                endpoint=endpoint,
                auth_header=self._get_auth_header(),
                data=data,
                params=params,
            ),
        )

    async def _put(self, *, endpoint: str, data: SerializableDict) -> Any:
        return await make_async_request(
            config=self.request_config,
            options=RequestOptions(
                method="PUT",
                endpoint=endpoint,
                auth_header=self._get_auth_header(),
                data=data,
            ),
        )

    async def _delete(self, *, endpoint: str) -> Any:
        return await make_async_request(
            config=self.request_config,
            options=RequestOptions(
                method="DELETE",
                endpoint=endpoint,
                auth_header=self._get_auth_header(),
            ),
        )

    # Metric methods
    async def create_metric(
        self,
        *,
        name: str,
        description: str,
        tags: NullableStringArray | NotGiven = NOT_GIVEN,
    ) -> Metric:
        """Adds a new evaluation metric."""
        metric_create = MetricCreate(name=name, description=description, tags=tags)

        data = await self._post(endpoint="metrics/", data=metric_create.model_dump())
        return Metric.model_validate(data)

    async def batch_create_metrics(
        self,
        *,
        metrics: list[MetricCreate],
    ) -> list[Metric]:
        """Creates multiple metrics concurrently."""
        requests = [
            RequestOptions(
                method="POST",
                endpoint="metrics/",
                auth_header=self._get_auth_header(),
                data=metric.model_dump(),
            )
            for metric in metrics
        ]

        results = await make_concurrent_requests(
            config=self.request_config,
            requests=requests,
        )

        return [Metric.model_validate(result) for result in results]

    async def get_metric(self, *, metric_id: UUID) -> Metric:
        """Fetches a specific metric by its unique identifier."""
        data = await self._get(endpoint=f"metrics/{metric_id}")
        return Metric.model_validate(data)

    async def get_metrics(
        self,
        *,
        skip: int = 0,
        limit: int = DEFAULT_GET_LIMIT,
        tags: NullableStringArray | NotGiven = NOT_GIVEN,
        filters: SerializableDict | NotGiven = NOT_GIVEN,
    ) -> list[Metric]:
        """Retrieve a list of metrics with optional filtering."""
        params = process_get_options(skip=skip, limit=limit, tags=tags, filters=filters)
        data = await self._get(endpoint="metrics/", params=params)
        return [Metric.model_validate(metric_data) for metric_data in data]

    async def update_metric(
        self,
        *,
        metric_id: UUID,
        name: str | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        tags: NullableStringArray | NotGiven = NOT_GIVEN,
    ) -> Metric:
        """Modifies an existing metric's attributes."""
        metric_update = MetricUpdate(
            name=name,
            description=description,
            tags=tags,
        )

        data = await self._put(
            endpoint=f"metrics/{metric_id}", data=metric_update.model_dump()
        )
        return Metric.model_validate(data)

    async def delete_metric(self, *, metric_id: UUID) -> None:
        """Removes a metric permanently."""
        await self._delete(endpoint=f"metrics/{metric_id}")

    # Evaluation methods
    async def create_evaluation(
        self,
        *,
        metric_id: UUID,
        prompt: str,
        prompt_image: str | None = None,
        response: str | None = None,
        response_image: str | None = None,
        properties: NullableSerializableDict | NotGiven = NOT_GIVEN,
        include_content: bool = True,
    ) -> Evaluation:
        """Performs an evaluation for a single metric on a prompt-response pair."""
        evaluation_create = EvaluationCreate(
            metric_id=metric_id,
            prompt=prompt,
            prompt_image=prompt_image,
            response=response,
            response_image=response_image,
            properties=properties,
        )

        params = {"include_content": include_content}
        data = await self._post(
            endpoint="evaluations/", data=evaluation_create.model_dump(), params=params
        )
        return Evaluation.model_validate(data)

    async def batch_create_evaluations(
        self,
        *,
        evaluations: list[EvaluationCreate],
        include_content: bool = True,
    ) -> list[Evaluation]:
        """Creates multiple evaluations concurrently."""
        params = {"include_content": include_content}
        requests = [
            RequestOptions(
                method="POST",
                endpoint="evaluations/",
                auth_header=self._get_auth_header(),
                data=evaluation.model_dump(),
                params=params,
            )
            for evaluation in evaluations
        ]

        results = await make_concurrent_requests(
            config=self.request_config,
            requests=requests,
        )

        return [Evaluation.model_validate(result) for result in results]

    async def batch_create_evaluations_for_metrics(
        self,
        *,
        metric_ids: list[UUID],
        prompt: str,
        prompt_image: str | None = None,
        response: str | None = None,
        response_image: str | None = None,
        properties: NullableSerializableDict | NotGiven = NOT_GIVEN,
        include_content: bool = True,
    ) -> list[Evaluation]:
        """
        Creates evaluations across multiple metrics concurrently for a single
        prompt-response pair.
        """
        evaluations = [
            EvaluationCreate(
                metric_id=metric_id,
                prompt=prompt,
                prompt_image=prompt_image,
                response=response,
                response_image=response_image,
                properties=properties,
            )
            for metric_id in metric_ids
        ]

        return await self.batch_create_evaluations(
            evaluations=evaluations, include_content=include_content
        )

    async def get_evaluation(
        self, *, evaluation_id: UUID, include_content: bool = True
    ) -> Evaluation:
        """Fetches details of a specific evaluation."""
        params = {"include_content": include_content}
        data = await self._get(endpoint=f"evaluations/{evaluation_id}", params=params)
        return Evaluation.model_validate(data)

    async def get_evaluations(
        self,
        *,
        skip: int = 0,
        limit: int = DEFAULT_GET_LIMIT,
        metric_id: UUID | NotGiven = NOT_GIVEN,
        include_content: bool | NotGiven = NOT_GIVEN,
        properties: NullableSerializableDict | NotGiven = NOT_GIVEN,
        filters: SerializableDict | NotGiven = NOT_GIVEN,
    ) -> list[Evaluation]:
        """Retrieve a list of evaluations with optional filtering."""
        params = process_get_options(
            skip=skip,
            limit=limit,
            metric_id=metric_id,
            include_content=include_content,
            properties=properties,
            filters=filters,
        )
        data = await self._get(endpoint="evaluations/", params=params)
        return [Evaluation.model_validate(evaluation_data) for evaluation_data in data]

    async def update_evaluation(
        self,
        *,
        evaluation_id: UUID,
        properties: NullableSerializableDict | NotGiven = NOT_GIVEN,
    ) -> Evaluation:
        """Modifies an existing evaluation's properties."""
        evaluation_update = EvaluationUpdate(properties=properties)

        data = await self._put(
            endpoint=f"evaluations/{evaluation_id}", data=evaluation_update.model_dump()
        )
        return Evaluation.model_validate(data)

    async def delete_evaluation(self, *, evaluation_id: UUID) -> None:
        """Removes an evaluation permanently."""
        await self._delete(endpoint=f"evaluations/{evaluation_id}")
