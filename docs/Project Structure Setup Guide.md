AI Study Buddy - Complete Project Structure Setup
📁 Directory Structure
Create this exact folder structure in your project root:
ai-study-buddy/
├── backend/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── session.py
│   │   └── flashcard.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py
│   │   ├── flashcard_service.py
│   │   └── session_service.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── api.py
│   │   └── health.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── validators.py
│   │   └── helpers.py
│   ├── config.py
│   ├── app.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── main.js
├── docs/
│   ├── requirements.md
│   ├── developer_tasks.md
│   ├── system_design.md
│   └── user_management.md
└── README.md
🚀 Step-by-Step Setup
Step 1: Create Directory Structure
On Windows:
cmdmkdir ai-study-buddy
cd ai-study-buddy
mkdir backend backend\models backend\services backend\routes backend\utils
mkdir frontend frontend\css frontend\js
mkdir docs
On Mac/Linux:
bashmkdir -p ai-study-buddy/{backend/{models,services,routes,utils},frontend/{css,js},docs}
cd ai-study-buddy
Step 2: Create Python Files
Create all the Python files with the exact content I provided. Here's the file creation order:

Backend Configuration:

backend/config.py
backend/.env (see environment setup below)


Models (Data Layer):

backend/models/__init__.py
backend/models/base.py
backend/models/session.py
backend/models/flashcard.py


Services (Business Logic):

backend/services/__init__.py
backend/services/ai_service.py
backend/services/flashcard_service.py
backend/services/session_service.py


Routes (API Endpoints):

backend/routes/__init__.py
backend/routes/api.py
backend/routes/health.py


Utilities:

backend/utils/__init__.py
backend/utils/validators.py
backend/utils/helpers.py


Main Application:

backend/app.py
backend/requirements.txt



Step 3: Environment Configuration
Create backend/.env file:
env# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here-change-in-production

# Database Configuration
DATABASE_URL=sqlite:///flashcards.db

# Hugging Face API (get from https://huggingface.co/settings/tokens)
HUGGING_FACE_API_TOKEN=your-hugging-face-token-here

# Session Configuration
SESSION_TIMEOUT_DAYS=30

# Rate Limiting (optional)
REDIS_URL=memory://
Step 4: Install Dependencies
bashcd backend
pip install -r requirements.txt
If you get import errors, install manually:
bashpip install Flask==2.3.3 Flask-SQLAlchemy==3.0.5 Flask-CORS==4.0.0 Flask-Limiter==3.5.0 python-dotenv==1.0.0 requests==2.31.0 PyMySQL==1.1.0
Step 5: Database Setup
For SQLite (Development):

No additional setup needed
Database file will be created automatically

For MySQL (Production):
sqlCREATE DATABASE flashcards_db;
Update .env:
envDATABASE_URL=mysql+pymysql://username:password@localhost/flashcards_db
Step 6: Frontend Files
Keep your existing frontend files, but update the structure:

Move index.html to frontend/index.html
Move CSS to frontend/css/styles.css
Create frontend/js/main.js (extract JS from HTML)

Step 7: Test the Setup

Start the backend:

bashcd backend
python app.py

Check health endpoint:

bashcurl http://localhost:5000/health

Open frontend:

Open frontend/index.html in your browser
Or serve it locally: python -m http.server 8000 (from frontend directory)



🔧 Migration from Old Code
Update Frontend API Calls
Change the JavaScript fetch calls to include session management:
Old way:
javascriptfetch('http://localhost:5000/api/process-notes', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ notes })
})
New way:
javascript// Get or create session first
let sessionId = localStorage.getItem('sessionId');
if (!sessionId) {
    const sessionResponse = await fetch('http://localhost:5000/api/session', {
        method: 'POST'
    });
    const sessionData = await sessionResponse.json();
    sessionId = sessionData.data.id;
    localStorage.setItem('sessionId', sessionId);
}

// Use session in API calls
fetch('http://localhost:5000/api/process-notes', {
    method: 'POST',
    headers: { 
        'Content-Type': 'application/json',
        'X-Session-ID': sessionId 
    },
    body: JSON.stringify({ notes })
})
📋 File Contents Summary
Each file serves a specific purpose:

config.py: Environment-based configuration
models/: Database table definitions and relationships
services/: Business logic and AI integration
routes/: API endpoints and request handling
utils/: Helper functions and validation
app.py: Application factory and initialization

🚨 Common Issues & Solutions
Import Errors
python# Add this to the top of app.py if you get import errors
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
Database Errors

Delete flashcards.db and restart the app to recreate tables
Check file permissions on the database file

Hugging Face API Issues

The app works without the API token (uses fallback generation)
Get a free token at https://huggingface.co/settings/tokens

CORS Errors

Make sure Flask-CORS is installed and configured
Check that the frontend is making requests to the correct port

🎯 Testing Your Setup
Run these tests to verify everything works:

Backend Health Check:
bashcurl http://localhost:5000/health

Create Session:
bashcurl -X POST http://localhost:5000/api/session

Process Notes:
bashcurl -X POST http://localhost:5000/api/process-notes \
-H "Content-Type: application/json" \
-d '{"notes": "Python is a programming language. It is used for web development, data science, and automation. Variables store data. Functions perform tasks."}'

Frontend Test:

Open frontend/index.html
Paste some notes and click "Generate Flashcards"
Check browser console for any errors



📈 Next Steps After Setup
Once everything is working:

Enhance the Frontend: Add session persistence
Add Features: Study tracking, statistics, multiple flashcard sets
Deploy: Use the deployment guide in the documentation
Monitor: Check logs and performance

This modular structure makes your codebase much more maintainable and scalable for future enhancements!