from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str
    chat_history: List[Dict[str, str]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    answer: str
    diagnostics: Dict[str, Any] = Field(default_factory=dict)


class RoutedQuery(BaseModel):
    intent: str
    metric: str
    sector: Optional[str] = None
    timeframe: Optional[str] = None
    board_scope: List[str] = Field(default_factory=list)
    needs_clarification: bool = False
    clarification_question: Optional[str] = None
    leadership_update_mode: bool = False


class BoardColumn(BaseModel):
    id: str
    title: str
    type: str


class BoardItem(BaseModel):
    id: str
    name: str
    column_values: Dict[str, Any]


class BoardData(BaseModel):
    board_id: str
    board_name: str
    columns: List[BoardColumn]
    items: List[BoardItem]