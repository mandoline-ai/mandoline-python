import os
from typing import Any
from uuid import UUID

from mandoline.config import DEFAULT_GET_LIMIT, MAX_GET_LIMIT, MandolineRequestConfig
from mandoline.connection_manager import RequestOptions, make_request
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


class Mandoline:
    """
    Mandoline client for interacting with the Mandoline API.

    This class provides methods to create, retrieve, update, and delete
    metrics and evaluations. It handles authentication and request
    management to the Mandoline API.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        api_base_url: str | None = None,
        connect_timeout: float | None = None,
        rwp_timeout: float | None = None,
    ):
        """Creates a new Mandoline client instance."""
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

    def _get_auth_header(self) -> Headers:
        if not self.api_key:
            raise ValueError(
                "Mandoline API key required. Set MANDOLINE_API_KEY environment "
                "variable or create one at https://mandoline.ai/account"
            )
        return {"X-API-KEY": self.api_key}

    def _get(self, *, endpoint: str, params: SerializableDict | None = None) -> Any:
        if params and params.get("limit") and params["limit"] > MAX_GET_LIMIT:
            raise ValueError(
                f"Limit exceeds maximum allowed value of {MAX_GET_LIMIT}. "
                "Please reduce the limit."
            )
        return make_request(
            config=self.request_config,
            options=RequestOptions(
                method="GET",
                endpoint=endpoint,
                auth_header=self._get_auth_header(),
                params=params,
            ),
        )

    def _post(
        self,
        *,
        endpoint: str,
        data: SerializableDict,
        params: SerializableDict | None = None,
    ) -> Any:
        return make_request(
            config=self.request_config,
            options=RequestOptions(
                method="POST",
                endpoint=endpoint,
                auth_header=self._get_auth_header(),
                data=data,
                params=params,
            ),
        )

    def _put(self, *, endpoint: str, data: SerializableDict) -> Any:
        return make_request(
            config=self.request_config,
            options=RequestOptions(
                method="PUT",
                endpoint=endpoint,
                auth_header=self._get_auth_header(),
                data=data,
            ),
        )

    def _delete(self, *, endpoint: str) -> Any:
        return make_request(
            config=self.request_config,
            options=RequestOptions(
                method="DELETE",
                endpoint=endpoint,
                auth_header=self._get_auth_header(),
            ),
        )

    # Metric methods
    def create_metric(
        self,
        *,
        name: str,
        description: str,
        tags: NullableStringArray | NotGiven = NOT_GIVEN,
    ) -> Metric:
        """Adds a new evaluation metric."""
        metric_create = MetricCreate(name=name, description=description, tags=tags)

        data = self._post(endpoint="metrics/", data=metric_create.model_dump())
        return Metric.model_validate(data)

    def get_metric(self, *, metric_id: UUID) -> Metric:
        """Fetches a specific metric by its unique identifier."""
        data = self._get(endpoint=f"metrics/{metric_id}")
        return Metric.model_validate(data)

    def get_metrics(
        self,
        *,
        skip: int = 0,
        limit: int = DEFAULT_GET_LIMIT,
        tags: NullableStringArray | NotGiven = NOT_GIVEN,
        filters: SerializableDict | NotGiven = NOT_GIVEN,
    ) -> list[Metric]:
        """Retrieve a list of metrics with optional filtering."""
        params = process_get_options(skip=skip, limit=limit, tags=tags, filters=filters)
        data = self._get(endpoint="metrics/", params=params)
        return [Metric.model_validate(metric_data) for metric_data in data]

    def update_metric(
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

        data = self._put(
            endpoint=f"metrics/{metric_id}", data=metric_update.model_dump()
        )
        return Metric.model_validate(data)

    def delete_metric(self, *, metric_id: UUID) -> None:
        """Removes a metric permanently."""
        self._delete(endpoint=f"metrics/{metric_id}")

    # Evaluation methods
    def create_evaluation(
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
        data = self._post(
            endpoint="evaluations/", data=evaluation_create.model_dump(), params=params
        )
        return Evaluation.model_validate(data)

    def get_evaluation(
        self, *, evaluation_id: UUID, include_content: bool = True
    ) -> Evaluation:
        """Fetches details of a specific evaluation."""
        params = {"include_content": include_content}
        data = self._get(endpoint=f"evaluations/{evaluation_id}", params=params)
        return Evaluation.model_validate(data)

    def get_evaluations(
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
        data = self._get(endpoint="evaluations/", params=params)
        return [Evaluation.model_validate(evaluation_data) for evaluation_data in data]

    def update_evaluation(
        self,
        *,
        evaluation_id: UUID,
        properties: NullableSerializableDict | NotGiven = NOT_GIVEN,
    ) -> Evaluation:
        """Modifies an existing evaluation's properties."""
        evaluation_update = EvaluationUpdate(properties=properties)

        data = self._put(
            endpoint=f"evaluations/{evaluation_id}", data=evaluation_update.model_dump()
        )
        return Evaluation.model_validate(data)

    def delete_evaluation(self, *, evaluation_id: UUID) -> None:
        """Removes an evaluation permanently."""
        self._delete(endpoint=f"evaluations/{evaluation_id}")
