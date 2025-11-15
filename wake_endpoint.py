#!/usr/bin/env python3
"""
Quick script to wake up the RunPod endpoint!
This sends a simple request to activate the workers.
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

print("🌟 Sending wake-up request to RunPod endpoint...")
print(f"Endpoint ID: {ENDPOINT_ID}")

url = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/run"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Send a minimal workflow just to wake up the workers
payload = {
    "input": {
        "workflow": {}
    }
}

try:
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    print(f"\n✅ Response Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"📦 Response: {json.dumps(data, indent=2)}")

        if "id" in data:
            job_id = data["id"]
            print(f"\n🎯 Job started! ID: {job_id}")
            print("Workers are waking up! This might take 30-60 seconds the first time.")
            print("Try your website again in a minute!")
        elif data.get("status") == "IN_QUEUE":
            print("\n⏳ Job is in queue - workers are starting up!")
            print("Give it 30-60 seconds and try again!")
    else:
        print(f"❌ Error: {response.text}")

except Exception as e:
    print(f"❌ Error: {e}")
