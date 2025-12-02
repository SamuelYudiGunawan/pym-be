from datetime import datetime
import typing as t
from pydantic import BaseModel, Field


class NoteData(BaseModel):
    id: int
    content: str
    author: str
    is_anonymous: bool
    created_at: str
    reply_count: int


class ReplyData(BaseModel):
    id: int
    content: str
    author: str
    is_anonymous: bool
    created_at: str


class NoteDetailData(BaseModel):
    id: int
    content: str
    author: str
    is_anonymous: bool
    created_at: str
    reply_count: int
    replies: t.List[ReplyData]


class NotesListData(BaseModel):
    notes: t.List[NoteData]
    has_next: bool
    has_previous: bool
    current_page: int
    total_pages: int


class NoteCreateRequest(BaseModel):
    content: str = Field(...,
                         description="Your thoughts to share with the world")
    author_name: t.Optional[str] = Field(
        None, description="Your name (optional - leave blank to post anonymously)")


class ReplyCreateRequest(BaseModel):
    content: str = Field(..., description="Your response to this thought")
    author_name: t.Optional[str] = Field(
        None, description="Your name (optional - leave blank to reply anonymously)")


class NoteCreateResponse(BaseModel):
    success: bool
    note: NoteData


class ReplyCreateResponse(BaseModel):
    success: bool
    reply: ReplyData


class AboutData(BaseModel):
    name: str
    description: str
    features: t.List[str]
    version: str


class AboutResponse(BaseModel):
    about: AboutData
