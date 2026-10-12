from pydantic import BaseModel
from typing import Optional

class TenantCreate(BaseModel):
    business_name: str
    industry_category: str
    faqs_content: str
    whatsapp_handle: Optional[str] = None

class TenantRead(TenantCreate):
    id: int

class ChatRequest(BaseModel):
    tenant_id: int
    customer_query: str

class ChatResponse(BaseModel):
    response: str