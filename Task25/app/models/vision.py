from typing import Any, Literal


from pydantic import BaseModel, Field


AnalysisType = Literal[
    "general",
    "document",
    "product",
    "ui",
]


class VisionResult(BaseModel):
    analysis_type: AnalysisType

    description: str = ""

    visible_text: list[str] = Field(
        default_factory=list
    )

    objects: list[str] = Field(
        default_factory=list
    )

    attributes: dict[str, Any] = Field(
        default_factory=dict
    )

    uncertain_details: list[str] = Field(
        default_factory=list
    )

    answer: str | None = None

    observed: list[str] = Field(
        default_factory=list
    )

    not_determinable: list[str] = Field(
        default_factory=list
    )


class DocumentResult(VisionResult):
    document_type: str | None = None

    fields: dict[str, Any] = Field(
        default_factory=dict
    )


class ProductResult(VisionResult):
    product_category: str | None = None

    colors: list[str] = Field(
        default_factory=list
    )

    visible_features: list[str] = Field(
        default_factory=list
    )


class UIResult(VisionResult):
    screen_type: str | None = None

    components: list[str] = Field(
        default_factory=list
    )

    buttons: list[str] = Field(
        default_factory=list
    )

    input_fields: list[str] = Field(
        default_factory=list
    )

    navigation_elements: list[str] = Field(
        default_factory=list
    )

    usability_observations: list[str] = Field(
        default_factory=list
    )


class ImageMetadata(BaseModel):
    file_name: str

    content_type: str

    size_bytes: int

    width: int | None = None

    height: int | None = None


class VisionResponse(BaseModel):
    success: bool

    status_code: int

    data: VisionResult

    metadata: ImageMetadata


class DifferenceItem(BaseModel):
    type: str

    description: str


class ComparisonResult(BaseModel):
    summary: str

    differences: list[DifferenceItem] = Field(
        default_factory=list
    )

    uncertain_details: list[str] = Field(
        default_factory=list
    )


class ComparisonResponse(BaseModel):
    success: bool

    status_code: int

    data: ComparisonResult

    metadata: dict[str, ImageMetadata]