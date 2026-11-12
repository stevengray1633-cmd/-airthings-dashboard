
import os
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone

CLIENT_ID = os.environ["AIRTHINGS_CLIENT_ID"]
CLIENT_SECRET = os.environ["AIRTHINGS_CLIENT_SECRET"]

TOKEN_URL = "https://accounts-api.airthings.com/v1/token"
API_URL = "https://ext-api.airthings.com/v1"

DEVICES = {
    "2930125849": "Airthings 1 DFX",
    "2960180535": "DH MFRs",
    "2960194763": "View Plus DFX"
}

def request_json(url, data=None, headers=None):
    request = urllib.request.Request(
        url,
        data=data,
        headers=headers or {}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)

def get_token():
    data = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "read:device:current_values"
    }).encode()

    response = request_json(
        TOKEN_URL,
        data=data,
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )
    return response["access_token"]

def get_device_readings(device_id, token):
    return request_json(
        f"{API_URL}/devices/{device_id}/latest-samples",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
    )

def main():
    token = get_token()
    output = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "devices": {}
    }

    for device_id, name in DEVICES.items():
        print(f"Retrieving readings for {name}")
        try:
            readings = get_device_readings(device_id, token)
            output["devices"][device_id] = {
                "name": name,
                "readings": readings
            }
        except Exception as error:
            print(f"Error retrieving {name}: {error}")
            raise

    with open("airthings-data.json", "w", encoding="utf-8") as file:
        json.dump(output, file, indent=2)

    print("Airthings data file created successfully")

if __name__ == "__main__":
    main()
