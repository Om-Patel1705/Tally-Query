# Tally Query

A full-stack application combining React frontend with FastAPI backend for intelligent query processing and data analysis.

## Project Structure

```
Tally-query/
├── backend/                          # FastAPI backend
│   ├── app/
│   │   ├── core/                     # Core configurations and middleware
│   │   ├── models/                   # Request/response models
│   │   ├── routers/                  # API endpoints
│   │   ├── services/                 # Business logic
│   │   ├── session/                  # Session management
│   │   └── utils/                    # Utility functions
│   ├── main.py                       # Application entry point
│   ├── requirements.txt              # Python dependencies
│   └── .env                          # Environment variables
│
├── Figma-Exported-Tally-Frontend/   # React frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/          # React components
│   │   │   └── App.tsx              # Main app component
│   │   └── index.tsx                # Entry point
│   ├── package.json
│   ├── vite.config.ts              # Vite configuration
│   └── .env                         # Frontend environment variables
│
└── README.md                        # This file
```

## Prerequisites

- **Python 3.8+** (for backend)
- **Node.js 16+** and **npm** (for frontend)
- **Git**

## Getting Started

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Create or update `.env` with your configuration:
     ```
     GEMINI_API_KEY=your_gemini_api_key
     CORS_ORIGINS=http://localhost:5173
     SESSION_TTL_MINUTES=30
     ```

5. Start the development server:
   ```bash
   python main.py
   ```
   
   The API will be available at `http://localhost:5000`
   - Swagger docs: `http://localhost:5000/docs`
   - ReDoc: `http://localhost:5000/redoc`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure environment variables:
   - Create `.env` file with:
     ```
     VITE_API_URL=http://localhost:5000
     ```

4. Start the development server:
   ```bash
   npm run dev
   ```
   
   The frontend will be available at `http://localhost:5173`

## API Endpoints

### Health Check
- `GET /health` - Server health status

### Session Management
- `POST /session/start` - Start a new session
- `GET /session/{session_id}` - Get session details
- `DELETE /session/{session_id}` - End session

### File Upload
- `POST /upload` - Upload CSV/data files

### Query Processing
- `POST /query` - Execute a query

### Analytics
- `GET /analytics/{session_id}` - Get session analytics

## Development

### Project Features

- **Gemini AI Integration** - Intelligent query processing
- **Session Management** - Track user sessions
- **File Upload** - CSV/data file support
- **SQL Execution** - Execute SQL queries on uploaded data
- **Analytics** - Track usage and query metrics

### Key Services

- `gemini_service.py` - AI-powered query generation
- `file_service.py` - File upload and processing
- `sql_executor.py` - SQL query execution
- `analytics_service.py` - Usage tracking

## Environment Variables

### Backend (.env)
```
GEMINI_API_KEY=your_gemini_api_key
CORS_ORIGINS=http://localhost:5173
SESSION_TTL_MINUTES=30
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:5000
VITE_APP_NAME=Tally Query
```

## Building for Production

### Backend
```bash
# Install production dependencies
pip install -r requirements.txt

# Run with production server (Gunicorn)
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Frontend
```bash
# Build optimized bundle
npm run build

# Preview production build
npm run preview
```

## Troubleshooting

### Backend Issues
- **Module not found**: Ensure virtual environment is activated and dependencies installed
- **Port 5000 already in use**: Change port in `main.py`
- **API key errors**: Verify GEMINI_API_KEY in `.env`

### Frontend Issues
- **Dependencies not installing**: Clear npm cache: `npm cache clean --force`
- **Port conflict**: Vite will automatically use next available port
- **API connection issues**: Check `VITE_API_URL` in `.env`

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request


## Support

For issues and questions, please open an issue in the repository.
