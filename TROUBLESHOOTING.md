# Troubleshooting Vercel Deployment

## If you see "FUNCTION_INVOCATION_FAILED" error:

### Step 1: Check Function Logs

1. Go to your Vercel Dashboard
2. Click on your project
3. Go to **Deployments** tab
4. Click on the failed deployment
5. Click on **Function Logs** tab
6. Look for Python errors/tracebacks

The logs will show the **actual error** that's causing the crash.

### Step 2: Common Issues and Fixes

#### Issue: Import Error / Module Not Found

**Symptoms**: Error like `ModuleNotFoundError: No module named 'app'`

**Fix**: 
- Make sure `api/index.py` exists
- Verify all Python files are in the root directory (not in subdirectories)
- Check that `vercel.json` points to `api/index.py`

#### Issue: Database Initialization Error

**Symptoms**: Error related to SQLite or `/tmp` directory

**Fix**:
- The app now uses `/tmp/honeypot.db` on Vercel
- If `/tmp` doesn't work, it falls back to `/var/task`
- Check Function Logs to see which path is being used

#### Issue: Missing Environment Variables

**Symptoms**: Error about `GROQ_API_KEY` or initialization failing silently

**Fix**:
1. Go to Project Settings → Environment Variables
2. Add:
   - `GROQ_API_KEY` = your Groq API key
   - `SESSION_SECRET` = any random string
   - `FLASK_DEBUG` = `0`
3. Make sure they're added for **Production**, **Preview**, and **Development**
4. Redeploy

#### Issue: Template/Static Files Not Found

**Symptoms**: Error like `TemplateNotFound` or 404 on CSS files

**Fix**:
- Verify `templates/` folder exists with `dashboard.html`
- Verify `static/` folder exists with `style.css`
- Check that these folders are committed to git

#### Issue: Groq API Error

**Symptoms**: Error initializing Groq client

**Fix**:
- Make sure `GROQ_API_KEY` is set correctly
- The app will use fallback responses if Groq fails, so this shouldn't crash the app
- Check Groq API key is valid at [console.groq.com](https://console.groq.com)

### Step 3: Test Locally with Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Test locally (simulates Vercel environment)
vercel dev
```

This will help identify issues before deploying.

### Step 4: Verify Project Structure

Your project should have this structure:

```
.
├── api/
│   └── index.py          # Must exist!
├── app.py                # Main Flask app
├── ai_engine.py
├── models.py
├── requirements.txt      # Must exist!
├── runtime.txt           # Python version
├── vercel.json           # Vercel config
├── templates/
│   └── dashboard.html    # Must exist!
└── static/
    └── style.css         # Must exist!
```

### Step 5: Check Build Logs

1. Go to Deployment → **Build Logs**
2. Look for:
   - Python version (should be 3.11)
   - Dependencies installing correctly
   - Any build errors

### Step 6: Common Fixes

1. **Redeploy**: Sometimes a simple redeploy fixes transient issues
2. **Clear Cache**: In Vercel dashboard, try "Redeploy" with "Clear Build Cache"
3. **Check Git**: Make sure all files are committed and pushed to GitHub
4. **Environment Variables**: Double-check all env vars are set correctly

### Step 7: Get Help

If you're still stuck:

1. **Copy the exact error** from Function Logs
2. **Check**:
   - All files are committed to git
   - Environment variables are set
   - `requirements.txt` has all dependencies
3. **Share**:
   - The error message from Function Logs
   - Your `vercel.json` content
   - Your project structure

### Debug Mode

To see more detailed errors, temporarily set:
- `FLASK_DEBUG` = `1` in environment variables
- This will show full tracebacks in responses (remove after debugging!)

---

**Remember**: The Function Logs are your best friend - they show exactly what's wrong!
