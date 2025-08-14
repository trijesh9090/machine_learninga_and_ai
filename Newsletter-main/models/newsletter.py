from dataclasses import dataclass, field
from typing import Optional, Literal
from uuid import uuid4
from datetime import datetime


@dataclass
class Newsletter:
    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    description: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    published_at: Optional[datetime] = None
    content: Optional[str] = None
    author: Optional[str] = None
    type: Literal["news", "research"] = "news"
    is_prioritized: bool = False
    priority_reason: Optional[str] = None
    summary: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "source": self.source,
            "published_at": (
                self.published_at.isoformat() if self.published_at else None
            ),
            "content": self.content,
            "author": self.author,
            "type": self.type,
            "is_prioritized": self.is_prioritized,
            "priority_reason": self.priority_reason,
            "summary": self.summary,
        }
