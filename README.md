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

**3. Create your `.env` file**

Copy the example template and fill in your values:

```bash
# Mac/Linux
cp .env.example .env

# Windows
copy .env.example .env
```

Then open `.env` and set your values:

```env
FORTIAIG_URL=https://your-fortiaig-ip:port/v1
OPENAI_API_KEY=sk-proj-...
```

> ⚠️ **Never commit `.env` to git.** It contains secrets and is already listed in `.gitignore`.

> **SSL note:** The script uses `verify=False` to bypass SSL verification for FortiAIGate's self-signed certificate. This is expected for lab/dev environments.

## Run

```bash
uv run fortiaig_client.py
```

`uv` will automatically install all dependencies (`openai`, `httpx`, `python-dotenv`) from `pyproject.toml` — no manual `pip install` needed.

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
| `.env.example` | Template for your `.env` file — copy this, never edit directly |
| `pyproject.toml` | Project dependencies for uv |
| `uv.lock` | Locked dependency versions |
