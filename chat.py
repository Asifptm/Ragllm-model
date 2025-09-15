# chat.py - Perplexity-style Chat Interface
import os
from bson import ObjectId
from dotenv import load_dotenv
from openai import OpenAI
from data import DataService

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY in .env")

client = OpenAI(api_key=OPENAI_API_KEY)
service = DataService(k=5)

USER_ID = "1234567890abcdef12345678"
SESSION_ID = ObjectId()

def generate_related_prompts(query: str, answer: str) -> list:
    prompt = f"""
The user asked: "{query}"
You answered: "{answer}"

Now suggest 3-5 related follow-up questions the user might naturally ask next,
short and conversational, without answers.
"""
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=150
    )
    suggestions = resp.choices[0].message.content.strip().split("\n")
    suggestions = [s.lstrip(" -0123456789.").strip() for s in suggestions if s.strip()]
    return suggestions

def ask_perplexity_style(query: str) -> dict:
    service.clear_sources()
    kb_tool, web_tool = service.get_tools()
    kb_context = kb_tool.func(query)
    web_context = web_tool.func(query)

    system_prompt = "You are an AI assistant like Perplexity.ai. Always be clear, concise, and cite sources when relevant."
    user_prompt = f"""Question: {query}

Knowledge Base Context:
{kb_context or 'No KB results.'}

Web Context:
{web_context or 'No web results.'}

Answer naturally and comprehensively.
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=800,
    )

    answer = response.choices[0].message.content.strip()
    sources = service.get_sources()
    related = generate_related_prompts(query, answer)
    service.save_chat(query, answer, USER_ID, SESSION_ID)

    return {"query": query, "answer": answer, "sources": sources, "related_prompts": related}

if __name__ == "__main__":
    print("💬 Perplexity-Style Chat (Ctrl+C to exit)")
    try:
        while True:
            q = input("\nYou: ").strip()
            if not q:
                continue
            result = ask_perplexity_style(q)
            print("\n🤖 Assistant:", result["answer"])

            # Knowledge base sources
            if result["sources"]["knowledge_base"]:
                print("\n📚 Knowledge Base Sources:")
                for s in result["sources"]["knowledge_base"]:
                    print(" -", s)

            # Categorized web sources
            if result["sources"]["web"]:
                print("\n🌍 Web Sources:")
                for cat, links in result["sources"]["web"].items():
                    if links:
                        print(f"  🔹 {cat}:")
                        for l in links:
                            print("   -", l)

            # Related prompts
            if result["related_prompts"]:
                print("\n💡 Related Prompts:")
                for rp in result["related_prompts"]:
                    print(" -", rp)

    except KeyboardInterrupt:
        print("\nExiting chat...")
        service.close_connection()
