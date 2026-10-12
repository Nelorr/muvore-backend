from sqlmodel import SQLModel, Field
from typing import Optional

class BusinessTenant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    business_name: str
    industry_category: str

class TenantKnowledgeSource(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="businesstenant.id")
    source_type: str  # e.g., "website", "instagram_comments", "product_catalog"
    source_url: Optional[str] = None
    content_chunk: str  # The scraped text or parsed comments ready for AIs