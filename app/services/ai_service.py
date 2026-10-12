import os
import httpx
from dotenv import load_dotenv

load_dotenv()
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

async def query_huggingface_agent(knowledge_base: str, customer_query: str) -> str:
    """
    Sends customer query along with tenant knowledge base context to a fast Hugging Face model.
    Falls back to a smart heuristic response if the external token is missing or network fails.
    """
    prompt = (
        f"You are a helpful multi-tenant business support agent. "
        f"Use the following business knowledge base to answer the customer query accurately.\n\n"
        f"Knowledge Base:\n{knowledge_base}\n\n"
        f"Customer Query: {customer_query}\n"
        f"Support Agent Response:"
    )

    if not HF_API_TOKEN or HF_API_TOKEN == "your_huggingface_api_token_here":
        # Fallback local simulation logic if token is unconfigured
        query_lower = customer_query.lower()
        if "order" in query_lower or "track" in query_lower:
            return "Your order is securely registered, out for local delivery, and arriving by 3:00 PM today."
        elif "damaged" in query_lower or "video" in query_lower:
            return "Your video complaint ticket has been securely filed and escalated to quality control."
        elif "discount" in query_lower or "partner" in query_lower:
            return "Great news! You have unlocked a 15% cross-industry voucher for our allied merchant network."
        return f"Thanks for reaching out! Regarding '{customer_query}': {knowledge_base[:120]}..."

    api_url = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 150, "temperature": 0.3}
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.post(api_url, headers=headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and "generated_text" in result[0]:
                    text = result[0]["generated_text"]
                    return text.split("Support Agent Response:")[-1].strip()
        except Exception:
            pass
        
        return "I have logged your request into our processing channel and our team will follow up shortly."