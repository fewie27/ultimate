import chromadb
from sentence_transformers import SentenceTransformer
import uuid

# 1. Setup: ChromaDB & Embedding-Modell
client = chromadb.Client()
collection = client.get_or_create_collection("test_saetze")

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# 2. Beispiel-Sätze definieren
sätze = [
    "Die Kündigung ist nur zum Monatsende möglich.",
    "Man darf den Vertrag jeweils zum Quartal beenden.",
    "Der Vertrag endet automatisch nach einem Jahr.",
    "Ein Rücktritt ist nur schriftlich gültig.",
    "Verträge können jederzeit mit einer Frist von vier Wochen gekündigt werden."
]

# 3. Embeddings erzeugen & einfügen
embeddings = model.encode(sätze)

for satz, emb in zip(sätze, embeddings):
    collection.add(
        documents=[satz],
        embeddings=[emb.tolist()],
        ids=[str(uuid.uuid4())],
        metadatas=[{"info": "Beispiel"}]
    )

# 4. Suchanfrage definieren
query = "Wie lange ist die Kündigungsfrist?"

# 5. Embedding für die Anfrage erzeugen
query_embedding = model.encode([query])[0].tolist()

# 6. Suche durchführen
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)

# 7. Ergebnisse ausgeben
print("\n🔍 Ähnliche Sätze zur Anfrage:")
for doc, dist in zip(results["documents"][0], results["distances"][0]):
    print(f" - {doc} (Distanz: {dist:.4f})")

