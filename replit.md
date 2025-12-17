# Chameleon: AI-Powered API Honeypot

## Overview
A full-stack Python application that acts as a fake vulnerable server. It accepts traffic to any URL path and uses Google Gemini 1.5 Flash to generate realistic JSON responses in real-time, logging attacker details for analysis.

## Project Structure
```
├── app.py              # Main Flask application
├── models.py           # SQLAlchemy database models
├── ai_engine.py        # Gemini AI integration
├── templates/
│   └── dashboard.html  # Admin dashboard UI
├── static/
│   └── style.css       # Cybersecurity-themed styling
└── requirements.txt    # Python dependencies
```

## Tech Stack
- **Backend**: Python 3.11+, Flask
- **Database**: SQLite with SQLAlchemy ORM
- **AI**: Google Gemini 1.5 Flash via google-genai
- **Frontend**: HTML5, Bootstrap 5, JavaScript (Fetch API)

## Key Features
1. **Catch-All Route**: Any request to undefined endpoints triggers the honeypot
2. **AI Response Generation**: Gemini generates realistic fake API responses
3. **Attack Logging**: All requests logged with IP, method, endpoint, payload, and AI response
4. **Real-time Dashboard**: Auto-refreshing view of attack logs (every 2 seconds)
5. **Statistics**: Total attacks and most targeted endpoint tracking

## Routes
- `/` - Redirects to dashboard
- `/monitor` - Admin dashboard
- `/api/logs` - JSON API for log data (internal use)
- `/<any-path>` - Honeypot trap (catches all other requests)

## Environment Variables
- `GEMINI_API_KEY` - Required for AI response generation
- `SESSION_SECRET` - Flask session secret

## Running the Application
The app runs on port 5000 and binds to 0.0.0.0 for accessibility.

## Database
SQLite database (`honeypot.db`) is created automatically in the instance folder.
