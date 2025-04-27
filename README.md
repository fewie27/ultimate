# Ultimate Legal Document Analysis

A powerful legal document analysis tool designed to analyze rental agreements and identify potential issues. Built with a Python FastAPI backend and React frontend.

## Features

- **Document Upload**: Easily upload rental agreements for analysis
- **Legal Analysis**: Automatically analyze documents for potentially invalid or unusual clauses
- **Essential Content Extraction**: Identifies and extracts key information like parties, rental object, rent amount, and rental start date
- **Vector-based Comparison**: Uses advanced embedding techniques to compare with sample agreements and legal requirements
- **AI-powered Analysis**: Leverages OpenAI for intelligent document understanding

## Project Structure

```
.
├── backend/                # Python FastAPI backend
│   ├── analysis/           # Document analysis engine
│   ├── api/                # API implementations
│   ├── utils/              # Utility functions
│   ├── main.py             # Main FastAPI application
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/                # React source code
│   └── package.json        # NPM dependencies
├── openapi/                # OpenAPI specification
│   └── openapi.yml         # API specification
├── sample_data/            # Sample rental agreements
└── docker-compose.yml      # Docker Compose configuration
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Node.js 14+
- OpenAI API key

### Environment Setup

1. Copy the template environment file:
   ```bash
   cp .env.template .env
   ```

2. Add your OpenAI API key to the `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

### Running with Docker

Start the application with Docker Compose:

```bash
docker-compose up
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000/api

### Development Setup

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Technical Details

### Backend

- **FastAPI**: High-performance API framework
- **Sentence Transformers**: For generating document embeddings
- **ChromaDB**: Vector database for similarity comparisons
- **OpenAI API**: For analyzing essential contract contents

### Frontend

- **React**: UI framework
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tooling

## License

[MIT License](LICENSE) 