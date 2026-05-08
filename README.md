# FortiAIGate Scripts

Simple Python scripts for testing and validating AI traffic flowing through a [Fortinet FortiAIGate](https://www.fortinet.com) proxy to OpenAI.

## What it does

Instead of calling OpenAI's API directly, your script sends requests to your FortiAIGate, which proxies the traffic to OpenAI. This lets FortiAIGate inspect, log, and apply AI Guard policies to all your AI API calls.

```
Your Script → FortiAIGate (https://your-ip:port/v1/...) → OpenAI API
```

## Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/) — fast Python package manager
- A FortiAIGate with an AI Flow configured (Entry Path: `/v1/chat/completions`)
- An OpenAI API key

## Setup

**1. Install uv** (if you haven't already)

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**2. Clone the repo**

```bash
git clone https://github.com/who-would-know/fortiaigate_scripts.git
cd fortiaigate_scripts
```

**3. Configure your settings**

Open `fortiaig_client.py` and update the two lines at the top:

```python
# ── Config ──────────────────────────────────────────────────────────────────
FORTIAIG_URL = "https://your-ip:port/v1"   # e.g. https://192.168.1.10:8443/v1
OPENAI_API_KEY = "sk-proj-..."             # Your OpenAI API key
# ────────────────────────────────────────────────────────────────────────────
```

> **Note:** The script uses `verify=False` to bypass SSL verification for FortiAIGate's self-signed certificate. This is expected for lab/dev environments.

## Run

```bash
uv run fortiaig_client.py
```

`uv` will automatically install dependencies (`openai`, `httpx`) from `pyproject.toml` and run the script — no manual `pip install` needed.

## FortiAIGate Configuration Tips

| Setting | Value |
|---|---|
| Entry Path | `/v1/chat/completions` |
| Schema | `/v1/chat/completions` (OpenAI) |
| Model ID | `gpt-5.4-mini` (use exact API ID, not display name) |
| API Key Validation | Disable for testing, enable for production |

## Files

| File | Description |
|---|---|
| `fortiaig_client.py` | Main client — sends a chat completion through FortiAIGate |
| `fortiaig_client_test.py` | Raw `requests`-based test script for debugging |
| `pyproject.toml` | Project dependencies for uv |
| `uv.lock` | Locked dependency versions |
