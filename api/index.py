"""
Vercel serverless function wrapper for Flask app.
Vercel's @vercel/python builder automatically handles WSGI apps like Flask.
"""
import sys
import os
from pathlib import Path

# Set Vercel environment variable for app.py to detect
os.environ["VERCEL"] = "1"

# Add parent directory to path so we can import app modules
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Import the Flask app
# This will initialize the app and database
try:
    from app import app
    
    # Verify app is properly initialized
    if app is None:
        raise ImportError("Flask app is None")
        
except Exception as e:
    # If import fails, create a minimal error handler that shows the actual error
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    
    @app.route('/')
    @app.route('/<path:path>')
    def error_handler(path=''):
        import traceback
        error_trace = traceback.format_exc()
        # Print to stderr so it shows in Vercel logs
        print(f"CRITICAL: Application initialization failed\nError: {e}\n\nTraceback:\n{error_trace}", file=sys.stderr, flush=True)
        return jsonify({
            "error": "Application initialization failed",
            "message": str(e),
            "hint": "Check Vercel Function Logs for full traceback"
        }), 500

# Vercel's Python runtime automatically detects WSGI apps
# The app variable must be named 'app' for Vercel to detect it
__all__ = ['app']
