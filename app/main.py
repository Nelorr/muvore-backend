from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from app.database import init_db, get_session
from app.models import BusinessTenant, TenantKnowledgeSource
from app.schemas import TenantCreate, TenantRead, SourceCreate, ChatRequest, ChatResponse
from app.controllers.tenant_controller import create_tenant_record, get_tenant_by_id, get_tenant_context
from app.services.ai_service import query_huggingface_agent

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup sequence: Initialize DB tables
    init_db()
    
    # Auto-seed a default test tenant and initial knowledge source for instant testing
    with Session(get_session().__next__()) as session:
        pass  # Handled via standard dependency or manual creation if needed
    yield

app = FastAPI(title="MuvoreAI Backend Platform", version="1.0.0", lifespan=lifespan)

@app.post("/api/tenants", response_model=TenantRead)
def register_tenant(data: TenantCreate, session: Session = Depends(get_session)):
    return create_tenant_record(session, data)

@app.post("/api/ai/chat", response_model=ChatResponse)
async def handle_ai_chat(payload: ChatRequest, session: Session = Depends(get_session)):
    tenant = get_tenant_by_id(session, payload.tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Business tenant profile not found.")
    
    # Pull all dynamic multi-source knowledge chunks for this specific tenant
    knowledge_base = get_tenant_context(session, payload.tenant_id)
    if not knowledge_base:
        knowledge_base = "No specific knowledge sources uploaded yet. Provide general professional support."

    reply = await query_huggingface_agent(knowledge_base, payload.customer_query)
    return ChatResponse(response=reply)

@app.post("/api/tenants/{tenant_id}/sources")
async def add_knowledge_source(
    tenant_id: int, 
    source_data: SourceCreate,  # <--- Imported from schemas.py
    session: Session = Depends(get_session)
):
    tenant = get_tenant_by_id(session, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Business tenant not found.")

    content_chunk = source_data.content_chunk
    if source_data.source_url and not content_chunk:
        content_chunk = await scrape_url_text(source_data.source_url)
        if not content_chunk:
            raise HTTPException(status_code=400, detail="Failed to extract text from the provided URL.")
    
    if not content_chunk:
        raise HTTPException(status_code=400, detail="Content chunk or valid source_url is required.")

    source = TenantKnowledgeSource(
        tenant_id=tenant_id,
        source_type=source_data.source_type,
        source_url=source_data.source_url,
        content_chunk=content_chunk
    )
    session.add(source)
    session.commit()
    
    return {
        "status": "success", 
        "tenant_id": tenant_id,
        "content_chunk": content_chunk,
        "message": "Knowledge source successfully ingested and indexed."
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "system": "MuvoreAI Multi-Tenant RAG API Active"}