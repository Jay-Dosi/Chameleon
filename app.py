import os
from flask import Flask, request, redirect, render_template, jsonify, Response
from models import db, AttackLog
from ai_engine import generate_honeypot_response, init_gemini
from sqlalchemy import func

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "chameleon-honeypot-secret")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///honeypot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    init_gemini()

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
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    payload_data = None
    if request.data:
        try:
            payload_data = request.data.decode('utf-8')
        except:
            payload_data = str(request.data)
    elif request.form:
        payload_data = str(dict(request.form))
    else:
        try:
            if request.is_json and request.json:
                payload_data = str(request.json)
        except:
            pass
    
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
        mimetype='application/json',
        headers={'Cache-Control': 'no-cache, no-store, must-revalidate'}
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
