import requests
from bs4 import BeautifulSoup


def fetch_company_website(url: str) -> dict:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Title
        title = soup.title.string if soup.title else None

        # Meta description
        meta_desc_tag = soup.find("meta", attrs={"name": "description"})
        meta_description = (
            meta_desc_tag["content"] if meta_desc_tag and "content" in meta_desc_tag.attrs else None
        )

        # Extract visible text (basic)
        paragraphs = soup.find_all("p")
        text_content = " ".join([p.get_text(strip=True) for p in paragraphs])

        return {
            "success": True,
            "title": title,
            "meta_description": meta_description,
            "content_snippet": text_content[:1000]  # limit size
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }