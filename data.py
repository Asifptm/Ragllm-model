# data.py - Data Flow and Database Operations
# Handles MongoDB connections, retrievers, and data management

import os
from typing import List, Dict, Any
from datetime import datetime
from urllib.parse import urlparse

from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.tools import Tool
from langchain_community.utilities import GoogleSerperAPIWrapper
from pydantic import Field

# =========================
# Environment & Config
# =========================
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME") or os.getenv("DATABASE_NAME")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME") or os.getenv("COLLECTION_NAME")
MONGO_VECTOR_INDEX_NAME = os.getenv("MONGO_VECTOR_INDEX_NAME", "vector_index")
MONGO_HISTORY_COLLECTION_NAME = os.getenv("MONGO_HISTORY_COLLECTION_NAME", "chathistory")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not MONGO_URI or not MONGO_DB_NAME or not MONGO_COLLECTION_NAME:
    raise ValueError("Missing MongoDB connection settings in .env (MONGO_URI/MONGO_DB_NAME/MONGO_COLLECTION_NAME)")
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY in .env")

# =========================
# MongoDB Operations
# =========================

def get_mongo_client() -> MongoClient:
    return MongoClient(MONGO_URI)

def get_collections(client: MongoClient):
    db = client[MONGO_DB_NAME]
    return db[MONGO_COLLECTION_NAME], db[MONGO_HISTORY_COLLECTION_NAME]

def save_chat_history(history_col, query: str, answer: str, *, user_id: str, session_id: ObjectId, status: str = "completed") -> None:
    doc = {
        "attachments": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "query": query,
        "response": answer,
        "role": "assistant",
        "session_id": session_id,
        "status": status,
        "text": answer,
        "user_id": ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id,
    }
    history_col.insert_one(doc)

# =========================
# Categorizer for links
# =========================
def categorize_link(url: str) -> str:
    """Intelligently categorize links by domain & heuristics."""
    url = url.lower()
    domain = urlparse(url).netloc

    # Social Media
    if any(s in domain for s in [
        "twitter.com", "x.com", "facebook.com", "instagram.com",
        "tiktok.com", "linkedin.com", "reddit.com", "youtube.com",
        "quora.com", "pinterest.com", "yandex.ru",
    ]):
        return "Social Media"

    # Blogs
    if any(b in domain for b in [
        "medium.com", "substack.com", "wordpress.com", "blogspot.com",
        "ghost.io", "hashnode.com", "dev.to"
    ]) or "blog" in domain:
        return "Blogs"

    # News
    if any(n in domain for n in [
        "nytimes.com", "bbc.com", "cnn.com", "reuters.com", "bloomberg.com",
        "forbes.com", "theguardian.com", "washingtonpost.com",
        "wired.com", "techcrunch.com", "theverge.com"
    ]) or "news" in domain:
        return "News"

    # Academic / Research
    if any(a in domain for a in [
        "arxiv.org", "researchgate.net", "springer.com",
        "sciencedirect.com", "acm.org", "ieee.org"
    ]) or domain.endswith(".edu"):
        return "Academic / Research"

    # Government / Org
    if domain.endswith(".gov") or domain.endswith(".int") or any(g in domain for g in ["who.int", "un.org", "nasa.gov", "europa.eu", "worldbank.org"]):
        return "Government / Organization"

    # E-commerce
    if any(e in domain for e in [
        "amazon.com", "flipkart.com", "ebay.com", "walmart.com", "aliexpress.com"
    ]) or "shop" in domain or "store" in domain:
        return "E-commerce"

    # Technical Docs
    if any(t in domain for t in [
        "github.com", "gitlab.com", "readthedocs.io", "stackoverflow.com",
        "docs.python.org"
    ]) or "docs" in domain:
        return "Technical Docs"

    return "Others"

