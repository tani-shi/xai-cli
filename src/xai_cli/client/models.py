from __future__ import annotations

from collections.abc import Callable
from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from xai_cli.domain import normalize_domain, normalize_handle, validate_date_range
from xai_cli.errors import InvalidRequestError


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class XSearchTool(BaseModel):
    type: Literal["x_search"] = "x_search"
    allowed_x_handles: Annotated[list[str], Field(max_length=20)] | None = None
    excluded_x_handles: Annotated[list[str], Field(max_length=20)] | None = None
    from_date: date | None = None
    to_date: date | None = None
    enable_image_understanding: bool | None = None
    enable_video_understanding: bool | None = None

    @model_validator(mode="after")
    def validate_filters(self) -> XSearchTool:
        if self.allowed_x_handles and self.excluded_x_handles:
            raise ValueError("allowed and excluded X handles cannot be combined")
        self.allowed_x_handles = _normalized_unique(self.allowed_x_handles, normalize_handle)
        self.excluded_x_handles = _normalized_unique(self.excluded_x_handles, normalize_handle)
        try:
            validate_date_range(self.from_date, self.to_date)
        except InvalidRequestError as exc:
            raise ValueError(str(exc)) from exc
        return self


class WebSearchFilters(BaseModel):
    allowed_domains: Annotated[list[str], Field(max_length=5)] | None = None
    excluded_domains: Annotated[list[str], Field(max_length=5)] | None = None

    @model_validator(mode="after")
    def validate_domains(self) -> WebSearchFilters:
        if self.allowed_domains and self.excluded_domains:
            raise ValueError("allowed and excluded domains cannot be combined")
        self.allowed_domains = _normalized_unique(self.allowed_domains, normalize_domain)
        self.excluded_domains = _normalized_unique(self.excluded_domains, normalize_domain)
        return self


class WebSearchTool(BaseModel):
    type: Literal["web_search"] = "web_search"
    filters: WebSearchFilters | None = None
    enable_image_understanding: bool | None = None
    enable_image_search: bool | None = None


SearchTool = XSearchTool | WebSearchTool


class InputMessage(BaseModel):
    role: Literal["user"] = "user"
    content: str = Field(min_length=1)


class ResponseRequest(BaseModel):
    model: str = Field(min_length=1)
    input: list[InputMessage]
    tools: list[SearchTool]
    stream: bool


class UrlCitation(ApiModel):
    type: str = "url_citation"
    url: str
    title: str | None = None
    start_index: int | None = None
    end_index: int | None = None


class OutputContent(ApiModel):
    type: str
    text: str | None = None
    annotations: list[UrlCitation] = Field(default_factory=list)


class ResponseOutput(ApiModel):
    type: str
    content: list[OutputContent] = Field(default_factory=list)


class ResponseEnvelope(ApiModel):
    id: str
    model: str | None = None
    status: str | None = None
    output: list[ResponseOutput]
    citations: list[str] = Field(default_factory=list)

    @property
    def text(self) -> str:
        return "\n".join(
            content.text
            for item in self.output
            if item.type == "message"
            for content in item.content
            if content.type == "output_text" and content.text is not None
        )

    @property
    def citation_urls(self) -> list[str]:
        urls = [*self.citations]
        urls.extend(
            annotation.url
            for item in self.output
            for content in item.content
            for annotation in content.annotations
        )
        return list(dict.fromkeys(urls))


class ModelInfo(ApiModel):
    id: str | None = None
    name: str | None = None
    owned_by: str | None = None

    @property
    def identifier(self) -> str:
        return self.id or self.name or "unknown"


class ModelsResponse(ApiModel):
    data: list[ModelInfo] = Field(default_factory=list)


class ErrorDetail(ApiModel):
    message: str
    type: str | None = None
    code: str | None = None


class DeltaEvent(BaseModel):
    type: Literal["response.output_text.delta"]
    delta: str


class CompletedEvent(BaseModel):
    type: Literal["response.completed"]
    response: ResponseEnvelope


class FailedEvent(BaseModel):
    type: Literal["response.failed"]
    response: ResponseEnvelope | None = None
    error: ErrorDetail | None = None


class IncompleteEvent(BaseModel):
    type: Literal["response.incomplete"]
    response: ResponseEnvelope | None = None


class ErrorEvent(ApiModel):
    type: Literal["error"]
    message: str | None = None
    code: str | None = None
    error: ErrorDetail | None = None

    @model_validator(mode="after")
    def validate_error(self) -> ErrorEvent:
        if self.message is None and self.error is None:
            raise ValueError("error event must include message or error details")
        return self

    @property
    def detail(self) -> ErrorDetail:
        if self.error is not None:
            return self.error
        return ErrorDetail(message=self.message or "The response failed.", code=self.code)


StreamTerminalEvent = CompletedEvent | FailedEvent | IncompleteEvent | ErrorEvent
StreamEvent = DeltaEvent | StreamTerminalEvent


class Answer(BaseModel):
    schema_version: Literal[1] = 1
    response_id: str
    model: str | None = None
    status: str
    text: str
    citations: list[str]

    @classmethod
    def from_response(cls, response: ResponseEnvelope) -> Answer:
        return cls(
            response_id=response.id,
            model=response.model,
            status=response.status or "completed",
            text=response.text,
            citations=response.citation_urls,
        )


def _normalized_unique(
    values: list[str] | None, normalizer: Callable[[str], str]
) -> list[str] | None:
    if values is None:
        return None
    normalized = [normalizer(value) for value in values]
    if len(set(normalized)) != len(normalized):
        raise ValueError("filter values must be unique")
    return normalized
