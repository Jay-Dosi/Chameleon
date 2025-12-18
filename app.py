import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, request, redirect, render_template, jsonify, Response
from sqlalchemy import func

from ai_engine import generate_honeypot_response, init_groq
from models import db, AttackLog


# Load environment variables from a .env file if present
BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)


# Ensure Flask can find templates and static files
# Get the directory where app.py is located
app = Flask(__name__, 
            template_folder=str(BASE_DIR / "templates"),
            static_folder=str(BASE_DIR / "static"))
app.secret_key = os.environ.get("SESSION_SECRET", "chameleon-honeypot-secret")

# Database configuration for Vercel serverless environment
# Vercel provides /tmp directory which is writable in serverless functions
# For local development, use the instance folder (Flask-recommended pattern)
# Check for Vercel environment (VERCEL or VERCEL_ENV)
is_vercel = os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV")
if is_vercel:
    # Running on Vercel - use /tmp for database (ephemeral storage)
    db_path = Path("/tmp") / "honeypot.db"
    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        # Fallback if /tmp doesn't work
        db_path = Path("/var/task") / "honeypot.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
else:
    # Local development - use instance folder
    db_path = BASE_DIR / "instance" / "honeypot.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Initialize database and Groq client
# Wrap in try-except to handle initialization errors gracefully
try:
    with app.app_context():
        db.create_all()
        init_groq()
except Exception as e:
    # Log error but don't crash - app can still run with fallback responses
    import sys
    import traceback
    error_msg = f"Warning: Initialization error (non-fatal): {e}"
    print(error_msg, file=sys.stderr, flush=True)
    # Only print full traceback in debug mode to avoid log spam
    if os.environ.get("FLASK_DEBUG") == "1":
        traceback.print_exc(file=sys.stderr)

@app.route('/')
def index():
    return redirect('/monitor')

@app.route('/monitor')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/logs')
def get_logs():
    logs = AttackLog.query.order_by(AttackLog.timestamp.desc()).limit(50).all()
    
    total_attacks = AttackLog.query.count()
    
    most_attacked = db.session.query(
        AttackLog.endpoint, 
        func.count(AttackLog.endpoint).label('count')
    ).group_by(AttackLog.endpoint).order_by(func.count(AttackLog.endpoint).desc()).first()
    
    most_attacked_endpoint = most_attacked[0] if most_attacked else "N/A"
    most_attacked_count = most_attacked[1] if most_attacked else 0
    
    return jsonify({
        'logs': [log.to_dict() for log in logs],
        'stats': {
            'total_attacks': total_attacks,
            'most_attacked_endpoint': most_attacked_endpoint,
            'most_attacked_count': most_attacked_count
        }
    })

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
def honeypot_trap(path):
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address and ',' in ip_address:
        ip_address = ip_address.split(',')[0].strip()
    
    method = request.method
    endpoint = f"/{path}"
    user_agent = request.headers.get("User-Agent", "Unknown")
    
    # Capture any payload the attacker sends (JSON, form, or raw body)
    payload_data = None

    # Prefer structured JSON if available
    json_payload = None
    try:
        if request.is_json:
            json_payload = request.get_json(silent=True)
    except Exception:
        json_payload = None

    if json_payload is not None:
        payload_data = str(json_payload)
    elif request.form:
        payload_data = str(dict(request.form))
    elif request.data:
        try:
            payload_data = request.data.decode("utf-8", errors="replace")
        except Exception:
            payload_data = str(request.data)
    
    ai_response = generate_honeypot_response(method, endpoint, payload_data)
    
    attack_log = AttackLog(
        ip_address=ip_address,
        request_method=method,
        endpoint=endpoint,
        payload_data=payload_data,
        ai_response_sent=ai_response,
        user_agent=user_agent
    )
    
    db.session.add(attack_log)
    db.session.commit()
    
    return Response(
        ai_response,
        status=200,
        mimetype="application/json",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
    )

if __name__ == '__main__':
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host='0.0.0.0', port=5000, debug=debug)
