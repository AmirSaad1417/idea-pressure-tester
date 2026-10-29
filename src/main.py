import json
import os
from dotenv import load_dotenv
import requests

# Hardcoded test idea
test_idea = "An app that finds study partners nearby"

SYSTEM_PROMPT = """You are a panel of four expert personas evaluating a startup idea.
You must respond ONLY with a valid JSON object with exactly these four keys:
investor, skeptic, customer, competitor.
Each key's value is a string of 2-3 sentences giving that persona's honest reaction.
The investor focuses on market size and returns.
The skeptic looks for fatal flaws and risks.
The customer reacts based on whether they would actually use or pay for this.
The competitor thinks about how they would respond to this entering the market.
Return only the JSON. No markdown, no backticks, no extra text."""

GEMINI_MODEL = "gemini-3.5-flash-lite"

# Module-level storage for teach mode telemetry
last_raw_json = ""
last_search_request = {}


def call_gemini_rest(prompt: str, system_instruction: str = None, json_mode: bool = False) -> str:
    """Fast, reliable REST call to Gemini API avoiding Windows TLS handshake stalls."""
    load_dotenv()
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("GEMINI_API_KEY not found in .env")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={gemini_key}"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    if system_instruction:
        payload["system_instruction"] = {
            "parts": [{"text": system_instruction}]
        }

    if json_mode:
        payload["generationConfig"] = {"response_mime_type": "application/json"}

    response = requests.post(url, json=payload, timeout=25)

    if response.status_code == 429:
        raise RuntimeError("Google API Rate limit reached (429). Please wait a moment and try again.")

    if not response.ok:
        err_msg = response.text
        try:
            err_msg = response.json().get("error", {}).get("message", err_msg)
        except Exception:
            pass
        raise RuntimeError(f"Gemini API error ({response.status_code}): {err_msg}")

    res_json = response.json()
    candidates = res_json.get("candidates", [])
    if not candidates:
        raise RuntimeError("No response candidate returned by Gemini.")

    return candidates[0]["content"]["parts"][0]["text"].strip()


def get_persona_reactions(idea: str) -> dict:
    """Call AI API (OpenAI or Gemini) to get reactions from four personas."""
    global last_raw_json
    load_dotenv()
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    if not openai_key and not gemini_key:
        raise ValueError("ERROR: OPENAI_API_KEY not found in .env")

    # If OPENAI_API_KEY is available, use OpenAI client
    if openai_key:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": idea},
            ],
        )
        content = response.choices[0].message.content
        last_raw_json = content
        return json.loads(content)

    # Use Gemini REST
    text = call_gemini_rest(
        prompt=idea,
        system_instruction=SYSTEM_PROMPT,
        json_mode=True,
    )
    last_raw_json = text
    clean_text = text
    if clean_text.startswith("```"):
        clean_text = clean_text.strip("`")
        if clean_text.startswith("json"):
            clean_text = clean_text[4:]
        clean_text = clean_text.strip()
    return json.loads(clean_text)


def get_web_search_summary(idea: str) -> str:
    """Call AI API (OpenAI or Gemini) to find existing similar startups/products."""
    global last_search_request
    load_dotenv()
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    if not openai_key and not gemini_key:
        raise ValueError("ERROR: OPENAI_API_KEY not found in .env")

    search_prompt = (
        f"Search the web for existing startups or products similar to this idea: {idea}.\n"
        "Summarize what already exists in 3-4 sentences."
    )

    # If OPENAI_API_KEY is available, use OpenAI search tool
    if openai_key:
        from openai import OpenAI
        last_search_request = {
            "model": "gpt-4o-search-preview",
            "user_message": search_prompt,
        }
        client = OpenAI(api_key=openai_key)
        try:
            search_response = client.chat.completions.create(
                model="gpt-4o-search-preview",
                tools=[{"type": "web_search_preview"}],
                messages=[{"role": "user", "content": search_prompt}],
            )
            content = search_response.choices[0].message.content
            if content and content.strip():
                return content.strip()
        except Exception:
            pass
        return "No closely similar products found."

    # Use Gemini
    market_prompt = (
        f"Identify 2-3 real existing products, apps, or startups similar to this idea: '{idea}'.\n"
        "Summarize who they are and what they already offer in 3-4 sentences."
    )
    last_search_request = {
        "model": GEMINI_MODEL,
        "user_message": market_prompt,
    }
    try:
        summary = call_gemini_rest(prompt=market_prompt)
        if summary and summary.strip():
            return summary.strip()
    except Exception:
        pass

    return "No closely similar products found."


def main():
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not found in .env")
        return

    # 1. Persona evaluation call
    try:
        reactions = get_persona_reactions(test_idea)
        print(f"INVESTOR: {reactions.get('investor', '')}\n")
        print(f"SKEPTIC: {reactions.get('skeptic', '')}\n")
        print(f"CUSTOMER: {reactions.get('customer', '')}\n")
        print(f"COMPETITOR: {reactions.get('competitor', '')}")
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse JSON response: {e}")
    except Exception as e:
        print(f"ERROR: OpenAI API call failed: {e}")

    # 2. Web search call for existing similar products/startups
    try:
        summary = get_web_search_summary(test_idea)
        if summary and summary != "No closely similar products found.":
            print(f"\nSIMILAR IDEAS ON THE WEB: {summary}")
        else:
            print("\nNo closely similar products found.")
    except Exception:
        print("\nNo closely similar products found.")


if __name__ == "__main__":
    main()
