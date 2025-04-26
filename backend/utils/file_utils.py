import os
import logging
import PyPDF2
import docx
import pytesseract
from PIL import Image
import nltk
import json
import re

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download necessary NLTK data for sentence tokenization
try:
    nltk.download('punkt', quiet=True)
except Exception as e:
    logger.error(f"Error downloading NLTK data: {e}")

def split_text_into_sections(text):
    """Split German text into sentences using a reliable pattern-based approach 
    optimized for legal documents while preserving the periods at the end."""
    if not text:
        return []
    
    try:
        # Normalize whitespace but keep paragraphs
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        sentences = []
        
        for paragraph in paragraphs:
            if not paragraph:
                continue
            
            # Use a simpler approach that preserves sentence endings
            # Look for patterns like ". " followed by uppercase or end of text
            # But exclude common abbreviations and numbers
            parts = []
            last_end = 0
            
            # Pattern: Look for period + space + capital letter
            # Negative lookbehind to avoid splitting after common abbreviations or numbers
            pattern = r'(?<![0-9]|[A-Za-z]\.[A-Za-z]|Nr|Abs|Art|Str|Dr|Prof|bzw|[0-9])\.\s+(?=[A-ZÄÖÜ])'
            
            for match in re.finditer(pattern, paragraph):
                # Include the period in the sentence
                end_pos = match.end() - 1  # Points to the space after the period
                
                # Extract sentence with the period
                sentence = paragraph[last_end:end_pos].strip()
                if sentence and not (len(sentence) <= 5 and re.match(r'^[0-9]+\.?$', sentence)):
                    parts.append(sentence)
                
                last_end = match.end() - 1  # Start next sentence after the space
                
            # Add the last part
            last_part = paragraph[last_end:].strip()
            if last_part:
                parts.append(last_part)
            
            # Process each part to ensure it ends with proper punctuation
            for part in parts:
                if part and not re.search(r'[\.\!\?]$', part):
                    # If sentence doesn't end with punctuation and not just a number
                    if not re.match(r'^[0-9]+$', part.strip()):
                        part = part + "."
                sentences.append(part)
        
        # Join short fragments like section numbers with their sentences
        final_sentences = []
        i = 0
        while i < len(sentences):
            current = sentences[i]
            
            # If this is a short fragment like a number or section marker
            if (i < len(sentences) - 1 and 
                (re.match(r'^[0-9§]+\.?$', current) or len(current) < 3)):
                # Join with next sentence
                current = current + " " + sentences[i+1]
                i += 2
            else:
                i += 1
                
            final_sentences.append(current)
        
        return final_sentences
    
    except Exception as e:
        logger.error(f"Error in sentence splitting: {e}")
        # Fallback to a simpler approach
        result = []
        for para in text.split('\n'):
            if not para.strip():
                continue
                
            # Simple split at ". " but preserve the periods
            current_pos = 0
            for match in re.finditer(r'\.\s+(?=[A-ZÄÖÜ])', para):
                end_pos = match.start() + 1  # Include the period
                sentence = para[current_pos:end_pos].strip()
                if sentence:
                    result.append(sentence)
                current_pos = match.end()
                
            # Add the last part
            if current_pos < len(para):
                last_sentence = para[current_pos:].strip()
                if last_sentence:
                    result.append(last_sentence)
                    
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