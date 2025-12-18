## Chameleon – The Infinite API Honeypot

AI‑Powered Dynamic API Honeypot with Groq.

Chameleon is an AI‑driven API honeypot that traps attackers in an **infinite maze of fake APIs**:

- Any path a scanner or attacker tries (e.g. `/admin`, `/wp-login.php`, `/api/users`, `/secret_passwords.txt`) will:
  - Be **accepted and logged**.
  - Be answered with a **realistic JSON response** hallucinated by **Groq's openai/gpt-oss-120b**.
- The attacker sees **plausible data** and keeps poking; you watch everything live on the **monitoring dashboard**.

---

## 1. Architecture

- **Flask (`app.py`)** – Web server, routes, and the global catch‑all trap.
- **SQLite + SQLAlchemy (`models.py`)** – Persistent logging of every probe:
  - Time, IP, HTTP method, endpoint, payload, fake response, user agent.
- **Groq AI (`ai_engine.py`)** – The brain that fabricates convincing JSON responses using Groq's fast LLM inference.
- **Dashboard (`templates/dashboard.html` + `static/style.css`)** – Cyber/hacker‑themed live monitoring UI.

Project layout:

```text
.
├─ app.py                # Main Flask app, routes, trap logic, env loading
├─ ai_engine.py          # Groq integration and response generation
├─ models.py             # SQLAlchemy models (AttackLog)
├─ requirements.txt      # Python dependencies
├─ main.py               # (legacy; not used by honeypot)
├─ instance/
│  └─ honeypot.db        # SQLite database (auto-created)
├─ templates/
│  └─ dashboard.html     # Live Attack Dashboard
└─ static/
   └─ style.css          # Cyber / hacker theme styles
```

---

## 2. Prerequisites

