"""Data models for the ingestion pipeline."""

import hashlib
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class RawDocument:
    """Raw bytes of a source document and their SHA-256 digest."""

    content: bytes = field(repr=False)
    sha256: str = field(init=False)

    def __post_init__(self) -> None:
        # frozen=True blocks normal assignment; the digest is derived from content.
        object.__setattr__(self, "sha256", hashlib.sha256(self.content).hexdigest())
