"""
proxy OpenAI Proxy Client
--------------------------------
Reads config from a .env file in the same directory as this script.

SETUP:
    1. Create a .env file in this folder (see .env.example for the template)
    2. Fill in your proxy URL and OpenAI API key in the .env file
    3. Run with: uv run fortiaig_client.py

DEPENDENCIES (managed automatically by uv via pyproject.toml):
    - openai       : Official OpenAI Python SDK (handles /v1/chat/completions etc.)
    - httpx        : HTTP client used under the hood by the OpenAI SDK;
                     needed here so we can disable SSL verification for
                     proxy's self-signed certificate.
    - python-dotenv: Loads environment variables from your local .env file
                     so secrets never get hardcoded in the script.

ERROR HANDLING:
    - 500 errors are a known intermittent proxy bug.
      The script will automatically retry up to MAX_RETRIES times with
      a delay between each attempt and print clear debug info per attempt.
"""

import sys
import os
import time
import httpx
import openai
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

# ── Retry config ──────────────────────────────────────────────────────────────
# Tweak these if you want more/fewer retries or a longer delay between them.
MAX_RETRIES   = 1   # number of attempts before giving up
RETRY_DELAY_S = 2   # seconds to wait between retries
# ─────────────────────────────────────────────────────────────────────────────

# Fail fast with a clear message if either variable is missing
if not FORTIAIG_URL:
    sys.exit(1) 
    ValueError("FORTIAIG_URL is not set. Add it to your .env file.")
if not OPENAI_API_KEY:
    sys.exit(1) 
    ValueError("OPENAI_API_KEY is not set. Add it to your .env file.")


def get_client() -> OpenAI:
    """
    Return an OpenAI client routed through the proxy.

    verify=False disables SSL certificate verification — required when
    proxy is using a self-signed cert. For production, replace
    False with the path to your CA bundle, e.g. verify="/path/to/ca.crt"
    """
    return OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=FORTIAIG_URL,
        http_client=httpx.Client(verify=False),  # ← bypasses self-signed cert error
    )


def chat(prompt: str, model: str = "gpt-5.4-mini") -> str:
    """
    Send a prompt through proxy and return the response text.

    Retries automatically on 500 errors (known intermittent proxy
    proxy bug) up to MAX_RETRIES times with RETRY_DELAY_S seconds between
    each attempt. Prints clear debug info on every failure so you can
    track exactly where and when it is erroring.
    """
    client = get_client()

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"[Attempt {attempt}/{MAX_RETRIES}] Sending request to: {FORTIAIG_URL}")
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
            )
            # Success — print attempt info so you can see how many tries it took
            print(f"[Attempt {attempt}/{MAX_RETRIES}] ✓ Success")
            return response.choices[0].message.content

        except openai.InternalServerError as e:
            # 500 error — likely the intermittent proxy proxy bug
            print(f"[Attempt {attempt}/{MAX_RETRIES}] ✗ 500 InternalServerError from proxy proxy")
            print(f"  Error type    : {type(e).__name__}")
            print(f"  Error message : {e.message}")
            print(f"  Status code   : {e.status_code}")
            print(f"  Raw response  : {e.response.text if e.response else 'N/A'}")
            if attempt < MAX_RETRIES:
                print(f"  Retrying in {RETRY_DELAY_S}s...\n")
                time.sleep(RETRY_DELAY_S)
            else:
                print(f"\n[✗] All {MAX_RETRIES} attempts failed with 500.")
                print("    This appears to be an intermittent proxy proxy bug.")
                print("    Check your proxy logs for more detail.")
                sys.exit(1)  # re-sys.exit(1) so the full traceback is still visible

        except openai.AuthenticationError as e:
            # 401 — bad API key, no point retrying
            print(f"[✗] Authentication failed (401) — check your OPENAI_API_KEY in .env")
            print(f"    Error: {e.message}")
            sys.exit(1)

        except openai.APIConnectionError as e:
            # Can't reach proxy at all
            print(f"[Attempt {attempt}/{MAX_RETRIES}] ✗ Cannot connect to proxy")
            print(f"  URL           : {FORTIAIG_URL}")
            print(f"  Error         : {e}")
            if attempt < MAX_RETRIES:
                print(f"  Retrying in {RETRY_DELAY_S}s...\n")
                time.sleep(RETRY_DELAY_S)
            else:
                print(f"\n[✗] All {MAX_RETRIES} attempts failed — is proxy reachable?")
                sys.exit(1)

        except openai.APIStatusError as e:
            # Any other non-200 status (404, 403, etc.) — print and stop
            print(f"[✗] Unexpected API error (HTTP {e.status_code})")
            print(f"    Error type    : {type(e).__name__}")
            print(f"    Error message : {e.message}")
            print(f"    Raw response  : {e.response.text if e.response else 'N/A'}")
            sys.exit(1)


# ── Run ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    reply = chat("Say hello and confirm you are reachable please thanks!.")
    print("\nResponse:")
    print(reply)