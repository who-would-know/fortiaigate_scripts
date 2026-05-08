"""
FortiAIGate OpenAI Proxy Client
--------------------------------
Reads config from a .env file in the same directory as this script.
 
SETUP:
    1. Create a .env file in this folder (see .env.example for the template)
    2. Fill in your FortiAIGate URL and OpenAI API key in the .env file
    3. Run with: uv run fortiaig_client.py
 
DEPENDENCIES (managed automatically by uv via pyproject.toml):
    - openai       : Official OpenAI Python SDK (handles /v1/chat/completions etc.)
    - httpx        : HTTP client used under the hood by the OpenAI SDK;
                     needed here so we can disable SSL verification for
                     FortiAIGate's self-signed certificate.
    - python-dotenv: Loads environment variables from your local .env file
                     so secrets never get hardcoded in the script.
"""

import os
import httpx
from openai import OpenAI
from dotenv import load_dotenv

# ── Load .env ────────────────────────────────────────────────────────────────
# Looks for a .env file in the same directory as this script and loads it
# into environment variables. Does nothing if .env doesn't exist.
load_dotenv()
# ─────────────────────────────────────────────────────────────────────────────
 

# ── Config (loaded from .env) ─────────────────────────────────────────────────
# Set these in your .env file — do NOT hardcode values here.
# See .env.example for the template.
FORTIAIG_URL   = os.getenv("FORTIAIG_URL")    # e.g. https://192.168.1.10:8443/v1
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # e.g. sk-proj-...
# ─────────────────────────────────────────────────────────────────────────────
 
# Fail fast with a clear message if either variable is missing
if not FORTIAIG_URL:
    raise ValueError("FORTIAIG_URL is not set. Add it to your .env file.")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set. Add it to your .env file.")


def get_client() -> OpenAI:
    """
    Return an OpenAI client routed through the FortiAIGate proxy.

    verify=False disables SSL certificate verification — required when
    FortiAIGate is using a self-signed cert. For production, replace
    False with the path to your CA bundle, e.g. verify="/path/to/ca.crt"
    """
    return OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=FORTIAIG_URL,
        http_client=httpx.Client(verify=False),  # ← bypasses self-signed cert error
    )

# Updated gpt-4o to gpt-5.4-mini
def chat(prompt: str, model: str = "gpt-5.4-mini") -> str: 
    """Send a prompt and return the response text."""
    client = get_client()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


# ── Run ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    reply = chat("Say hello and confirm you are reachable please thanks!.")
    print(reply)
