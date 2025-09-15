#!/usr/bin/env python3
"""
Interactive test script for the RAG Chat API
Allows users to test queries against the running FastAPI server
"""

import requests
import json
import sys
from typing import Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:8000"

def test_health() -> bool:
    """Test if the API server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running!")
            print(f"   Status: {response.json()}")
            return True
        else:
            print(f"❌ API server returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API server: {e}")
        print("   Make sure the server is running with: uvicorn api:app --host 0.0.0.0 --port 8000 --reload")
        return False

def send_chat_query(query: str) -> Dict[str, Any]:
    """Send a chat query to the API"""
    try:
        payload = {"query": query}
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ API returned status {response.status_code}: {response.text}")
            return {}
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending request: {e}")
        return {}

def get_web_sources() -> Dict[str, Any]:
    """Get web sources from the last query"""
    try:
        response = requests.get(f"{API_BASE_URL}/websource", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"sources": {}}
    except requests.exceptions.RequestException:
        return {"sources": {}}

def get_related_prompts() -> Dict[str, Any]:
    """Get related prompts from the last query"""
    try:
        response = requests.get(f"{API_BASE_URL}/related", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"related_prompts": []}
    except requests.exceptions.RequestException:
        return {"related_prompts": []}

def display_answer(result: Dict[str, Any]):
    """Display the chat answer in a formatted way"""
    if not result:
        return
    
    print("\n" + "="*60)
    print("🤖 RAG CHAT RESPONSE")
    print("="*60)
    print(f"Query: {result.get('query', 'N/A')}")
    print("\nAnswer:")
    print("-" * 40)
    print(result.get('answer', 'No answer received'))
    print("-" * 40)

def display_sources(sources_data: Dict[str, Any]):
    """Display web sources in a formatted way"""
    sources = sources_data.get('sources', {})
    if not sources:
        print("\n📚 No sources available")
        return
    
    print("\n📚 SOURCES")
    print("="*60)
    
    # Display knowledge base sources
    kb_sources = sources.get('knowledge_base', [])
    if kb_sources:
        print("📖 Knowledge Base Sources:")
        for i, source in enumerate(kb_sources[:5], 1):  # Limit to 5 sources
            print(f"  {i}. {source.get('title', 'Untitled')}")
            if source.get('url'):
                print(f"     URL: {source['url']}")
        print()
    
    # Display web sources
    web_sources = sources.get('web', [])
    if web_sources:
        print("🌐 Web Sources:")
        for i, source in enumerate(web_sources[:5], 1):  # Limit to 5 sources
            print(f"  {i}. {source.get('title', 'Untitled')}")
            if source.get('url'):
                print(f"     URL: {source['url']}")
        print()

def display_related_prompts(related_data: Dict[str, Any]):
    """Display related prompts in a formatted way"""
    prompts = related_data.get('related_prompts', [])
    if not prompts:
        print("\n💡 No related prompts available")
        return
    
    print("\n💡 RELATED PROMPTS")
    print("="*60)
    for i, prompt in enumerate(prompts, 1):
        print(f"  {i}. {prompt}")
    print()

def interactive_mode():
    """Run interactive chat mode"""
    print("\n🚀 Starting Interactive RAG Chat Test")
    print("="*60)
    print("Type your questions and press Enter to get AI responses.")
    print("Commands:")
    print("  - Type 'quit', 'exit', or 'q' to exit")
    print("  - Type 'sources' to see sources from last query")
    print("  - Type 'related' to see related prompts from last query")
    print("  - Type 'health' to check API status")
    print("="*60)
    
    while True:
        try:
            # Get user input
            user_input = input("\n💬 Your question: ").strip()
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            elif user_input.lower() == 'sources':
                sources_data = get_web_sources()
                display_sources(sources_data)
                continue
            elif user_input.lower() == 'related':
                related_data = get_related_prompts()
                display_related_prompts(related_data)
                continue
            elif user_input.lower() == 'health':
                test_health()
                continue
            elif not user_input:
                print("Please enter a question or command.")
                continue
            
            # Send chat query
            print(f"\n🔄 Processing: {user_input}")
            result = send_chat_query(user_input)
            
            if result:
                display_answer(result)
                
                # Ask if user wants to see sources and related prompts
                show_extras = input("\n❓ Show sources and related prompts? (y/n): ").strip().lower()
                if show_extras in ['y', 'yes']:
                    sources_data = get_web_sources()
                    display_sources(sources_data)
                    
                    related_data = get_related_prompts()
                    display_related_prompts(related_data)
            else:
                print("❌ Failed to get response from API")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

def single_query_mode(query: str):
    """Run a single query and display results"""
    print(f"\n🔄 Processing: {query}")
    result = send_chat_query(query)
    
    if result:
        display_answer(result)
        
        # Get and display sources
        sources_data = get_web_sources()
        display_sources(sources_data)
        
        # Get and display related prompts
        related_data = get_related_prompts()
        display_related_prompts(related_data)
    else:
        print("❌ Failed to get response from API")

def main():
    """Main function"""
    print("🧪 RAG Chat API Test Client")
    print("="*60)
    
    # Test API health first
    if not test_health():
        sys.exit(1)
    
    # Check if query provided as command line argument
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        single_query_mode(query)
    else:
        interactive_mode()

if __name__ == "__main__":
    main()
