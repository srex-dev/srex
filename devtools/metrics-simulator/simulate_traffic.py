import time
import random
import requests
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate traffic to a target endpoint.")
    parser.add_argument('--interval', type=float, default=1.0, help='Interval between requests in seconds (default: 1.0)')
    parser.add_argument('--target', type=str, default='http://localhost:8000', help='Base URL of the target service (default: http://localhost:8000)')
    parser.add_argument('--endpoint', type=str, default='/', help='Endpoint to hit (default: /)')
    parser.add_argument('--method', type=str, choices=['GET', 'POST', 'RANDOM'], default='RANDOM', help='HTTP method to use (GET, POST, or RANDOM; default: RANDOM)')
    parser.add_argument('--count', type=int, default=None, help='Number of requests to send (default: infinite)')
    args = parser.parse_args()

    BASE_URL = args.target
    ENDPOINT = args.endpoint
    INTERVAL = args.interval
    METHOD = args.method
    COUNT = args.count

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

    sent = 0
    while True:
        if METHOD == 'RANDOM':
            method = random.choice(['GET', 'POST'])
        else:
            method = METHOD
        simulate_request(method)
        sent += 1
        if COUNT is not None and sent >= COUNT:
            break
        time.sleep(INTERVAL)