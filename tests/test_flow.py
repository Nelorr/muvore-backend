# tests/test_flow.py
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session

# 1. Setup an isolated in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# 2. Override the get_session dependency so FastAPI uses our test database
def get_test_session():
    with Session(engine) as session:
        yield session

app.dependency_overrides[get_session] = get_test_session

@pytest.fixture(name="client", scope="module", autouse=True)
def setup_test_db():
    # Create tables before tests run
    SQLModel.metadata.create_all(engine)
    client = TestClient(app)
    yield client
    # Clean up tables after tests finish
    SQLModel.metadata.drop_all(engine)

# 3. Test Cases
def test_create_tenant(client: TestClient):
    """Test registering a new business tenant."""
    payload = {
        "business_name": "Lagos Fashion Hub",
        "industry_category": "Fashion",
        "faqs_content": "Whatsapp",
        "whatsapp_handle": "+2348000000000"
    }
    response = client.post("/api/tenants", json=payload)
    
    assert response.status_code in (200, 201)
    data = response.json()
    assert data["business_name"] == "Lagos Fashion Hub"
    assert "id" in data


def test_ingest_knowledge_source(client: TestClient):
    """Test adding manual knowledge text (delivery fees & pricing)."""
    # Create tenant first
    tenant_res = client.post("/api/tenants", json={
        "business_name": "Kicks & Threads",
        "industry_category": "Footwear"
    })
    tenant_id = tenant_res.json()["id"]

    # Ingest knowledge chunk
    source_payload = {
        "source_type": "manual",
        "content_chunk": "Ankara sneakers cost ₦25,000. Delivery to Lekki and Ikeja is ₦2,500 within 24 hours."
    }
    response = client.post(f"/api/tenants/{tenant_id}/sources", json=source_payload)

    assert response.status_code in (200, 201)
    data = response.json()
    assert data["tenant_id"] == tenant_id
    assert "₦25,000" in data["content_chunk"]


def test_ai_chat_with_retrieved_context(client: TestClient):
    """Test asking a question and verifying RAG responses with tenant context."""
    # Create tenant and ingest knowledge
    tenant_res = client.post("/api/tenants", json={
        "business_name": "Gourmet Kitchen",
        "industry_category": "Food"
    })
    tenant_id = tenant_res.json()["id"]

    client.post(f"/api/tenants/{tenant_id}/sources", json={
        "source_type": "business_policy",
        "content_chunk": "Bank account details: GTBank 0123456789, Gourmet Kitchen Ltd. Interstate shipping takes 3 days."
    })

    # Query AI chat endpoint
    chat_payload = {
        "tenant_id": tenant_id,
        "customer_query": "What are your bank details for payment?"
    }
    response = client.post("/api/ai/chat", json=chat_payload)

    assert response.status_code == 200
    res_data = response.json()
    assert "response" in res_data
    assert len(res_data["response"]) > 0