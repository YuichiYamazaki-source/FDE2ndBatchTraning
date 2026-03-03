import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

SYSTEM_PROMPT = """You are a news credibility checker.

Given a claim, you will:
1. Search for multiple sources covering this claim (supporting AND opposing views)
2. Compare what different sources say
3. Identify any contradictions
4. Assign a credibility score based on source consensus and evidence quality

Always search at least 3 different angles before concluding.
"""

def check_credibility(claim: str) -> dict:
    print(f"\nChecking: \"{claim}\"\n")
    print("Searching sources...")

    response = client.responses.create(
        model="gpt-4o",
        tools=[{"type": "web_search_preview"}],
        instructions=SYSTEM_PROMPT,
        input=f"""Verify this claim: "{claim}"

Search for:
1. Sources that SUPPORT this claim
2. Sources that CONTRADICT or DENY this claim
3. Fact-check sites covering this claim

After searching, output a JSON object with exactly this structure:
{{
  "score": <integer 0-100>,
  "label": "<one of: Likely True | Mostly Supported | Contested | Likely False | Misinformation>",
  "sources": [
    {{"outlet": "...", "stance": "supports|denies|neutral", "key_point": "..."}}
  ],
  "contradictions": ["..."],
  "explanation": "2-3 sentence summary"
}}

Output ONLY the JSON, nothing else."""
    )

    text = response.output_text
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        return json.loads(text[start:end])
    except json.JSONDecodeError:
        return {"raw": text}


def display_result(claim: str, result: dict):
    print("\n" + "=" * 60)
    print(f"CLAIM: {claim}")
    print("=" * 60)

    if "raw" in result:
        print(result["raw"])
        return

    score = result.get("score", 0)
    label = result.get("label", "N/A")

    filled = score // 5
    bar = "#" * filled + "-" * (20 - filled)
    print(f"\nSCORE : {score}/100  [{bar}]")
    print(f"LABEL : {label}\n")

    sources = result.get("sources", [])
    if sources:
        print("SOURCES:")
        icons = {"supports": "[+]", "denies": "[-]", "neutral": "[o]"}
        for s in sources:
            icon = icons.get(s.get("stance"), "[?]")
            print(f"  {icon} [{s.get('stance'):8}]  {s.get('outlet')}")
            print(f"              -> {s.get('key_point')}")

    contradictions = result.get("contradictions", [])
    if contradictions:
        print("\nCONTRADICTIONS:")
        for c in contradictions:
            print(f"  !! {c}")

    print(f"\nSUMMARY:\n  {result.get('explanation', '')}")
    print("=" * 60)


if __name__ == "__main__":
    claim = input("Enter claim to verify: ").strip()
    if claim:
        result = check_credibility(claim)
        display_result(claim, result)
    else:
        print("No claim entered.")
