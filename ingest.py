import os
import json
import tempfile
import uuid
from typing import List, Optional
import boto3
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

# -------------------------
# Load environment variables
# -------------------------
load_dotenv()

# --- Mongo ---
MONGO_URI: Optional[str] = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
MONGO_DB_NAME: Optional[str] = os.getenv("MONGO_DB_NAME") or os.getenv("DATABASE_NAME")
MONGO_COLLECTION_NAME: Optional[str] = os.getenv("MONGO_COLLECTION_NAME") or os.getenv("COLLECTION_NAME")

# --- S3 ---
S3_BUCKET_NAME: Optional[str] = os.getenv("S3_BUCKET_NAME")
S3_PREFIX: str = os.getenv("S3_PREFIX", "")
AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION: Optional[str] = os.getenv("AWS_REGION")

# --- Embeddings ---
OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")

# --- Chunking ---
CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 200))

# -------------------------
# Helpers
# -------------------------

def get_mongo_collection():
    if not MONGO_URI:
        raise ValueError("MongoDB connection string not provided. Set MONGO_URI or MONGODB_URI in .env")
    if not MONGO_DB_NAME or not MONGO_COLLECTION_NAME:
        raise ValueError("Mongo DB/collection not provided. Set MONGO_DB_NAME and MONGO_COLLECTION_NAME in .env")
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    return db[MONGO_COLLECTION_NAME]


def extract_text_from_record(obj) -> str:
    if isinstance(obj, dict):
        if "text" in obj and isinstance(obj["text"], str):
            return obj["text"]
        for v in obj.values():
            t = extract_text_from_record(v)
            if t:
                return t
    elif isinstance(obj, list):
        for item in obj:
            t = extract_text_from_record(item)
            if t:
                return t
    elif isinstance(obj, str):
        return obj
    return ""



def load_s3_json_documents(bucket: str, prefix: str) -> List[Document]:
    if not bucket:
        return []
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )

    docs: List[Document] = []
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    for obj in response.get("Contents", []):
        key = obj["Key"]
        if not key.lower().endswith(".json"):
            continue

        tmp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.json")
        s3.download_file(bucket, key, tmp_path)
        try:
            with open(tmp_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            text = extract_text_from_record(data).strip()
            if text:
                docs.append(Document(page_content=text, metadata={"origin": "s3", "s3_key": key}))
        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass
    print(f"S3: loaded {len(docs)} docs")
    return docs


def load_mongodb_documents() -> List[Document]:
    if not MONGO_URI or not MONGO_DB_NAME or not MONGO_COLLECTION_NAME:
        return []

    coll = get_mongo_collection()
    docs: List[Document] = []
    for rec in coll.find({}):
        text = rec.get("text")
        if not text:
            text = extract_text_from_record(rec)
        text = (text or "").strip()
        if not text:
            continue

        meta = {k: v for k, v in rec.items() if k != "text"}
        if "_id" in meta:
            meta["_id"] = str(meta["_id"])
        docs.append(Document(page_content=text, metadata=meta))

    print(f"MongoDB: loaded {len(docs)} docs from {MONGO_DB_NAME}.{MONGO_COLLECTION_NAME}")
    return docs



def ingest_data_to_vector_store():
    s3_docs = load_s3_json_documents(S3_BUCKET_NAME, S3_PREFIX)
    mongo_docs = load_mongodb_documents()
    all_docs = s3_docs + mongo_docs

    if not all_docs:
        print("No documents to ingest. Exiting.")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = splitter.split_documents(all_docs)

    if not chunks:
        print("No chunks created. Exiting.")
        return

    texts: List[str] = []
    metadatas: List[dict] = []
    ids: List[str] = []

    for i, ch in enumerate(chunks):
        if not ch.page_content.strip():
            continue
        md = dict(ch.metadata or {})
        _id = str(uuid.uuid4())
        md["chunk_id"] = _id
        texts.append(ch.page_content)
        metadatas.append(md)
        ids.append(_id)

    if not texts:
        print("No valid texts to embed. Exiting.")
        return

    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not set in environment.")

    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, openai_api_key=OPENAI_API_KEY)
    collection = get_mongo_collection()

    for text, md, _id in zip(texts, metadatas, ids):
        embedding_vector = embeddings.embed_query(text)
        record = {
            "_id": _id,
            "text": text,
            "embedding": embedding_vector,
            "model_version": EMBEDDING_MODEL,
            "metadata": md,
        }
        collection.update_one({"_id": _id}, {"$set": record}, upsert=True)

    print("✅ Ingestion complete. Embeddings upserted into MongoDB Atlas.")


if __name__ == "__main__":
    ingest_data_to_vector_store()
