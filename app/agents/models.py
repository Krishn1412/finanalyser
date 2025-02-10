from typing import List, Optional

from pydantic import BaseModel
class Document(BaseModel):
    """Represents a document with its content."""

    content: str
    source: Optional[str] = None


class ChatMessage(BaseModel):
    """Represents a chat message."""

    role: str
    content: str


class ChatResponse(BaseModel):
    """Represents a response from the chat model."""

    output_text: str