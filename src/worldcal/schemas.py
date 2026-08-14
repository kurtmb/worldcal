from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def new_id() -> str:
    return uuid.uuid4().hex


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RelationshipLabel(str, Enum):
    SAME_SEX = "SAME_SEX"
    DIFFERENT_SEX = "DIFFERENT_SEX"
    INDETERMINATE = "INDETERMINATE"
    INELIGIBLE = "INELIGIBLE"


class NameGuess(str, Enum):
    SAME_SEX = "SAME_SEX"
    DIFFERENT_SEX = "DIFFERENT_SEX"
    NAME_AMBIGUOUS = "NAME_AMBIGUOUS"
    MISSING = "MISSING"


class SamplingConfig(BaseModel):
    """Frozen inference settings for a run. Seed is per-generation, not run-level."""

    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 800
    seed: int | None = None

    @field_validator("temperature")
    @classmethod
    def _temp_range(cls, value: float) -> float:
        if not 0.0 <= value <= 2.0:
            raise ValueError("temperature must be in [0, 2]")
        return value

    @field_validator("top_p")
    @classmethod
    def _top_p_range(cls, value: float) -> float:
        if not 0.0 < value <= 1.0:
            raise ValueError("top_p must be in (0, 1]")
        return value

    def for_generation(self, seed: int | None) -> "SamplingConfig":
        """Copy with a unique per-generation seed (or None to omit)."""
        return self.model_copy(update={"seed": seed})


class ModelRecord(BaseModel):
    id: str
    provider: str
    bedrock_model_id: str
    display_name: str
    seed_supported: bool = False
    # Anthropic Converse on Bedrock rejects temperature and top_p together.
    sampling_knobs: str = "temperature_and_top_p"


class PromptRecord(BaseModel):
    id: str
    scenario: str
    paraphrase: str = "a"
    geography: str = "us-national"
    text: str
    sha256: str = ""
    version: str = "DRAFT"

    def model_post_init(self, __context: Any) -> None:
        if not self.sha256:
            object.__setattr__(self, "sha256", sha256_text(self.text))


class RunRecord(BaseModel):
    id: str
    git_commit: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
    sampling: SamplingConfig
    concurrency: int = 1
    notes: str = ""


class GenerationRecord(BaseModel):
    id: str
    run_id: str
    model_id: str
    prompt_id: str
    prompt_hash: str
    raw_text: str = ""
    response_hash: str = ""
    input_tokens: int | None = None
    output_tokens: int | None = None
    latency_ms: int | None = None
    request_id: str | None = None
    stop_reason: str | None = None
    error: str | None = None
    sampling: SamplingConfig
    created_at: datetime = Field(default_factory=utcnow)
    retry_count: int = 0

    @property
    def succeeded(self) -> bool:
        return self.error is None and bool(self.raw_text)

    def model_post_init(self, __context: Any) -> None:
        if self.raw_text and not self.response_hash:
            object.__setattr__(self, "response_hash", sha256_text(self.raw_text))


class EvidenceSpan(BaseModel):
    field: str
    quote: str
    start: int | None = None
    end: int | None = None


class AnnotationRecord(BaseModel):
    generation_id: str
    relationship: RelationshipLabel
    partnership_term: str | None = None
    adult1_name: str | None = None
    adult2_name: str | None = None
    name_guess: NameGuess = NameGuess.MISSING
    explicit_lgbtq: bool = False
    evidence_spans: list[EvidenceSpan] = Field(default_factory=list)
    schema_version: str = "0.1"
    notes: str = ""
