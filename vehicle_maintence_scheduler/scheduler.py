import requests
import sys
import os

BASE_URL = "http://20.207.122.201/evaluation-service"
AUTH_DATA = {
    "email": "jansaidasyed743@gmail.com",
    "name": "Syed Jan Saida",
    "rollNo": "RA2311003010093",
    "accessCode": "QkbpxH",
    "clientID": "8b9078f6-7fcc-4bfc-9543-1cd90ed63c28",
    "clientSecret": "nzPWAFBCNhbWMMmB",
}


def get_access_token():
    response = requests.post(f"{BASE_URL}/auth", json=AUTH_DATA, timeout=10)
    if response.status_code not in (200, 201):
        raise RuntimeError(f"Auth Failed: {response.status_code} {response.text}")

    token_data = response.json()
    token = token_data.get("access_token") or token_data.get("token")
    if not token:
        raise RuntimeError("Auth response did not include an access token")
    return token


# Ensure the project root is searched before any installed packages with the same name.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


AUTH_TOKEN = get_access_token()
os.environ["EVAL_AUTH_TOKEN"] = AUTH_TOKEN

try:
    from logging_middleware.logger import Log
except ImportError:
    from logging_middleware.logger import log_event as Log

HEADERS = {"Authorization": f"Bearer {AUTH_TOKEN}"}

def get_scheduler_data():
    Log("backend", "info", "service", "Initiating GET requests for depots and vehicles")
    depots_res = requests.get(f"{BASE_URL}/depots", headers=HEADERS)
    vehicles_res = requests.get(f"{BASE_URL}/vehicles", headers=HEADERS)
    
    if depots_res.status_code != 200 or vehicles_res.status_code != 200:
        Log("backend", "error", "service", f"API Failure. Depots: {depots_res.status_code}, Vehicles: {vehicles_res.status_code}")
        return None, None
        
    return depots_res.json()['depots'], vehicles_res.json()['vehicles']

def solve_knapsack(capacity, items):
    n = len(items)
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        duration = items[i-1]['Duration']
        impact = items[i-1]['Impact']
        for w in range(capacity + 1):
            if duration <= w:
                dp[i][w] = max(impact + dp[i-1][w-duration], dp[i-1][w])
            else:
                dp[i][w] = dp[i-1][w]
    
    selected = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            selected.append(items[i-1])
            w -= items[i-1]['Duration']
            
    return dp[n][capacity], selected

def run_scheduler():
    Log("backend", "info", "controller", "Starting Vehicle Maintenance Scheduler execution")
    try:
        depots, vehicles = get_scheduler_data()
        if not depots or not vehicles:
            return

        print(f"{'Depot ID':<10} | {'Budget':<10} | {'Max Impact':<12}")
        print("-" * 40)

        for depot in depots:
            budget = depot['MechanicHours']
            max_impact, scheduled_tasks = solve_knapsack(budget, vehicles)
            
            Log("backend", "info", "service", f"Calculated schedule for Depot {depot['ID']}. Impact: {max_impact}")
            
            print(f"{depot['ID']:<10} | {budget:<10} | {max_impact:<12}")
            # Optional: Print first 2 TaskIDs to keep terminal clean for screenshot
            task_ids = [v['TaskID'] for v in scheduled_tasks[:2]]
            print(f"   Tasks: {task_ids} ... (+{len(scheduled_tasks)-2} more)")
        
    except Exception as e:
        Log("backend", "error", "handler", f"Critical failure in scheduler: {str(e)}")

if __name__ == "__main__":
    run_scheduler()