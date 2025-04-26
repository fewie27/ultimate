import os
import uuid
import logging
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
import nltk

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download necessary NLTK data for sentence tokenization
try:
    nltk.download('punkt', quiet=True)
except Exception as e:
    logger.error(f"Error downloading NLTK data: {e}")

class RentalAnalysis:
    """
    A class to analyze rental agreements using vector embeddings.
    Creates and manages two collections:
    1. minimal_requirements - Contains minimal requirements for a valid rental agreement
    2. sample_agreement - Contains a sample rental agreement for comparison
    """
    
    def __init__(self):
        # Create directory for ChromaDB data
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'chroma_data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = PersistentClient(path=data_dir)

        
        # Initialize sentence embedding model
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        
        # Create collections
        self.minimal_requirements = self.client.get_or_create_collection("minimal_requirements")
        self.sample_agreement = self.client.get_or_create_collection("sample_agreement")
        
        # Populate collections if they're empty
        self._initialize_collections()
        
        logger.info("Rental agreement analysis initialized")
    
    def _initialize_collections(self):
        """Initialize collections with data if they are empty."""
        # Check if collections are empty
        min_req_data = self.minimal_requirements.get()
        sample_data = self.sample_agreement.get()
        
        # Only populate if empty
        if len(min_req_data["ids"]) == 0:
            logger.info("Populating minimal requirements collection")
            self._populate_minimal_requirements()
        
        if len(sample_data["ids"]) == 0:
            logger.info("Populating sample agreement collection")
            self._populate_sample_agreement()
    
    def _populate_minimal_requirements(self):
        """Populate the minimal requirements collection with essential clauses for rental agreements."""
        requirements = [
            "Der Mietvertrag muss die genaue Anschrift der Wohnung enthalten.",
            "Die Namen und Anschriften aller Mietparteien müssen angegeben sein.",
            "Die monatliche Miethöhe muss klar festgelegt sein.",
            "Die Mietkaution darf maximal drei Monatsmieten betragen.",
            "Nebenkosten müssen genau definiert sein.",
            "Die Kündigungsfrist muss gesetzeskonform sein (3 Monate Standardfrist).",
            "Der Beginn des Mietverhältnisses muss schriftlich festgehalten sein.",
            "Bei befristeten Mietverträgen muss der Grund der Befristung angegeben sein.",
            "Die Wohnfläche sollte genau angegeben sein.",
            "Regelungen zur Instandhaltung und Kleinreparaturen müssen enthalten sein.",
            "Haustierhaltung muss geregelt sein.",
            "Regelungen zu baulichen Veränderungen müssen vorhanden sein.",
            "Die Pflicht zur Schönheitsreparaturen muss klar definiert sein."
        ]
        
        # Create embeddings for all requirements
        embeddings = self.model.encode(requirements)
        
        # Add each requirement to the collection
        for req, emb in zip(requirements, embeddings):
            self.minimal_requirements.add(
                documents=[req],
                embeddings=[emb.tolist()],
                ids=[str(uuid.uuid4())],
                metadatas=[{"info": "Beispiel"}]
            )
    
    def _populate_sample_agreement(self):
        """Populate the sample agreement collection with clauses from a typical rental agreement."""
        sample_clauses = [
            "§1 Mieträume: Der Vermieter vermietet an den Mieter zu Wohnzwecken die Wohnung in der Musterstraße 123, 12345 Musterstadt, bestehend aus 3 Zimmern, Küche, Bad mit einer Gesamtwohnfläche von ca. 75 qm.",
            "§2 Mietdauer: Das Mietverhältnis beginnt am 01.01.2023 und läuft auf unbestimmte Zeit.",
            "§3 Miete: Die monatliche Grundmiete beträgt 750,00 EUR. Die Miete ist monatlich im Voraus, spätestens am dritten Werktag des Monats zu entrichten.",
            "§4 Nebenkosten: Zusätzlich zur Grundmiete zahlt der Mieter monatliche Vorauszahlungen für Betriebskosten in Höhe von 200,00 EUR.",
            "§5 Kaution: Der Mieter zahlt an den Vermieter eine Kaution in Höhe von 2.250,00 EUR (drei Monatsmieten).",
            "§6 Instandhaltung: Der Mieter hat die Mieträume und die gemeinschaftlichen Einrichtungen schonend und pfleglich zu behandeln.",
            "§7 Schönheitsreparaturen: Der Mieter übernimmt die Schönheitsreparaturen innerhalb der Wohnung auf eigene Kosten.",
            "§8 Kündigung: Die Kündigungsfrist beträgt für beide Parteien drei Monate. Die Kündigung muss schriftlich erfolgen.",
            "§9 Haustierhaltung: Die Haltung von Kleintieren ist erlaubt. Für andere Tiere ist die Erlaubnis des Vermieters einzuholen.",
            "§10 Bauliche Veränderungen: Bauliche Veränderungen dürfen nur mit schriftlicher Zustimmung des Vermieters vorgenommen werden.",
            "§11 Hausordnung: Die Hausordnung ist Bestandteil dieses Vertrages.",
            "§12 Schlüssel: Der Mieter erhält bei Einzug 3 Haustürschlüssel und 2 Wohnungsschlüssel.",
            "§13 Rückgabe der Mietsache: Bei Beendigung des Mietverhältnisses hat der Mieter die Mietsache vollständig geräumt und gereinigt zurückzugeben."
        ]
        
        # Create embeddings for all clauses
        embeddings = self.model.encode(sample_clauses)
        
        # Add each clause to the collection
        for clause, emb in zip(sample_clauses, embeddings):
            clause_number = clause.split(" ")[0]
            clause_title = clause.split(":")[0].split(" ", 1)[1] if ":" in clause else ""
            
            self.sample_agreement.add(
                documents=[clause],
                embeddings=[emb.tolist()],
                ids=[str(uuid.uuid4())],
                metadatas=[{"info": "Beispiel"}]
            )
        
    def split_text_into_sections(self, text):
        """Split a text into sentences using newline character."""
        try:
            sentences = text.split('\n')
            # Filter out too short or empty sentences
            sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
            return sentences
        except Exception as e:
            logger.error(f"Error splitting text into sentences: {e}")
            return []
    
    def analyze_document_for_issues(self, sentences, document_metadata=None):
        """
        Analyze a rental agreement document for issues by comparing each sentence
        with the sample agreement to identify unusual clauses.
        
        Args:
            sentences (list): List of sentences from the document
            document_metadata (dict, optional): Metadata about the document
            
        Returns:
            list: Analysis results for each identified issue, formatted according to the OpenAPI spec
        """
        if document_metadata is None:
            document_metadata = {}
            
        results = []
        
        # Skip if no sentences
        if not sentences:
            return [{"text": "Keine Sätze zum Analysieren gefunden.", 
                    "category": "fehlend", 
                    "description": "Das Dokument enthält keinen Text oder konnte nicht gelesen werden."}]
        
        # Process each sentence
        for sentence in sentences:
            # Skip very short sentences
            if len(sentence) < 10:
                continue
                
            # Create embedding for the sentence
            try:
                sentence_embedding = self.model.encode([sentence])[0].tolist()
                
                # Search for similar clauses in the sample agreement
                search_results = self.sample_agreement.query(
                    query_embeddings=[sentence_embedding],
                    n_results=1
                )
                
                # Check if there's a match in the sample agreement
                if search_results["distances"][0][0] > 0.3:  # Higher distance means less similar
                    # This is an unusual clause that doesn't match any standard clause
                    
                    results.append({
                        "text": sentence,
                        "category": "unusual",
                        "description": ""
                    })
                else: 
                    results.append({
                            "text": sentence,
                            "category": "",
                            "description": ""
                        })
                
            except Exception as e:
                logger.error(f"Error analyzing sentence: {e}")
                continue
        
        return results

# Create a singleton instance
analyzer = RentalAnalysis()

if __name__ == "__main__":
    # Test code
    query = "Kündigungsfrist Mietvertrag"
    
    # Query minimal requirements
    query_embedding = analyzer.model.encode([query])[0].tolist()
    results = analyzer.minimal_requirements.query(
        query_embeddings=[query_embedding],
        n_results=2
    )
    
    print("\n🔍 Relevante minimale Anforderungen:")
    for doc, dist in zip(results["documents"][0], results["distances"][0]):
        print(f" - {doc} (Ähnlichkeit: {1 - dist:.4f})")
    
    # Query sample agreement
    results = analyzer.sample_agreement.query(
        query_embeddings=[query_embedding],
        n_results=2
    )
    
    print("\n🔍 Relevante Klauseln aus dem Mustermietvertrag:")
    for doc, dist in zip(results["documents"][0], results["distances"][0]):
        print(f" - {doc} (Ähnlichkeit: {1 - dist:.4f})")