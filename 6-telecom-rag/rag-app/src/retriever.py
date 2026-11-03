"""
Builds a merged retriever across all three Chroma collections:
  - faq     : FAQ entries (no chunking — 1 row = 1 doc)
  - tickets : resolved support tickets (no chunking — 1 ticket = 1 doc)
  - guides  : PDF guide chunks (RecursiveCharacterTextSplitter applied at ingest)

Collections live in the ChromaDB container, reached over HTTP.
"""
import os

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda

from remote_embeddings import RemoteEmbeddings

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))


def _chroma_client() -> chromadb.HttpClient:
    return chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)


def build_retriever(
    k_faq: int = 3,
    k_tickets: int = 3,
    k_guides: int = 3,
) -> RunnableLambda:
    embeddings = RemoteEmbeddings()
    client = _chroma_client()

    faq_store     = Chroma(client=client, collection_name="faq",     embedding_function=embeddings)
    tickets_store = Chroma(client=client, collection_name="tickets", embedding_function=embeddings)
    guides_store  = Chroma(client=client, collection_name="guides",  embedding_function=embeddings)

    faq_retriever     = faq_store.as_retriever(search_kwargs={"k": k_faq})
    tickets_retriever = tickets_store.as_retriever(search_kwargs={"k": k_tickets})
    guides_retriever  = guides_store.as_retriever(search_kwargs={"k": k_guides})

    def retrieve(query: str) -> list[Document]:
        return (
            faq_retriever.invoke(query)
            + tickets_retriever.invoke(query)
            + guides_retriever.invoke(query)
        )

    return RunnableLambda(retrieve)
