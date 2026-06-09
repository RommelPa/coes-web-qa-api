from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Question about the indexed COES WebApi documentation.",
    )
    top_k: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Number of relevant chunks to retrieve.",
    )


class SourceChunk(BaseModel):
    chunk_id: str
    page_url: str
    page_title: str
    score: float
    text: str


class AskResponse(BaseModel):
    answer: str
    confidence: str
    sources: list[SourceChunk]


class MetadataResponse(BaseModel):
    source_url: str
    built_at_utc: str
    page_count: int
    chunk_count: int