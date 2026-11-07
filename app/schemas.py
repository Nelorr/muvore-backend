from pydantic import BaseModel
from typing import Optional

class TenantCreate(BaseModel):
    business_name: str
    industry_category: str
    faqs_content: Optional[str]= None
    whatsapp_handle: Optional[str] = None

class TenantRead(TenantCreate):
    id: int

class SourceCreate(BaseModel):
    source_type: str  # e.g., "manual", "website", "business_policy"
    content_chunk: Optional[str] = None
    source_url: Optional[str] = None


class ChatRequest(BaseModel):
    tenant_id: int
    customer_query: str

class ChatResponse(BaseModel):
    response: str