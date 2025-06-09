
import requests
import time
import random

url = "http://localhost:8000/api"

while True:
    try:
        response = requests.get(url)
        print(f"{response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(random.uniform(0.5, 2.0))  # Simulate human-ish traffic