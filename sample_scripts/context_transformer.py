import torch
import torch.nn as nn
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer

# 1. Device automatisch wählen
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print(f"Using device: {device}")

# 2. SentenceTransformer Modell laden (bleibt intern meist auf CPU, ist ok)
sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

# 3. Combiner-Netzwerk definieren
class Combiner(nn.Module):
    def __init__(self, embedding_dim):
        super().__init__()
        self.fc1 = nn.Linear(embedding_dim * 2, embedding_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(embedding_dim, embedding_dim)

    def forward(self, sentence_embedding, context_embedding):
        combined = torch.cat([sentence_embedding, context_embedding], dim=-1)
        x = self.fc1(combined)
        x = self.relu(x)
        x = self.fc2(x)
        return x

# 4. Combiner initialisieren und auf Device verschieben
combiner = Combiner(embedding_dim=sentence_model.get_sentence_embedding_dimension()).to(device)

# 5. Beispieltext
sentence = "Die Katze schläft auf dem Sofa."
context = "Es war ein sonniger Nachmittag. Die Katze schläft auf dem Sofa. Draußen spielten Kinder."

# 6. Embeddings erstellen (SentenceTransformer produziert erstmal CPU-Tensoren)
sentence_embedding = sentence_model.encode(sentence, convert_to_tensor=True).to(device)
context_embedding = sentence_model.encode(context, convert_to_tensor=True).to(device)

# 7. Finales Kontext-Embedding berechnen
final_embedding = combiner(sentence_embedding, context_embedding)

# 8. Ausgabe
cosine_sim = F.cosine_similarity(final_embedding, sentence_embedding, dim=0)
euclidean_dist = torch.norm(final_embedding - sentence_embedding, p=2)

# 9. Ausgabe
print(f"Final Embedding Shape: {final_embedding.shape}")
print(f"Cosine Similarity: {cosine_sim.item():.4f}")  # 1.0 = exakt gleich
print(f"Euclidean Distance: {euclidean_dist.item():.4f}")  # 0.0 = exakt gleich
