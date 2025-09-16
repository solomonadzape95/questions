# app/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional

class QuestionRequest(BaseModel):
    category: str
    num_questions: int = 10

class Question(BaseModel):
    question: str
    options: List[str]
    answer: str

class QuestionResponse(BaseModel):
    category: str
    questions: List[Question]


# Share Records API
class ShareRecordCreate(BaseModel):
    shared_by: str = Field(..., min_length=1)
    shared_to: str = Field(..., min_length=1)
    pub_key: str = Field(..., min_length=1)
    project: str = Field(..., min_length=1)

class ShareRecord(BaseModel):
    id: int
    shared_by: str
    shared_to: str
    pub_key: str
    project: str
