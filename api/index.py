"""
Vercel serverless function wrapper for Flask app.
Vercel's @vercel/python builder automatically handles WSGI apps like Flask.
We just need to import and expose the Flask app instance.
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import app modules
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Import the Flask app
# This will initialize the app and database
from app import app

# Vercel's Python runtime automatically detects WSGI apps
# and handles routing. We just need to export the app.
__all__ = ['app']
