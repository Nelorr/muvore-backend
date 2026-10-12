import httpx
from bs4 import BeautifulSoup

async def scrape_url_text(url: str) -> str:
    headers = {"User-Agent": "MuvoreAI-Bot/1.0 (Customer Support RAG)"}
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        try:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Remove clutter elements that don't contain product/business info
                for element in soup(["script", "style", "nav", "footer", "header"]):
                    element.extract()
                
                # Extract clean text
                text = soup.get_text(separator=" ", strip=True)
                return text[:6000]  # Cap character limit to prevent overflowing AI token limits
        except Exception as e:
            print(f"Error scraping URL: {e}")
            
    return ""