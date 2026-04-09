from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def run_email_agent(research_data: dict, qualification_data: dict) -> dict:
    prompt = f"""
You are a B2B sales outreach system.

Generate a personalized cold email based on the company research and qualification.

Return ONLY valid JSON:
{{
  "subject": "...",
  "email_body": "...",
  "tone": "professional",
  "confidence": 0-1
}}

Company Research:
{json.dumps(research_data)}

Qualification Decision:
{json.dumps(qualification_data)}

Rules:
- Keep email concise
- Make it personalized (mention company context)
- Focus on value
- No fluff
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    raw_output = response.choices[0].message.content
    cleaned = re.sub(r"```json|```", "", raw_output).strip()

    try:
        parsed = json.loads(cleaned)
        return {
            "success": True,
            "data": parsed
        }
    except Exception:
        return {
            "success": False,
            "raw_output": raw_output
        }