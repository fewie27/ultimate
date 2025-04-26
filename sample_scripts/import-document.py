import chromadb
from sentence_transformers import SentenceTransformer
import os
import uuid
from PyPDF2 import PdfReader

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.Client(chromadb.config.Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="../chroma_data"
))
collection = client.get_or_create_collection("documents")

def chunk_text(text, max_length=500):
    words = text.split()
    for i in range(0, len(words), max_length):
        yield " ".join(words[i:i + max_length])

def import_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    for chunk in chunk_text(text):
        embedding = model.encode([chunk])[0].tolist()
        print(chunk)
        collection.add(
            documents=[chunk],
            embeddings=[embedding],
            ids=[str(uuid.uuid4())],
            metadatas=[{"source": pdf_path}]
        )
    exit()
    client.persist()
    print(f"✅ Import abgeschlossen für {pdf_path}")

import_pdf("/documents/Bewilligung.pdf")
