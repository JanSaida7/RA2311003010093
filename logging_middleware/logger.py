import requests
import os

LOG_API = "http://20.207.122.201/evaluation-service/logs"


def get_auth_token():
    token = os.getenv("EVAL_AUTH_TOKEN")
    if not token:
        raise RuntimeError("EVAL_AUTH_TOKEN is not set")
    return token

def Log(stack, level, package, message):
    headers = {
        "Authorization": f"Bearer {get_auth_token()}",
        "Content-Type": "application/json"
    }
    payload = {
        "stack": stack.lower(),
        "level": level.lower(),
        "package": package.lower(),
        "message": message
    }
    try:
        response = requests.post(LOG_API, json=payload, headers=headers, timeout=5)
        if response.status_code >= 400:
            print(f"Log Error: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Log Error: {e}")


log_event = Log


if __name__ == "__main__":
    Log("backend", "info", "utils", "Verification test: Middleware is active")