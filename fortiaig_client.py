"""
FortiAIGate OpenAI Proxy Client
--------------------------------
Set your FortiAIGate URL and API key below, then run.

INSTALL DEPENDENCIES:
    pip install openai httpx

    - openai  : Official OpenAI Python SDK (handles /v1/chat/completions etc.)
    - httpx   : HTTP client used under the hood by the OpenAI SDK;
                needed here so we can disable SSL verification for
                FortiAIGate's self-signed certificate.
"""

import httpx
from openai import OpenAI

# ── Config ──────────────────────────────────────────────────────────────────
FORTIAIG_URL = "xxx"  # e.g. https://192.168.1.10:8443
OPENAI_API_KEY = "xxxx"
# ────────────────────────────────────────────────────────────────────────────


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
