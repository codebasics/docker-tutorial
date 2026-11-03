"""
Ingests resolved tickets from data/tickets.db into the 'tickets' Chroma collection (ChromaDB container).
Run once (or after adding new tickets):
    docker compose run --rm rag-app python -m src.ingest.tickets
"""
import os
import sqlite3

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.remote_embeddings import RemoteEmbeddings

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
COLLECTION  = "tickets"
DB_PATH     = os.path.join("data", "tickets.db")


def load_ticket_documents(db_path: str) -> list[Document]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM tickets WHERE status = 'resolved'"
    ).fetchall()
    conn.close()

    docs = []
    for row in rows:
        content = (
            f"Issue: {row['issue_type']}\n"
            f"Description: {row['description']}\n"
            f"Resolution: {row['resolution']}"
        )
        docs.append(Document(
            page_content=content,
            metadata={
                "source":    "ticket",
                "ticket_id": row["ticket_id"],
                "category":  row["category"],
                "status":    row["status"],
            },
        ))
    return docs


def main():
    print("Loading ticket documents from SQLite...")
    docs = load_ticket_documents(DB_PATH)
    print(f"  {len(docs)} resolved tickets loaded.")

    print(f"Connecting to ChromaDB at {CHROMA_HOST}:{CHROMA_PORT}...")
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    embeddings = RemoteEmbeddings()

    print(f"Embedding and storing in collection '{COLLECTION}'...")
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=COLLECTION,
        client=client,
    )
    print(f"  Done. {vectorstore._collection.count()} vectors stored.")


if __name__ == "__main__":
    main()
