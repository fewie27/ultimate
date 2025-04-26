FROM python:3.9-slim

# Install tesseract-ocr for image text extraction and other dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies directly (without virtual environment)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/uploads /app/chroma_data

# Copy the application code
COPY . .

# Download spaCy German language model
RUN python -m spacy download de_core_news_sm

EXPOSE 5000

# Run uvicorn directly 
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"] 