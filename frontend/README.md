# TallyQuery - AI Accounting Assistant

TallyQuery is an AI-powered accounting assistant web application that allows you to upload CSV or Excel files and ask natural language questions about your data. The app uses Google Gemini AI to analyze your data and provide answers with visualizations.

## Features

- **File Upload**: Upload CSV or Excel files (max 10MB)
- **Natural Language Queries**: Ask questions about your data in plain English
- **AI-Powered Analysis**: Uses Google Gemini to understand and analyze your data
- **Visualizations**: Automatic chart generation (bar/line) based on query results
- **Session Management**: In-memory session storage with automatic cleanup
- **Responsive Design**: Clean, modern UI built with React and Tailwind CSS

## Project Structure

```
Tally-query/
├── frontend/                        # React + TypeScript frontend
│   ├── src/
│   │   ├── components/              # Figma-exported UI components
│   │   ├── pages/
│   │   │   ├── UploadPage.tsx       # File upload page
│   │   │   └── QueryPage.tsx        # Query/chat interface
│   │   ├── api/
│   │   │   └── client.ts            # API client
│   │   ├── hooks/
│   │   │   ├── useUpload.ts         # Upload hook
│   │   │   └── useQuery.ts          # Query hook
│   │   ├── store/
│   │   │   └── sessionStore.ts      # Zustand state management
│   │   ├── types/
│   │   │   └── index.ts             # TypeScript types
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── .env                         # Environment variables
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                         # FastAPI Python backend
│   ├── app/
│   │   ├── routers/
│   │   │   ├── upload.py            # File upload endpoint
│   │   │   ├── query.py             # Query endpoint
│   │   │   ├── session.py           # Session management
│   │   │   └── health.py            # Health check
│   │   ├── services/
│   │   │   ├── file_service.py      # File parsing
│   │   │   ├── gemini_service.py    # Gemini AI integration
│   │   │   └── analytics_service.py # Query execution
│   │   ├── utils/
│   │   │   ├── schema_extractor.py  # Schema extraction
│   │   │   ├── prompt_builder.py    # Prompt generation
│   │   │   └── response_parser.py  # Response parsing
│   │   ├── session/
│   │   │   └── store.py             # In-memory session storage
│   │   ├── models/                  # Pydantic models
│   │   ├── core/                    # Config & middleware
│   │   └── main.py                  # FastAPI app
│   ├── .env                         # Environment variables
│   ├── requirements.txt
│   └── main.py
│
└── README.md
```

## Prerequisites

- **Node.js** (v18 or higher)
- **Python** (v3.10 or higher)
- **Google Gemini API Key**

## Setup

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables:
   - Open `backend/.env`
   - Replace `YOUR_KEY_HERE` with your Google Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   CORS_ORIGINS=http://localhost:5173
   SESSION_TTL_MINUTES=30
   ```

5. Start the backend server:
```bash
uvicorn main:app --reload
```

The backend will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:5173`

## Usage

1. Open your browser and navigate to `http://localhost:5173`
2. Upload a CSV or Excel file containing your data
3. Once uploaded, you'll be redirected to the query page
4. Type natural language questions about your data, for example:
   - "What is my total revenue by category?"
   - "Show me the top 5 customers"
   - "What's the monthly sales trend?"
5. View the AI-generated answers and visualizations

## API Endpoints

### POST /upload
Upload a CSV or Excel file
- **Body**: `multipart/form-data` with `file` field
- **Response**: `{ session_id: string, schema_preview: SchemaPreview }`

### POST /query
Submit a natural language query
- **Body**: `{ session_id: string, question: string }`
- **Response**: `{ answer: string, chart_data: ChartData | null, query_type: string, rows_analysed: number }`

### GET /session/status
Check session status
- **Query**: `session_id`
- **Response**: Session metadata

### DELETE /session/clear
Clear a session
- **Query**: `session_id`
- **Response**: Success message

### GET /health
Health check endpoint

## Environment Variables

### Backend (.env)
- `GEMINI_API_KEY`: Your Google Gemini API key (required)
- `CORS_ORIGINS`: Allowed CORS origins (default: http://localhost:5173)
- `SESSION_TTL_MINUTES`: Session time-to-live in minutes (default: 30)

### Frontend (.env)
- `VITE_API_BASE_URL`: Backend API URL (default: http://localhost:8000)

## Technology Stack

### Frontend
- React 18
- TypeScript
- Vite
- Tailwind CSS
- Recharts (visualizations)
- Zustand (state management)
- React Router (routing)
- Axios (HTTP client)

### Backend
- FastAPI
- Python 3.10+
- Pandas (data processing)
- LangChain (AI orchestration)
- Google Gemini (AI model)
- Pydantic (data validation)

## Notes

- **Data Privacy**: All data is stored in memory only and is automatically cleared after 30 minutes of inactivity
- **File Size Limit**: Maximum file size is 10MB
- **Supported Formats**: CSV and Excel (.xlsx) files only
- **No Database**: This is a prototype with in-memory storage only

## Troubleshooting

### Backend fails to start
- Ensure Python 3.10+ is installed
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify your GEMINI_API_KEY is set correctly in `.env`

### Frontend fails to start
- Ensure Node.js 18+ is installed
- Run `npm install` to install dependencies
- Check that the backend is running on port 8000

### CORS errors
- Verify `CORS_ORIGINS` in backend `.env` matches your frontend URL
- Ensure both frontend and backend are running

### Gemini API errors
- Check that your API key is valid
- Verify you have sufficient API quota
- Check the Gemini API status page

## License

This is a prototype project for demonstration purposes.
