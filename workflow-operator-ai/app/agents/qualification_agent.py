from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def run_qualification_agent(research_data: dict) -> dict:
    prompt = f"""
You are a sales qualification system.

Your job is to decide if a lead is worth contacting.

Return ONLY valid JSON in this format:
{{
  "qualified": true,
  "score": 0-100,
  "reasoning": "...",
  "recommended_action": "send_email" or "ignore",
  "confidence": 0-1
}}

Lead Research Data:
{json.dumps(research_data)}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
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