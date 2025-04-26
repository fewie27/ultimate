import os
import logging
import PyPDF2
import docx
import pytesseract
from PIL import Image
import json
import re
import spacy

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the German spaCy model
try:
    nlp = spacy.load("de_core_news_sm")
    logger.info("Loaded German spaCy model for sentence detection")
except Exception as e:
    logger.error(f"Error loading spaCy model: {e}")
    # Simple German pipeline as fallback if model can't be loaded
    try:
        nlp = spacy.blank("de")
        nlp.add_pipe("sentencizer")
        logger.info("Created basic German pipeline with sentencizer")
    except Exception as e2:
        logger.error(f"Error creating fallback spaCy pipeline: {e2}")
        nlp = None

def split_text_into_sections(text):
    """Split German text into sentences using spaCy's language model.
    This properly handles German sentence boundaries and preserves punctuation."""
    if not text or not text.strip():
        return []
    
    # Try using spaCy for sentence detection
    if nlp is not None:
        try:
            # Process the text with spaCy
            doc = nlp(text)
            
            # Extract sentences with their ending punctuation
            sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
            
            # If spaCy didn't find any sentences, fallback to paragraph splitting
            if not sentences:
                sentences = [p.strip() for p in text.split('\n') if p.strip()]
                
            return sentences
        except Exception as e:
            logger.error(f"Error in spaCy sentence splitting: {e}")
    
    # Fallback method if spaCy isn't available or fails
    try:
        # Simple paragraph and punctuation-based splitting
        paragraphs = text.split('\n')
        sentences = []
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
                
            # Simple split at ". " but preserve the periods
            current_pos = 0
            sentence_endings = list(re.finditer(r'[.!?]\s+(?=[A-ZÄÖÜ])', paragraph))
            
            if sentence_endings:
                for match in sentence_endings:
                    end_pos = match.end() - 1  # Include the punctuation but not the space
                    sentence = paragraph[current_pos:end_pos].strip()
                    if sentence:
                        sentences.append(sentence)
                    current_pos = match.end() - 1  # Start after the punctuation
                
                # Add the last part if there's content after the last period
                if current_pos < len(paragraph):
                    last_sentence = paragraph[current_pos:].strip()
                    if last_sentence:
                        sentences.append(last_sentence)
            else:
                # If no sentence boundaries found, add the whole paragraph
                if paragraph.strip():
                    sentences.append(paragraph.strip())
                    
        return sentences
        
    except Exception as e:
        logger.error(f"Error in fallback sentence splitting: {e}")
        # Last resort: just split by newlines
        return [line.strip() for line in text.split('\n') if line.strip()]

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file, adding one backslash-n after each paragraph."""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()

                if page_text:
                    lines = page_text.split('\n')
                    paragraph = ""
                    for line in lines:
                        stripped_line = line.strip()
                        if stripped_line:
                            paragraph += stripped_line + " "
                        else:
                            # End of paragraph
                            text += paragraph.strip() + "\n"
                            paragraph = ""
                    if paragraph:
                        text += paragraph.strip() + "\n"  # Last paragraph if no empty line at end
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        text = f"Error extracting text: {str(e)}"
    return text

def extract_text_from_docx(file_path):
    """Extract text from a DOCX file"""
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {e}")
        text = f"Error extracting text: {str(e)}"
    return text

def extract_text_from_image(file_path):
    """Extract text from an image using OCR"""
    text = ""
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
    except Exception as e:
        logger.error(f"Error extracting text from image: {e}")
        text = f"Error extracting text: {str(e)}"
    return text

def extract_text(file_path):
    """Extract text from a file based on its extension"""
    _, extension = os.path.splitext(file_path.lower())
    
    if extension in ['.pdf']:
        return extract_text_from_pdf(file_path)
    elif extension in ['.docx', '.doc']:
        return extract_text_from_docx(file_path)
    elif extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
        return extract_text_from_image(file_path)
    else:
        # For text files or unsupported formats, try to read as text
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error reading file as text: {e}")
            return f"Unsupported file format or error reading file: {str(e)}"

def save_results_to_json(file_path, data):
    """Save analysis results to JSON file"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f"Results saved to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving results to JSON: {e}")
        return False 