# =========================
# MongoDB Retriever
# =========================
class MongoDBRetriever(BaseRetriever):
    collection: Any = Field(...)
    embeddings: OpenAIEmbeddings = Field(...)
    index_name: str = Field(...)
    k: int = Field(default=5)

    def _get_relevant_documents(self, query: str) -> List[Document]:
        query_vector = self.embeddings.embed_query(query)
        pipeline = [
            {
                "$vectorSearch": {
                    "index": self.index_name,
                    "path": "embedding",
                    "queryVector": query_vector,
                    "numCandidates": 100,
                    "limit": self.k,
                }
            }
        ]
        results = self.collection.aggregate(pipeline)
        docs: List[Document] = []
        for r in results:
            docs.append(
                Document(
                    page_content=r.get("text", ""),
                    metadata={
                        "source": r.get("video_url") or r.get("source") or "MongoDB",
                        "chunk_index": r.get("chunk_index"),
                        "created_at": r.get("created_at"),
                        "post_id": r.get("post_id"),
                        "_id": str(r.get("_id")),
                    },
                )
            )
        return docs

# =========================
# Source Collector
# =========================
class SourceCollector:
    def __init__(self):
        self.kb_sources: List[str] = []
        self.web_sources: Dict[str, List[str]] = {
            "Social Media": [],
            "Blogs": [],
            "News": [],
            "Academic / Research": [],
            "Government / Organization": [],
            "E-commerce": [],
            "Technical Docs": [],
            "Others": []
        }

    def add_kb(self, sources: List[str]):
        self.kb_sources.extend([s for s in sources if s])

    def add_web(self, sources: List[str]):
        for s in sources:
            if not s:
                continue
            category = categorize_link(s)
            self.web_sources[category].append(s)

    def merged(self) -> Dict[str, Any]:
        deduped_web = {}
        for cat, links in self.web_sources.items():
            seen = set()
            deduped_web[cat] = []
            for l in links:
                if l not in seen:
                    deduped_web[cat].append(l)
                    seen.add(l)
        return {
            "knowledge_base": list(dict.fromkeys(self.kb_sources)),
            "web": deduped_web
        }

    def clear(self):
        self.kb_sources.clear()
        for cat in self.web_sources:
            self.web_sources[cat].clear()

# =========================
# Tool Functions
# =========================
def create_kb_tool(retriever: MongoDBRetriever, collector: SourceCollector) -> Tool:
    def kb_tool_func(q: str) -> str:
        docs = retriever.get_relevant_documents(q)
        sources = [d.metadata.get("source") for d in docs]
        collector.add_kb(sources)
        joined = "\n\n".join([d.page_content for d in docs if d.page_content])
        return joined or ""
    return Tool(name="KB_Search", func=kb_tool_func, description="Retrieve facts from MongoDB knowledge base.")

def create_web_tool(collector: SourceCollector) -> Tool:
    serper = GoogleSerperAPIWrapper(serper_api_key=SERPER_API_KEY)
    def web_tool_func(q: str) -> str:
        results = serper.results(q)
        organic = results.get("organic", []) if isinstance(results, dict) else []
        links = [item.get("link") for item in organic if item.get("link")]
        snippets = [item.get("snippet") or item.get("title") for item in organic]
        collector.add_web(links)
        return "\n".join([s for s in snippets if s])[:4000]
    return Tool(name="Web_Search", func=web_tool_func, description="Retrieve info from the public web via Serper.")

# =========================
# Data Service
# =========================
class DataService:
    def __init__(self, k: int = 5):
        self.k = k
        self.client = get_mongo_client()
        self.kb_col, self.history_col = get_collections(self.client)
        self.embeddings = OpenAIEmbeddings()
        self.retriever = MongoDBRetriever(collection=self.kb_col, embeddings=self.embeddings, index_name=MONGO_VECTOR_INDEX_NAME, k=k)
        self.collector = SourceCollector()

    def get_tools(self) -> List[Tool]:
        return [create_kb_tool(self.retriever, self.collector), create_web_tool(self.collector)]

    def save_chat(self, query: str, answer: str, user_id: str, session_id: ObjectId, status: str = "completed"):
        save_chat_history(self.history_col, query=query, answer=answer, user_id=user_id, session_id=session_id, status=status)

    def get_sources(self) -> Dict[str, Any]:
        return self.collector.merged()

    def clear_sources(self):
        self.collector.clear()

    def close_connection(self):
        if self.client:
            self.client.close()
