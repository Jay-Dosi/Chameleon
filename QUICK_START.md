# Quick Start Guide - Chameleon Honeypot

## Your Deployed Honeypot

**Dashboard URL**: https://chameleon-virid.vercel.app/monitor

## How Users Can Test It

### Option 1: Share the Dashboard URL
Share this link with anyone:
```
https://chameleon-virid.vercel.app/monitor
```

They can:
1. View the dashboard
2. Open a new tab and visit any endpoint like:
   - `https://chameleon-virid.vercel.app/admin`
   - `https://chameleon-virid.vercel.app/api/users`
   - `https://chameleon-virid.vercel.app/secret`
3. Go back to the dashboard tab to see their requests appear!

### Option 2: Direct Endpoint Testing

Users can directly visit any of these URLs in their browser:
- `https://chameleon-virid.vercel.app/admin`
- `https://chameleon-virid.vercel.app/api/users`
- `https://chameleon-virid.vercel.app/wp-login.php`
- `https://chameleon-virid.vercel.app/.env`
- `https://chameleon-virid.vercel.app/secret_passwords.txt`

**Any path works!** The honeypot will respond to literally any URL.

### Option 3: Using curl (Command Line)

```bash
curl https://chameleon-virid.vercel.app/admin
curl https://chameleon-virid.vercel.app/api/users
curl -X POST https://chameleon-virid.vercel.app/api/users -H "Content-Type: application/json" -d '{"test": "data"}'
```

## What Happens

1. User visits any endpoint (e.g., `/admin`)
2. Honeypot generates a realistic JSON response using AI
3. Response is logged and appears on the dashboard
4. User sees a believable API response

## Dashboard Features

- **Real-time updates**: Refreshes every 2 seconds
- **Attack statistics**: Total attacks, most attacked endpoint
- **Live feed**: See all requests as they happen
- **Cyber theme**: Dark, hacker-style UI

## Troubleshooting

### CSS Not Loading?

If the dashboard looks unstyled:
1. Hard refresh: `Ctrl+F5` (Windows) or `Cmd+Shift+R` (Mac)
2. Clear browser cache
3. Check browser console (F12) for errors

### Requests Not Showing?

- Wait 2-3 seconds (auto-refresh interval)
- Make sure you're hitting the correct URL
- Check browser network tab to verify request succeeded

---

**For detailed testing instructions, see [TESTING_GUIDE.md](TESTING_GUIDE.md)**
