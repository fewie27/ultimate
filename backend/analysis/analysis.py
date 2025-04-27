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
    
    def _populate_minimal_requirements(self):
        """Populate the minimal requirements collection with essential clauses for rental agreements from file."""
        file_path = os.path.join(self.sample_data_dir, "Mindestanforderungen.txt")
        text = extract_text(file_path)
        requirements = split_text_into_sections(text)
        
        if not requirements:
            logger.warning("No requirements found in file. Using default set.")
            requirements = [
                "Der Mietvertrag muss die genaue Anschrift der Wohnung enthalten.",
                "Die Namen und Anschriften aller Mietparteien müssen angegeben sein.",
                "Die monatliche Miethöhe muss klar festgelegt sein."
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
            
        logger.info(f"Added {len(requirements)} requirements to minimal_requirements collection")
    
    def _populate_sample_agreement(self):
        """Populate the sample agreement collection with clauses from multiple sample rental agreement files."""
        sample_files = ["Mietvertrag_2.docx", "Mietvertrag_3.docx", "Mietvertrag_4.docx", "Mietvertrag_5.docx", "Mietvertrag_6.docx", "Mietvertrag_7.docx", "Mietrecht_GESETZ.docx"]
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
            logger.warning("No clauses found in any sample files. Using default set.")
            all_sample_clauses = [
                "§1 Mieträume: Der Vermieter vermietet an den Mieter zu Wohnzwecken die Wohnung.",
                "§2 Mietdauer: Das Mietverhältnis beginnt am 01.01.2023."
            ]
        
        # Create embeddings for all clauses
        embeddings = self.model.encode(all_sample_clauses)
        
        # Add each clause to the collection
        for clause, emb in zip(all_sample_clauses, embeddings):
            # Extract clause number if available
            clause_parts = clause.split(" ", 1)
            clause_number = clause_parts[0] if len(clause_parts) > 0 else ""
            
            self.sample_agreement.add(
                documents=[clause],
                embeddings=[emb.tolist()],
                ids=[str(uuid.uuid4())],
                metadatas=[{"info": "Beispiel"}]
            )
        
        logger.info(f"Added {len(all_sample_clauses)} clauses to sample_agreement collection")
    
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
                            "category": "",
                            "description": ""
                        })
                continue
                
            # Create embedding for the sentence
            try:
                sentence_embedding = self.model.encode([sentence])[0].tolist()
                
                # Search for similar clauses in the sample agreement
                search_results = self.sample_agreement.query(
                    query_embeddings=[sentence_embedding],
                    n_results=1
                )
                closest_document = search_results["documents"][0][0]

                
                # Check if there's a match in the sample agreement
                if search_results["distances"][0][0] > 4:  # Higher distance means less similar
                    # This is an unusual clause that doesn't match any standard clause
                    
                    results.append({
                        "text": sentence,
                        "category": "unusual",
                        "description": "",
                        "distance": search_results["distances"][0][0],
                        "closest_document": closest_document
                    })
                else: 
                    results.append({
                        "text": sentence,
                        "category": "match_found",
                        "description": "",
                        "distance": search_results["distances"][0][0],
                        "closest_document": closest_document
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
                model="gpt-4",  # Using gpt-4 as gpt-4.1 is not a valid model name
                messages=[
                    {"role": "system", "content": "Du bist ein hilfreicher Assistent, der Mietverträge analysiert."},
                    {"role": "user", "content": prompt + text}
                ],
                temperature=0.0,  # We want deterministic answers
                max_completion_tokens=1000
            )
            print(response)
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