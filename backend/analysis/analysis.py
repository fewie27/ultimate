import os
import uuid
import logging
import json
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
import openai
from dotenv import load_dotenv

# Import utilities
from utils.file_utils import extract_text, split_text_into_sections

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Initialize OpenAI with API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    logger.warning("OPENAI_API_KEY environment variable not found. OpenAI API calls will fail.")
else:
    logger.info("OPENAI_API_KEY found.")
    
openai.api_key = openai_api_key

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
        
        # Define path to sample data folder
        self.sample_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'sample_data')
        
        # Initialize ChromaDB client
        self.client = PersistentClient(path=data_dir)

        # Initialize sentence embedding model
        self.model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        
        # Create collections
        self.minimal_requirements = self.client.get_or_create_collection("minimal_requirements")
        self.sample_agreement = self.client.get_or_create_collection("sample_agreement")
        
        # Populate collections if they're empty
        self._initialize_collections()
        
        logger.info("Rental agreement analysis initialized")
    
    def _initialize_collections(self):
        """Initialize collections with data on each startup."""
        # Check if collections exist and delete them if they do
        try:
            if "minimal_requirements" in [col.name for col in self.client.list_collections()]:
                self.client.delete_collection("minimal_requirements")
            if "sample_agreement" in [col.name for col in self.client.list_collections()]:
                self.client.delete_collection("sample_agreement")
            
            # Recreate collections
            self.minimal_requirements = self.client.create_collection("minimal_requirements")
            self.sample_agreement = self.client.create_collection("sample_agreement")
        except Exception as e:
            logger.error(f"Error reinitializing collections: {e}")
            # If there was an error deleting, try to get existing collections
            self.minimal_requirements = self.client.get_or_create_collection("minimal_requirements")
            self.sample_agreement = self.client.get_or_create_collection("sample_agreement")
        
        # Populate collections
        logger.info("Populating minimal requirements collection")
        self._populate_minimal_requirements()
        
        logger.info("Populating sample agreement collection")
        self._populate_sample_agreement()
    
    def _populate_collection(self, collection, collection_name, sample_files):
        """
        Generic method to populate a collection with clauses from sample files.
        
        Args:
            collection: The ChromaDB collection to populate
            collection_name: Name of the collection (for logging purposes)
            sample_files: List of sample files to process
        """
        all_sample_clauses = []
        
        # Process each sample file
        for filename in sample_files:
            file_path = os.path.join(self.sample_data_dir, filename)
            
            # Check if file exists
            if not os.path.exists(file_path):
                logger.warning(f"Sample file not found: {file_path}")
                continue
            
            # Extract text from the file
            try:
                text = extract_text(file_path)
                sample_clauses = split_text_into_sections(text)
                
                logger.info(f"Extracted {len(sample_clauses)} clauses from {filename}")
                
                # Add to the combined list
                all_sample_clauses.extend(sample_clauses)
            except Exception as e:
                logger.error(f"Error extracting text from {filename}: {e}")
        
        # If no clauses were found in any file, use default set
        if not all_sample_clauses:
            logger.warning(f"No clauses found in any sample files for {collection_name}. Using default set.")
            if collection_name == "minimal_requirements":
                all_sample_clauses = [
                    "Der Mietvertrag muss die genaue Anschrift der Wohnung enthalten.",
                    "Die Namen und Anschriften aller Mietparteien müssen angegeben sein.",
                    "Die monatliche Miethöhe muss klar festgelegt sein."
                ]
            else:  # sample_agreement
                all_sample_clauses = [
                    "§1 Mieträume: Der Vermieter vermietet an den Mieter zu Wohnzwecken die Wohnung.",
                    "§2 Mietdauer: Das Mietverhältnis beginnt am 01.01.2023."
                ]
        
        # Create embeddings for all clauses
        embeddings = self.model.encode(all_sample_clauses)
        
        # Add each clause to the collection
        for clause, emb in zip(all_sample_clauses, embeddings):
            # Extract clause number if available (for sample agreements)
            metadata = {"info": "Beispiel"}
            collection.add(
                documents=[clause],
                embeddings=[emb.tolist()],
                ids=[str(uuid.uuid4())],
                metadatas=[metadata]
            )
        
        logger.info(f"Added {len(all_sample_clauses)} clauses to {collection_name} collection")
    
    def _populate_minimal_requirements(self):
        """Populate the minimal requirements collection with essential clauses for rental agreements."""
        sample_files = ["Mietvertrag_potentially_invalid.docx"]
        self._populate_collection(self.minimal_requirements, "minimal_requirements", sample_files)
    
    def _populate_sample_agreement(self):
        """Populate the sample agreement collection with clauses from sample rental agreement files."""
        sample_files = ["Mietvertrag_2.docx", "Mietvertrag_3.docx", "Mietvertrag_4.docx", 
                      "Mietvertrag_5.docx", "Mietvertrag_6.docx", "Mietvertrag_7.docx", "Mietrecht_GESETZ.docx"]
        self._populate_collection(self.sample_agreement, "sample_agreement", sample_files)
    
    def split_text_into_sections(self, text):
        """Split a text into sentences using newline character."""
        return split_text_into_sections(text)
    
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
            if len(sentence) < 40:
                results.append({
                            "text": sentence,
                            "category": [],
                            "description": ""
                        })
                continue
                
            try:
                sentence_embedding = self.model.encode([sentence])[0].tolist()
                
                # Search for similar clauses in the sample agreement
                sample_results = self.sample_agreement.query(
                    query_embeddings=[sentence_embedding],
                    n_results=1
                )
                
                # Search for similar clauses in the minimal requirements
                minimal_results = self.minimal_requirements.query(
                    query_embeddings=[sentence_embedding],
                    n_results=1
                )
                
                sample_distance = sample_results["distances"][0][0]
                minimal_distance = minimal_results["distances"][0][0]
                
                closest_sample = sample_results["documents"][0][0]
                closest_minimal = minimal_results["documents"][0][0]

                                # Determine the category based on distances
                category = []

                if sample_distance > 4:
                    category.append("unusual")
                else:
                    category.append("match_found")

                if minimal_distance <= 4:
                    category.append("invalid")
                else:
                    category.append("valid")

                                
                results.append({
                    "text": sentence,
                    "category": category,
                    "description": "",
                    "sample_distance": sample_distance,
                    "closest_sample": closest_sample,
                    "minimal_distance": minimal_distance,
                    "closest_minimal": closest_minimal
                })
                
            except Exception as e:
                logger.error(f"Error analyzing sentence: {e}")
                continue
        
        # If no results were found, add a default entry
        if not results:
            results.append({
                "text": "Keine problematischen Klauseln gefunden.",
                "category": "fehlend",
                "description": "Der Mietvertrag enthält keine offensichtlich problematischen Bestimmungen."
            })
        
        return results
    
    def analyze_essentials(self, text):
        """
        Analyze the essential contents of a rental agreement using OpenAI API.
        
        The essential contents are:
        1. Parties to the contract
        2. Rental object
        3. Rent amount
        4. Start of rental
        
        Args:
            text (str): The text of the rental agreement
            
        Returns:
            dict: Dictionary containing the essential contents of the rental agreement
        """
        logger.info("Analyzing essential contents of rental agreement")
        
        try:
            # Define the prompt for OpenAI
            prompt = """Bitte überprüfe den sogleich angegebenen Mietvertrag auf seine wesentlichen Vertragsinhalte und gebe die Ergebnisse in einem JSON-Format zurück. Die wesentlichen Vertragsinhalte eines Mietvertrags sind:
                1. Die Vertragsparteien
                2. Der Mietgegenstand
                3. Die Miete
                4. Der Mietbeginn

                Falls einer dieser Punkte nicht genannt ist, gib den Wert als `null` zurück. Der JSON-Output soll wie folgt aussehen:

                {
                    "vertragsparteien": "<Vertragsparteien>",
                    "mietgegenstand": "<Mietgegenstand>",
                    "miete": "<Miete>",
                    "mietbeginn": "<Mietbeginn>"
                }

                Mietvertrag:
            """
                        
            # Make API call to OpenAI
            response = openai.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "Du bist ein hilfreicher Assistent, der Mietverträge analysiert."},
                    {"role": "user", "content": prompt + text}
                ],
                temperature=0.0,  # We want deterministic answers
                max_completion_tokens=1000
            )
            response_text = response.choices[0].message.content

            # Attempt to parse the response as JSON
            try:
                # Extract JSON from the response text if it's wrapped in ```json ... ``` blocks
                if "```json" in response_text:
                    json_start = response_text.find('```json') + 7
                    json_end = response_text.rfind('```')
                    json_str = response_text[json_start:json_end].strip()
                    result = json.loads(json_str)
                else:
                    # Try direct parsing
                    result = json.loads(response_text)
                    
                logger.info("Successfully parsed JSON response")
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {e}")
                result = {
                    "error": "Invalid JSON response from OpenAI",
                    "response": response_text
                }
            
            logger.info("Essential content analysis complete")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing essential contents: {e}")
            return {
                "analysis": "Fehler bei der Analyse der wesentlichen Vertragsinhalte.",
                "status": "error",
                "error": str(e)
            }

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