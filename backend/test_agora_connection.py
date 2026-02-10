"""
Test script to verify Agora API connection and credentials
"""
import httpx
import base64
import os
from dotenv import load_dotenv

load_dotenv()

# Get credentials
app_id = os.getenv("AGORA_APP_ID")
customer_id = os.getenv("AGORA_CUSTOMER_ID")
customer_secret = os.getenv("AGORA_CUSTOMER_SECRET")

print(f"Testing Agora API connection...")
print(f"App ID: {app_id[:10]}..." if app_id else "App ID: NOT SET")
print(f"Customer ID: {customer_id[:10]}..." if customer_id else "Customer ID: NOT SET")
print(f"Customer Secret: {'*' * 10}" if customer_secret else "Customer Secret: NOT SET")

if not all([app_id, customer_id, customer_secret]):
    print("\n❌ ERROR: Missing Agora credentials in .env file")
    exit(1)

# Create Basic Auth
credentials = f"{customer_id}:{customer_secret}"
auth_header = base64.b64encode(credentials.encode()).decode()

# Test API connection
base_url = "https://api.agora.io/api/conversational-ai-agent/v2"
url = f"{base_url}/projects/{app_id}/agents"

headers = {
    "Authorization": f"Basic {auth_header}",
    "Content-Type": "application/json"
}

print(f"\nTesting connection to: {url}")

try:
    with httpx.Client(timeout=10.0) as client:
        response = client.get(url, headers=headers)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {response.text[:200]}")
        
        if response.status_code == 200:
            print("\n✅ SUCCESS: Agora API connection working!")
        elif response.status_code == 401:
            print("\n❌ ERROR: Authentication failed. Check your Customer ID and Secret.")
        elif response.status_code == 404:
            print("\n⚠️  WARNING: Endpoint not found. This might be normal if no agents exist yet.")
        else:
            print(f"\n⚠️  WARNING: Unexpected status code: {response.status_code}")
            
except httpx.RequestError as e:
    print(f"\n❌ ERROR: Network error - {e}")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
