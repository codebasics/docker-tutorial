"""
Ingests data/telecom_guide.pdf into the 'guides' Chroma collection (ChromaDB container).
Applies RecursiveCharacterTextSplitter to break the long document into chunks.
Run once (or after regenerating the PDF):
    docker compose run --rm rag-app python -m src.ingest.pdf
"""
import os

import chromadb
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.remote_embeddings import RemoteEmbeddings

CHROMA_HOST   = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT   = int(os.getenv("CHROMA_PORT", "8000"))
COLLECTION    = "guides"
PDF_PATH      = os.path.join("data", "telecom_guide.pdf")
CHUNK_SIZE    = 600
CHUNK_OVERLAP = 100


def main():
    print("Loading PDF...")
    loader = PyPDFLoader(PDF_PATH)
    pages = loader.load()
    print(f"  {len(pages)} pages loaded.")

    print(f"Chunking (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " "],
    )
    chunks = splitter.split_documents(pages)

    for i, chunk in enumerate(chunks):
        chunk.metadata["source"] = "guide"
        chunk.metadata["chunk_index"] = i

    print(f"  {len(chunks)} chunks produced.")

    print(f"Connecting to ChromaDB at {CHROMA_HOST}:{CHROMA_PORT}...")
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    embeddings = RemoteEmbeddings()

    print(f"Embedding and storing in collection '{COLLECTION}'...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION,
        client=client,
    )
    print(f"  Done. {vectorstore._collection.count()} vectors stored.")


if __name__ == "__main__":
    main()
