import json
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

# ==========================================
# User Schemas
# ==========================================
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: str = Field(..., max_length=100)
    password: str = Field(...)

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==========================================
# Question Schemas
# ==========================================
class QuestionBase(BaseModel):
    category: str = Field(..., description="Category of challenge, e.g. 'mathematics', 'logical', 'verbal'")
    title: str = Field(..., min_length=3, max_length=255)
    content: str = Field(..., description="Challenge text or body")
    options: Optional[List[str]] = Field(default=None, description="Optional array of string choices for multiple-choice questions")

    @field_validator("options", mode="before")
    @classmethod
    def parse_options(cls, v):
        """
        Converts JSON string from SQLite text column into list of strings if necessary,
        allowing seamless mapping from SQLAlchemy to the frontend.
        """
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return []
        return v

class QuestionCreate(QuestionBase):
    correct_answer: str = Field(..., description="The correct answer string")

class QuestionUpdate(BaseModel):
    category: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    is_active: Optional[bool] = None

class QuestionResponse(QuestionBase):
    id: int
    is_active: bool
    correct_answer: str
    activated_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ==========================================
# Submission Schemas
# ==========================================
class SubmissionBase(BaseModel):
    submitted_answer: str

class SubmissionCreate(SubmissionBase):
    question_id: int

class SubmissionResponse(SubmissionBase):
    id: int
    user_id: int
    question_id: int
    is_correct: bool
    submitted_at: datetime

    class Config:
        from_attributes = True
