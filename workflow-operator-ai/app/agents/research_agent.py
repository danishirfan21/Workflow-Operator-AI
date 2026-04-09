from openai import OpenAI
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def run_research_agent(scraped_data: dict) -> dict:
    if not scraped_data.get("success"):
        return {
            "success": False,
            "error": "Scraping failed"
        }

    content = scraped_data.get("content_snippet", "")

    prompt = f"""
You are a company research analyst.

Given the following website content, extract structured business insights.

Return JSON ONLY in this format:
{{
  "company_summary": "...",
  "industry": "...",
  "possible_use_cases_for_ai": ["...", "..."],
  "target_customer_type": "...",
  "confidence": 0-1
}}

Content:
\"\"\"
{content}
\"\"\"
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    raw_output = response.choices[0].message.content

    # Remove markdown ```json ```
    cleaned = re.sub(r"```json|```", "", raw_output).strip()

    try:
        parsed = json.loads(cleaned)
        return {
            "success": True,
            "data": parsed
        }
    except Exception as e:
        return {
            "success": False,
            "error": "Failed to parse JSON",
            "raw_output": raw_output
        }