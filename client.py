"""Client for CMPE 273 Lab 6.

Sends a request to the Inventory Service every two seconds and prints
which Pod served it. The client talks to the Kubernetes Service name
"inventory", never to a Pod address, so it keeps working when Pods
fail readiness or get replaced. Uses only the Python standard library.
"""

import json
import time
import urllib.error
import urllib.request
from datetime import datetime

SERVICE_URL = "http://inventory:5000/items"


def main():
    print(f"[client] Sending requests to {SERVICE_URL}", flush=True)
    while True:
        try:
            with urllib.request.urlopen(SERVICE_URL, timeout=5) as response:
                data = json.loads(response.read())
            stamp = datetime.now().isoformat(timespec="seconds")
            print(f"[client] {stamp} served by {data['pod']}: {data['items']}",
                  flush=True)
        except Exception as exc:
            print(f"[client] Request failed: {exc}", flush=True)
        time.sleep(2)


if __name__ == "__main__":
    main()
