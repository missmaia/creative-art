#!/usr/bin/env python3
"""
Script to add workers to RunPod endpoint using GraphQL API
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load API credentials from .env file
load_dotenv()

API_KEY = os.getenv("RUNPOD_API_KEY")
ENDPOINT_ID = os.getenv("RUNPOD_ENDPOINT_ID")

if not API_KEY or not ENDPOINT_ID:
    print("❌ Error: RUNPOD_API_KEY or RUNPOD_ENDPOINT_ID not found in .env file!")
    print("Please create a .env file with your RunPod credentials.")
    exit(1)

print("🔧 Trying to add workers to your endpoint...")
print(f"Endpoint ID: {ENDPOINT_ID}\n")

# GraphQL mutation to update endpoint
# This tries to set min workers to 1, max workers to 3
mutation = """
mutation {
  updateEndpoint(input: {
    endpointId: "%s"
    workersMin: 1
    workersMax: 3
  }) {
    id
    workersMin
    workersMax
  }
}
""" % ENDPOINT_ID

url = "https://api.runpod.io/graphql"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {"query": mutation}

try:
    print("📡 Sending request to RunPod...")
    response = requests.post(url, json=payload, headers=headers, timeout=30)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Response:")
        print(json.dumps(data, indent=2))

        if "errors" in data:
            print("\n❌ GraphQL returned errors:")
            print(json.dumps(data["errors"], indent=2))
            print("\n😞 The API doesn't allow changing workers this way.")
            print("You'll need to do it in the RunPod console website.")
        elif "data" in data and data["data"]:
            print("\n🎉 SUCCESS! Workers should be starting up!")
            print("Wait 30-60 seconds and try your website!")
        else:
            print("\n🤔 Unexpected response format")
    else:
        print(f"\n❌ Error: {response.text}")
        print("\n😞 Couldn't change workers via API.")
        print("You need to use the RunPod website console.")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\n😞 The API method didn't work.")
    print("We need to use the RunPod website to turn on workers.")
