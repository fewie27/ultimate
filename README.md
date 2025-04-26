# Web Application with Docker

This project is a web application with a Python backend, a React.js frontend, and uses OpenAPI for interface generation.

## Project Structure

```
.
├── backend/                # Python Flask backend
│   ├── api/                # API implementations
│   ├── openapi/            # OpenAPI specification directory 
│   ├── app.py              # Main Flask application
│   ├── Dockerfile          # Backend container configuration
│   └── requirements.txt    # Python dependencies
├── frontend/               # React.js frontend
│   ├── public/             # Static files
│   ├── src/                # React source code
│   ├── Dockerfile          # Frontend container configuration
│   └── package.json        # NPM dependencies
├── openapi/                # OpenAPI specification
│   └── openapi.yml         # API specification
└── docker-compose.yml      # Docker Compose configuration
```

## Getting Started

### Prerequisites

You need to have Docker and Docker Compose installed on your machine.

### Running the Application

1. Clone this repository
2. Start the application with Docker Compose:

```bash
docker-compose up
```

3. The application will be available at:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000/api
   - API Documentation: http://localhost:5000/api/ui

## API Generation

The system automatically generates API interfaces for both the frontend and backend from the OpenAPI specification.

- Backend: Connexion (Python) reads the OpenAPI spec and handles routing
- Frontend: openapi-typescript-codegen generates TypeScript clients during build

## Development

### Frontend Development

To run the frontend in development mode:

```bash
cd frontend
npm install
npm run generate-api  # Generate API clients from OpenAPI spec
npm start
```

### Backend Development

To run the backend in development mode:

```bash
cd backend
pip install -r requirements.txt
python app.py
```

## Notes

This is a starter project. For production use, consider:
- Adding proper authentication
- Setting up a database
- Implementing error handling
- Adding tests
- Setting up CI/CD pipelines 