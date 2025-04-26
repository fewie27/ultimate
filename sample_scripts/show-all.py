import chromadb
from sentence_transformers import SentenceTransformer
import os
import uuid
from PyPDF2 import PdfReader

# Stelle eine Verbindung zur Chroma-Datenbank her
client = chromadb.Client(chromadb.config.Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="../chroma_data"
))

# Hole oder erstelle die Sammlung 'documents'
collection = client.get_or_create_collection("documents")

# Teste, ob Dokumente vorhanden sind
def get_all_documents():
    # Abfrage der Sammlung, die alle Dokumente enthält
    results = collection.get()
    
    # Überprüfe, ob Ergebnisse vorhanden sind
    if not results['documents']:
        print("Keine Dokumente gefunden.")
        return

    # Ausgabe der Dokumente
    for i, doc in enumerate(results['documents']):
        print(f"Dokument {i + 1}:\n{doc}\n")

if __name__ == "__main__":
    get_all_documents()