- **Python** 3.10+ recommended.
- **Groq API key** (get one at [console.groq.com](https://console.groq.com)).
- Internet connectivity so the server can reach the Groq API.

---

## 3. Installation

From the project root (where `app.py` and `requirements.txt` live):

```bash
# (Optional) Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate # Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

Key dependencies (in `requirements.txt`):

- `flask`, `flask-sqlalchemy`, `sqlalchemy`
- `groq` (Groq AI client for fast LLM inference)
- `python-dotenv`

---

## 4. Environment Configuration

Chameleon loads environment variables from a local `.env` file using `python-dotenv`.

Create a file named **`.env`** in the same directory as `app.py`:

```bash
GROQ_API_KEY=your-real-groq-api-key-here
SESSION_SECRET=change-this-to-a-long-random-string

# Set to 1 for development (Flask debug mode), 0 or omit for production
FLASK_DEBUG=0
```

Recommended to also create a **`.env.example`** (for sharing in git) with placeholder values:

```bash
GROQ_API_KEY=your-groq-api-key-here
SESSION_SECRET=change-this-session-secret
FLASK_DEBUG=0
```

Then **do not commit** your real `.env` (add `.env` to `.gitignore`).

Environment loading is wired in `app.py`:

```python
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
```

The SQLite database is created in `instance/honeypot.db`:

```python
db_path = BASE_DIR / "instance" / "honeypot.db"
db_path.parent.mkdir(parents=True, exist_ok=True)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
```

---

## 5. How It Works

### 5.1 Routes

- **Dashboard**
  - `GET /` → Redirects to `/monitor`.
  - `GET /monitor` → Renders the live dashboard (`templates/dashboard.html`).

- **Logs API**
  - `GET /api/logs` → Returns:
    - `logs`: last 50 attack entries.
    - `stats`: `total_attacks`, `most_attacked_endpoint`, `most_attacked_count`.

- **Catch‑all Trap (the honeypot)**
  - `/<path:path>` for methods: `GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD`.
  - This route is defined **last** in `app.py`, so `/monitor` and `/api/logs` are not shadowed.
  - For every unmatched request, it:
    - Extracts IP (using `X-Forwarded-For` if present, otherwise `remote_addr`).
    - Captures payload in a best-effort order:
      - JSON via `request.get_json(silent=True)`,
      - else form data (`request.form`),
      - else raw body (`request.data`).
    - Calls `generate_honeypot_response(...)` in `ai_engine.py`.
    - Stores the full interaction in the `AttackLog` table.
    - Returns a JSON response (AI or fallback) to the requester.

### 5.2 AI Engine (Groq)

`ai_engine.py` wraps the Groq API and enforces **strict JSON**:

- Initializes a `Groq` client with `GROQ_API_KEY`.
- Uses the **openai/gpt-oss-120b** model on Groq for fast, high-quality responses.
- Uses a **legacy enterprise backend persona**:
  - Verbose, boring, structured responses.
  - Snake_case keys, timestamps, audit metadata.
  - GET → returns realistic dummy records (e.g., accounts, users, transactions).
  - POST/PUT/PATCH → returns success or validation-style payloads.
- The prompt includes a hard constraint:
  - **"OUTPUT ONLY RAW JSON. NO MARKDOWN. NO CODE BLOCKS. NO EXPLANATION TEXT."**

**Cleaning & validation:**

- Strips ```json / ``` fences if present.
- Attempts to extract the `{ ... }` portion from mixed text.
- Validates via `json.loads`. If invalid or any exception is raised, it falls back.

**Fallback behavior:**

- Returns a generic but realistic legacy success JSON:

```json
{
  "status": "ok",
  "timestamp": "2025-01-01T12:00:00.000000Z",
  "server": "legacy-enterprise-api",
  "correlation_id": "LEG-1730000000",
  "message": "Request processed successfully."
}
```

This ensures attackers always see a believable JSON response, even if the AI fails.

### 5.3 Logging

The `AttackLog` model (in `models.py`) records:

- `timestamp`
- `ip_address`
- `request_method`
- `endpoint`
- `payload_data`
- `ai_response_sent`
- `user_agent`

These are persisted to `instance/honeypot.db` and surfaced to the dashboard via `/api/logs`.

---

## 6. Running the Honeypot

From the project root:

```bash
python app.py
```

The app binds to:

- Host: `0.0.0.0`
- Port: `5000`
- Debug: controlled by `FLASK_DEBUG` in `.env` (1 = debug, 0 = production).

### 6.1 Access the Dashboard

Open:

```text
http://localhost:5000/monitor
```

You will see:

- Total attacks captured.
- Most attacked endpoint + its hit count.
- A live-updating table of requests with:
  - Timestamp, IP, method, endpoint, AI response preview.
- Cyber / hacker theme:
  - Dark background (`#0d1117 / #0a0a0a`),
  - Neon green text (`#00ff41 / #00ff00`),
  - Monospace font (`JetBrains Mono` / `Courier New`).

The frontend polls `/api/logs` every **2 seconds** using JavaScript `fetch` + `setInterval`, updating the UI without reloading the page.

### 6.2 Trigger the Trap

Use a browser, `curl`, Postman, Burp, etc.:

```bash
# Simple GET
curl http://localhost:5000/secret_passwords.txt

# POST with JSON
curl -X POST http://localhost:5000/api/users \
     -H "Content-Type: application/json" \
     -d '{"username": "attacker", "role": "admin"}'
```

Any path other than `/monitor` and `/api/logs` will:

1. Hit the catch‑all trap.
2. Be logged in SQLite.
3. Receive an AI or fallback JSON response.
4. Show up on the dashboard within ~2 seconds.

---

## 7. Deployment Notes

- Consider putting Chameleon behind a reverse proxy (Nginx, Caddy, etc.) and:
  - Forward `X-Forwarded-For` so IP logging is accurate.
  - Restrict `/monitor` to your IP or VPN.
- This is a **honeypot**, not an application for serving real users:
  - Run it isolated from production systems (container, VM, separate network segment).
  - Treat all incoming data as hostile.

---

## 8. Customization

- **Persona**: Edit the `system_instruction` string in `ai_engine.py` to change the “flavor” of the fake server (e.g. healthcare, IoT, industrial control, etc.).
- **Response shape**: You can enforce certain keys post‑generation by:
  - Parsing the JSON with `json.loads`,
  - Mutating/enriching it,
  - Re‑encoding with `json.dumps`.
- **Dashboard**: Extend `dashboard.html` to add filters, pagination, or drill‑down views into `payload_data` and `ai_response_sent`.

---

## 9. Troubleshooting

### Groq Client Initialization Error (`proxies` parameter)

If you see an error like:
```
Failed to initialize Groq client: Client.__init__() got an unexpected keyword argument 'proxies'
```

**Solution:**
1. Upgrade the Groq library to the latest version:
   ```bash
   pip install --upgrade groq
   ```

2. If the error persists, ensure your `.env` file has the correct `GROQ_API_KEY`:
   ```bash
   GROQ_API_KEY=your-actual-api-key-here
   ```

3. Restart your Flask server after upgrading.

The code now includes automatic fallback initialization methods to handle version differences.

### Model Decommissioned Error

If you see:
```
The model `llama-3.1-70b-versatile` has been decommissioned
```

**Solution:** The code now uses `llama-3.3-70b-versatile`. If you need to use a different model, edit `ai_engine.py` line 121 and replace the model name with one from [Groq's model list](https://console.groq.com/docs/models).

---

## 10. Quick Start

1. Clone/download the project.
2. (Optional) Create and activate a virtualenv.
3. Run `pip install -r requirements.txt`.
4. Create `.env` with `GROQ_API_KEY`, `SESSION_SECRET`, `FLASK_DEBUG`.
5. Run `python app.py`.
6. Visit `http://localhost:5000/monitor` and start hitting random endpoints to watch the honeypot come alive.


