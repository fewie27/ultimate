import os
import logging
import PyPDF2
import docx
import pytesseract
from PIL import Image
import json
import re
import nltk

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download and set up NLTK resources
try:
    nltk.download('punkt', quiet=True)
    from nltk.tokenize import sent_tokenize
    logger.info("Loaded NLTK punkt tokenizer for sentence detection")
except Exception as e:
    logger.error(f"Error loading NLTK resources: {e}")
    sent_tokenize = None

def split_text_into_sections(text):
    """Split German text into sentences using NLTK's sentence tokenizer.
    This properly handles German sentence boundaries and preserves punctuation."""
    if not text or not text.strip():
        return []
    
    result = []
    
    # Split the text by newlines to preserve paragraph structure
    paragraphs = text.split('\n')
    
    for paragraph in paragraphs:
        if not paragraph.strip():
            # Keep empty lines as separate entries
            result.append("\n\n")
            continue
        
        # If NLTK tokenizer is available, use it for sentence detection
        if sent_tokenize is not None:
            try:
                # Use NLTK to split the paragraph into sentences
                # Setting language to German for proper sentence boundary detection
                sentences = sent_tokenize(paragraph, language='german')
                if sentences:
                    # Add all sentences except the last one
                    for sentence in sentences[:-1]:
                        if sentence.strip():
                            result.append(sentence.strip())
                    
                    # For the last sentence, append a newline character
                    if sentences[-1].strip():
                        result.append(sentences[-1].strip() + "\n")
            except Exception as e:
                logger.error(f"Error in NLTK sentence splitting: {e}")
                # If a sentence couldn't be properly split, add the whole paragraph
                if paragraph.strip():
                    result.append(paragraph.strip() + "\n")
    
    return result

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
    """Extract text from a DOCX file, preserving empty lines"""
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            if para.text.strip() == "":
                text += "\n"  # Represent empty paragraph by an extra newline
            else:
                text += para.text.strip() + "\n"
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