from sqlmodel import Session, select
from app.models import BusinessTenant
from app.models import TenantKnowledgeSource
from app.schemas import TenantCreate

def create_tenant_record(session: Session, data: TenantCreate) -> BusinessTenant:
    db_tenant = BusinessTenant.model_validate(data)
    session.add(db_tenant)
    session.commit()
    session.refresh(db_tenant)
    return db_tenant

def get_tenant_by_id(session: Session, tenant_id: int) -> BusinessTenant | None:
    return session.get(BusinessTenant, tenant_id)

def get_tenant_context(session: Session, tenant_id: int) -> str:
    # Fetch all knowledge chunks belonging to this specific business
    statement = select(TenantKnowledgeSource).where(TenantKnowledgeSource.tenant_id == tenant_id)
    sources = session.exec(statement).all()
    
    # Combine chunks into a robust knowledge base for the AI prompt
    return "\n".join([source.content_chunk for source in sources])