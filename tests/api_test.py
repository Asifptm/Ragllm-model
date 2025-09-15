#!/usr/bin/env python3
"""
Direct API testing script - shows raw API responses without user interaction
"""

import requests
import json
import sys

API_BASE_URL = "http://localhost:8000"

def test_health():
    """Test API health endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        print("=== HEALTH CHECK ===")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_chat_api(query: str):
    """Test chat endpoint with raw response"""
    try:
        payload = {"query": query}
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print("=== CHAT API RESPONSE ===")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Chat API failed: {e}")
        return False

def test_websource_api():
    """Test websource endpoint with raw response"""
    try:
        response = requests.get(f"{API_BASE_URL}/websource", timeout=10)
        
        print("=== WEBSOURCE API RESPONSE ===")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Websource API failed: {e}")
        return False

def test_related_api():
    """Test related endpoint with raw response"""
    try:
        response = requests.get(f"{API_BASE_URL}/related", timeout=10)
        
        print("=== RELATED API RESPONSE ===")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Related API failed: {e}")
        return False

def run_all_tests(query: str = "What is Retrieval-Augmented Generation?"):
    """Run all API tests in sequence"""
    print("🧪 RAG API Direct Testing")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("❌ API server not available")
        return
    
    print("\n")
    
    # Test chat
    if test_chat_api(query):
        print("\n")
        
        # Test websource (depends on chat)
        test_websource_api()
        print("\n")
        
        # Test related (depends on chat)
        test_related_api()
    
    print("\n" + "=" * 50)
    print("✅ API testing completed")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        run_all_tests(query)
    else:
        run_all_tests()
