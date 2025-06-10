import time
import random
import requests

BASE_URL = "http://localhost:8000"
METHODS = ["GET", "POST"]
ENDPOINT = "/checkout"  # This matches your Flask route for checkout-service

def simulate_request(method):
    url = f"{BASE_URL}{ENDPOINT}"
    try:
        if method == "GET":
            response = requests.get(url)
        else:
            response = requests.post(url, data={"sample": "data"})
        print(f"{method} {url} → {response.status_code}")
    except Exception as e:
        print(f"{method} {url} → ERROR: {e}")

if __name__ == "__main__":
    while True:
        method = random.choice(METHODS)

        # 10% chance to simulate an unreachable request
        if random.random() < 0.1:
            simulate_request(method)  # still uses valid endpoint but could fail randomly
        else:
            simulate_request(method)

        time.sleep(random.uniform(0.3, 1.0))