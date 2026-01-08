
import sys
import os
from pathlib import Path

os.environ["VERCEL"] = "1"

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from app import app
    
    if app is None:
        raise ImportError("Flask app is None")
        
except Exception as e:
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    
    @app.route('/')
    @app.route('/<path:path>')
    def error_handler(path=''):
        import traceback
        error_trace = traceback.format_exc()

        print(f"CRITICAL: Application initialization failed\nError: {e}\n\nTraceback:\n{error_trace}", file=sys.stderr, flush=True)
        return jsonify({
            "error": "Application initialization failed",
            "message": str(e),
            "hint": "Check Vercel Function Logs for full traceback"
        }), 500

__all__ = ['app']
