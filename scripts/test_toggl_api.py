#!/usr/bin/env python3
"""
Test Toggl API với Bearer và Basic Auth
"""

import requests
import base64

# Toggl API Token
TOKEN = "2c16d14befa2afbc38f52e596d815391"
TOGGL_API_URL = "https://api.track.toggl.com/api/v9"

# Test 1: Bearer Auth
print("=== TEST 1: Bearer Auth ===")
headers_bearer = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}

url = f"{TOGGL_API_URL}/me/workspaces"
response = requests.get(url, headers=headers_bearer)
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    print(f"✅ Bearer Auth OK! Workspaces: {response.json()}")
else:
    print(f"❌ Bearer Auth FAILED! Error: {response.text}")

print()

# Test 2: Basic Auth
print("=== TEST 2: Basic Auth ===")
auth = base64.b64encode(f"{TOKEN}:api_token".encode()).decode()
headers_basic = {
    "Content-Type": "application/json",
    "Authorization": f"Basic {auth}"
}

response = requests.get(url, headers=headers_basic)
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    print(f"✅ Basic Auth OK! Workspaces: {response.json()}")
else:
    print(f"❌ Basic Auth FAILED! Error: {response.text}")

print()

# Test 3: Toggl API v8 (API cũ)
print("=== TEST 3: Toggl API v8 (API cũ) ===")
TOGGL_API_URL_V8 = "https://api.track.toggl.com/api/v8"
url_v8 = f"{TOGGL_API_URL_V8}/me"
response = requests.get(url_v8, auth=(TOKEN, "api_token"))
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    print(f"✅ API v8 OK! User: {response.json()}")
else:
    print(f"❌ API v8 FAILED! Error: {response.text}")
