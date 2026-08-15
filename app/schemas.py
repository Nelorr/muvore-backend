
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserRegister(BaseModel):
    company_name: str = Field(..., example="Acme Corp")
    email: EmailStr = Field(..., example="admin@acme.com")
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    company_id: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class KnowledgeCreate(BaseModel):
    title: str = Field(..., example="Return Policy")
    content: str = Field(..., example="We offer full refunds within 30 days.")

class KnowledgeResponse(BaseModel):
    id: int
    company_id: int
    title: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True