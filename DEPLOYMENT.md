# Deploying Chameleon to Vercel

This guide will walk you through deploying the Chameleon API Honeypot to Vercel so that anyone can access and test it.

## Prerequisites

1. **GitHub Account** - Your code needs to be in a GitHub repository
2. **Vercel Account** - Sign up at [vercel.com](https://vercel.com) (free tier is sufficient)
3. **Groq API Key** - Get one at [console.groq.com](https://console.groq.com)

## Step-by-Step Deployment Guide

### Step 1: Push Your Code to GitHub

1. **Initialize Git** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Chameleon API Honeypot"
   ```

2. **Create a GitHub Repository**:
   - Go to [github.com](https://github.com) and create a new repository
   - Name it something like `chameleon-honeypot`
   - **Do NOT** initialize with README, .gitignore, or license (if you already have these)

3. **Push Your Code**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/chameleon-honeypot.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy to Vercel

#### Option A: Deploy via Vercel Dashboard (Recommended)

1. **Go to Vercel Dashboard**:
   - Visit [vercel.com](https://vercel.com) and sign in
   - Click **"Add New..."** → **"Project"**

2. **Import Your GitHub Repository**:
   - You'll see a list of your GitHub repositories
   - Find and click **"Import"** next to your `chameleon-honeypot` repository

3. **Configure Project Settings**:
   - **Framework Preset**: Vercel will auto-detect Python/Flask (or select "Other")
   - **Root Directory**: Leave as `./` (project root)
   - **Build Command**: Leave empty (Vercel handles Python automatically)
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements.txt`

4. **Add Environment Variables**:
   Click **"Environment Variables"** and add:
   
   | Name | Value | Description |
   |------|-------|-------------|
   | `GROQ_API_KEY` | `your-actual-groq-api-key` | Your Groq API key from console.groq.com |
   | `SESSION_SECRET` | `a-long-random-string-here` | A random secret string (e.g., generate with `openssl rand -hex 32`) |
   | `FLASK_DEBUG` | `0` | Set to 0 for production |
   | `VERCEL` | `1` | This tells the app it's running on Vercel (optional, auto-detected) |

   **Important**: Make sure to add these for **Production**, **Preview**, and **Development** environments.

5. **Deploy**:
   - Click **"Deploy"**
   - Wait for the build to complete (usually 1-2 minutes)

#### Option B: Deploy via Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   vercel
   ```
   
   Follow the prompts:
   - Link to existing project or create new
   - Confirm settings
   - Add environment variables when prompted

4. **Set Environment Variables**:
   ```bash
   vercel env add GROQ_API_KEY
   vercel env add SESSION_SECRET
   vercel env add FLASK_DEBUG
   ```

5. **Deploy to Production**:
   ```bash
   vercel --prod
   ```

### Step 3: Verify Deployment

1. **Get Your Deployment URL**:
   - After deployment, Vercel will provide a URL like: `https://your-project-name.vercel.app`
   - You can also find it in the Vercel dashboard

2. **Test the Dashboard**:
   - Visit: `https://your-project-name.vercel.app/monitor`
   - You should see the Chameleon dashboard

3. **Test the Honeypot**:
   - Try accessing any endpoint: `https://your-project-name.vercel.app/admin`
   - Or: `https://your-project-name.vercel.app/api/users`
   - You should get a JSON response, and it should appear on the dashboard

### Step 4: Share Your Deployment

Your honeypot is now live! Share the URL:
- **Dashboard**: `https://your-project-name.vercel.app/monitor`
- **Honeypot**: `https://your-project-name.vercel.app/` (any path works)

## Important Notes

### Database Persistence

⚠️ **Important**: Vercel uses serverless functions with ephemeral storage. The SQLite database is stored in `/tmp` which means:

- **Data persists during a single deployment** (while the function is "warm")
- **Data is lost when**:
  - The function goes "cold" (after ~10 minutes of inactivity)
  - You redeploy the application
  - Vercel scales to a new instance

This is fine for **demo/testing purposes**, but for production use with persistent data, consider:
- Using Vercel Postgres (free tier available)
- Using an external database service (Supabase, PlanetScale, etc.)
- Using Vercel KV (Redis) for temporary storage

### Environment Variables

Make sure all environment variables are set in Vercel:
- Go to your project → **Settings** → **Environment Variables**
- Add variables for **Production**, **Preview**, and **Development**

### Custom Domain (Optional)

1. Go to your project → **Settings** → **Domains**
2. Add your custom domain
3. Follow Vercel's DNS configuration instructions

## Troubleshooting

### Build Fails

- **Check `requirements.txt`**: Make sure all dependencies are listed
- **Check Python version**: Vercel uses Python 3.11 by default (configured in `runtime.txt`)
- **Check build logs**: Click on the failed deployment to see detailed error messages

### App Returns 500 Errors (FUNCTION_INVOCATION_FAILED)

This is the most common error. Here's how to fix it:

1. **Check Function Logs**:
   - Go to your project → **Deployments** → Click on the failed deployment
   - Click **"Function Logs"** tab
   - Look for the actual error message (Python traceback)

2. **Common Causes**:
   - **Missing environment variables**: Make sure `GROQ_API_KEY` and `SESSION_SECRET` are set
   - **Database initialization error**: The app tries to create SQLite DB in `/tmp` - check logs
   - **Import errors**: Check if all Python files are in the correct location
   - **Template/static file paths**: Make sure `templates/` and `static/` folders exist

3. **Debug Steps**:
   ```bash
   # Test locally with Vercel CLI
   npm install -g vercel
   vercel dev
   ```
   This simulates the Vercel environment locally and helps identify issues.

4. **Quick Fixes**:
   - Ensure `api/index.py` exists and properly imports `app`
   - Verify `vercel.json` routes are correct
   - Check that all files are committed to git (Vercel only deploys committed files)
   - Make sure `requirements.txt` has all dependencies

5. **If Still Failing**:
   - Check the exact error in Function Logs
   - Verify environment variables are set for the correct environment (Production/Preview/Development)
   - Try redeploying after making sure all files are pushed to GitHub

### Database Not Working

- **Check logs**: The database is created automatically in `/tmp` on Vercel
- **First request might be slow**: Cold starts can take a few seconds
- **Data disappears**: This is expected behavior (see Database Persistence section above)

### Static Files Not Loading

- **Check `vercel.json`**: Make sure static files route is configured correctly
- **Check file paths**: Static files should be in the `static/` directory

## Updating Your Deployment

Whenever you push changes to GitHub:

1. **Automatic Deployment** (if enabled):
   - Vercel automatically deploys on every push to `main` branch
   - Check the Vercel dashboard for deployment status

2. **Manual Deployment**:
   ```bash
   vercel --prod
   ```

## Project Structure for Vercel

```
.
├── api/
│   └── index.py          # Vercel serverless function entry point
├── app.py                # Main Flask application
├── ai_engine.py          # Groq AI integration
├── models.py             # Database models
├── requirements.txt      # Python dependencies
├── vercel.json          # Vercel configuration
├── templates/
│   └── dashboard.html    # Dashboard template
└── static/
    └── style.css         # Stylesheet
```

## Security Considerations

⚠️ **This is a honeypot** - it's designed to attract attackers:

1. **Don't use this on production systems** - Keep it isolated
2. **Monitor your Groq API usage** - Set up usage alerts
3. **Consider rate limiting** - Add rate limiting if needed (Vercel Pro plan)
4. **Monitor costs** - Vercel free tier has limits, monitor your usage

## Support

- **Vercel Docs**: [vercel.com/docs](https://vercel.com/docs)
- **Vercel Python Runtime**: [vercel.com/docs/concepts/functions/serverless-functions/runtimes/python](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python)
- **Groq API Docs**: [console.groq.com/docs](https://console.groq.com/docs)

---

**Congratulations!** Your Chameleon API Honeypot is now live on Vercel! 🎉
