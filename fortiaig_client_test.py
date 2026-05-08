import requests

FORTIAIG_URL = "xxx"
OPENAI_API_KEY = "xxxx"
    FORTIAIG_URL,
    headers={
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "model": "gpt-5.4-mini",
        "messages": [{"role": "user", "content": "Say hello!"}],
    },
    verify=False,  # self-signed cert
)

print(response.status_code)
print(response.json())