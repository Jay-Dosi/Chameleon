import json
import os
from datetime import datetime

try:
    from groq import Groq
    # Try to import httpx for custom client if needed
    try:
        import httpx
        HAS_HTTPX = True
    except ImportError:
        HAS_HTTPX = False
except ImportError:
    Groq = None
    HAS_HTTPX = False


client = None


def init_groq() -> bool:
    """
    Initialize the Groq client using the GROQ_API_KEY environment variable.
    Returns True if initialization succeeded, False otherwise.
    """
    global client
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        # No API key configured – we will fall back to static responses.
        return False

    # Save proxy-related environment variables temporarily
    # Groq may try to read these and pass them incorrectly
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']
    saved_proxies = {}
    for var in proxy_vars:
        if var in os.environ:
            saved_proxies[var] = os.environ[var]
            # Temporarily remove to prevent Groq from using them incorrectly
            del os.environ[var]

    try:
        # Ensure GROQ_API_KEY is set in environment
        os.environ["GROQ_API_KEY"] = api_key
        
        # Initialize Groq client - it reads GROQ_API_KEY from environment automatically
        # By removing proxy env vars, we prevent the 'proxies' parameter error
        client = Groq()
        
        # Verify client is properly initialized
        if not hasattr(client, 'chat'):
            print("Groq client initialized but missing 'chat' attribute")
            return False
            
        return True
    except TypeError as e:
        error_msg = str(e)
        if 'proxies' in error_msg or 'unexpected keyword' in error_msg:
            # Even after removing proxy env vars, still getting the error
            # Try using a custom httpx client to bypass the proxies issue
            if HAS_HTTPX:
                try:
                    print("Attempting initialization with custom httpx client...")
                    # Create a custom httpx client without proxy settings
                    custom_client = httpx.Client(timeout=30.0)
                    client = Groq(api_key=api_key, http_client=custom_client)
                    if hasattr(client, 'chat'):
                        return True
                except Exception as e2:
                    print(f"Custom httpx client initialization failed: {e2}")
            
            # Fallback: Try using explicit api_key parameter
            try:
                import inspect
                sig = inspect.signature(Groq.__init__)
                valid_params = set(sig.parameters.keys()) - {'self'}
                
                if 'api_key' in valid_params:
                    # Build kwargs with only valid parameters
                    init_kwargs = {'api_key': api_key}
                    client = Groq(**init_kwargs)
                    if hasattr(client, 'chat'):
                        return True
            except Exception as e2:
                print(f"Explicit api_key initialization also failed: {e2}")
                print("This may be a Groq library version issue.")
                print("Try: pip install --upgrade groq httpx")
                return False
        raise e
    except Exception as e:
        print(f"Failed to initialize Groq client: {e}")
        print("Make sure GROQ_API_KEY is set correctly in your .env file")
        print("Try: pip install --upgrade groq")
        return False
    finally:
        # Restore proxy environment variables
        for var, value in saved_proxies.items():
            os.environ[var] = value


def _fallback_success_response() -> str:
    """
    Fallback JSON used when Groq fails or is unavailable.
    Keeps attackers engaged with a boring, legacy-looking success payload.
    """
    payload = {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "server": "legacy-enterprise-api",
        "correlation_id": f"LEG-{int(datetime.utcnow().timestamp())}",
        "message": "Request processed successfully.",
    }
    return json.dumps(payload)


def clean_response(text: str) -> str:
    """
    Strip common Markdown/code-block wrappers and try to isolate pure JSON.
    LLMs sometimes respond with ```json ... ``` or with prose around the JSON.
    """
    cleaned = text.strip()

    # Remove leading fenced code blocks like ```json or ```JSON
    lowered = cleaned.lower()
    if lowered.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]

    # Remove trailing ```
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    cleaned = cleaned.strip()

    # Try to extract the JSON object from surrounding text, if any
    if "{" in cleaned and "}" in cleaned:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        candidate = cleaned[start : end + 1]
        try:
            json.loads(candidate)
            return candidate
        except Exception:
            # Fall through and let caller validate the raw cleaned text
            pass

    return cleaned


def generate_honeypot_response(method: str, endpoint: str, payload: str | None) -> str:
    """
    Ask Groq to hallucinate a realistic JSON response for the attacker's request.
    Always returns a JSON string. On any failure, returns a static success JSON.
    """
    global client

    if client is None:
        if not init_groq():
            return _fallback_success_response()

    system_message = (
        "You are a legacy enterprise backend server for a large financial corporation. "
        "You must generate a realistic, verbose JSON response for the given HTTP request. "
        "The system is old, boring, and highly structured. Use snake_case keys, "
        "and include fields like status codes, timestamps, and audit metadata. "
        "If the method is POST/PUT/PATCH, respond with a success or validation error payload. "
        'If the method is GET, return realistic dummy records such as "accounts", "users", or "transactions". '
        "CRITICAL: OUTPUT ONLY RAW JSON. NO MARKDOWN. NO CODE BLOCKS. NO EXPLANATION TEXT."
    )

    user_prompt = f"""Legacy API Request:
- http_method: {method}
- endpoint: {endpoint}
- payload: {payload if payload else 'null'}

Generate ONLY a valid JSON response body that this legacy system would return."""

    try:
        # Non-streaming variant of the Groq docs pattern:
        # https://console.groq.com/docs
        # Use conservative, widely-supported parameters for compatibility
        chat_completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
            top_p=1,
            max_tokens=1024,
        )

        if not chat_completion or not chat_completion.choices:
            return _fallback_success_response()

        response_text = chat_completion.choices[0].message.content
        if not response_text:
            return _fallback_success_response()

        cleaned = clean_response(response_text)

        # Validate that what we return is valid JSON
        json.loads(cleaned)
        return cleaned

    except json.JSONDecodeError:
        # Groq responded with something non-JSON – keep attacker engaged anyway.
        return _fallback_success_response()
    except Exception as e:
        print(f"Groq API error: {e}")
        return _fallback_success_response()


