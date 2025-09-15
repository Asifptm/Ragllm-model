#!/usr/bin/env python3
"""
Quick test script for the RAG Chat API
Simple one-liner testing without interactive mode
"""

import requests
import json

def test_query(query: str):
    """Test a single query against the API"""
    try:
        # Send chat request
        response = requests.post(
            "http://localhost:8000/chat",
            json={"query": query},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Query: {result['query']}")
            print(f"Answer: {result['answer']}")
            
            # Get sources
            sources_response = requests.get("http://localhost:8000/websource")
            if sources_response.status_code == 200:
                sources = sources_response.json()['sources']
                if sources:
                    print(f"\nSources found: {len(sources.get('knowledge_base', []))} KB, {len(sources.get('web', []))} web")
            
            # Get related prompts
            related_response = requests.get("http://localhost:8000/related")
            if related_response.status_code == 200:
                related = related_response.json()['related_prompts']
                if related:
                    print(f"Related prompts: {len(related)}")
            
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        test_query(query)
    else:
        test_query("What is Retrieval-Augmented Generation?")
