# Testing Your Chameleon Honeypot on Vercel

Your honeypot is live at: **https://chameleon-virid.vercel.app**

## How to Test the Honeypot

### 1. View the Dashboard

Visit the monitoring dashboard:
```
https://chameleon-virid.vercel.app/monitor
```

This shows:
- Total attacks captured
- Most attacked endpoint
- Live feed of all requests

### 2. Trigger the Honeypot (Attack It!)

The honeypot will respond to **ANY path** you try. Here are some examples:

#### Using a Browser

Just visit any URL like:
- `https://chameleon-virid.vercel.app/admin`
- `https://chameleon-virid.vercel.app/api/users`
- `https://chameleon-virid.vercel.app/wp-login.php`
- `https://chameleon-virid.vercel.app/secret_passwords.txt`
- `https://chameleon-virid.vercel.app/.env`

**Note**: Browsers will show JSON responses. Open the browser's developer console (F12) to see the full response.

#### Using curl (Command Line)

```bash
# Simple GET request
curl https://chameleon-virid.vercel.app/admin

# POST with JSON
curl -X POST https://chameleon-virid.vercel.app/api/users \
     -H "Content-Type: application/json" \
     -d '{"username": "test", "password": "test123"}'

# Try different endpoints
curl https://chameleon-virid.vercel.app/api/secret
curl https://chameleon-virid.vercel.app/config.php
curl https://chameleon-virid.vercel.app/.git/config
```

#### Using Postman or Similar Tools

1. Create a new request
2. Set URL to: `https://chameleon-virid.vercel.app/ANY_PATH_HERE`
3. Try different HTTP methods: GET, POST, PUT, DELETE
4. Add JSON body for POST/PUT requests
5. Send the request

#### Using JavaScript (Browser Console)

Open browser console on any page and run:

```javascript
// GET request
fetch('https://chameleon-virid.vercel.app/admin')
  .then(r => r.json())
  .then(data => console.log(data));

// POST request
fetch('https://chameleon-virid.vercel.app/api/users', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'test', role: 'admin'})
})
  .then(r => r.json())
  .then(data => console.log(data));
```

### 3. Watch the Dashboard Update

After making requests:
1. Go back to: `https://chameleon-virid.vercel.app/monitor`
2. The dashboard auto-refreshes every 2 seconds
3. You'll see your requests appear in the "Attack Log Feed" table

### 4. Share with Others

Share these URLs with friends/colleagues to test:

**Dashboard (Monitoring)**:
```
https://chameleon-virid.vercel.app/monitor
```

**Honeypot Endpoints** (any of these will work):
```
https://chameleon-virid.vercel.app/admin
https://chameleon-virid.vercel.app/api/users
https://chameleon-virid.vercel.app/secret
https://chameleon-virid.vercel.app/wp-login.php
```

## What Happens When You "Attack"

1. **Request is logged**: Your IP, method, endpoint, payload, and user agent are recorded
2. **AI generates response**: Groq AI creates a realistic JSON response
3. **Response sent**: You receive the fake API response
4. **Appears on dashboard**: Within 2 seconds, your request shows up on the monitoring dashboard

## Example Responses

The honeypot will return realistic-looking JSON like:

```json
{
  "status": "ok",
  "users": [
    {"id": 1, "username": "admin", "role": "administrator"},
    {"id": 2, "username": "user1", "role": "member"}
  ],
  "timestamp": "2025-01-18T12:00:00Z",
  "server": "legacy-enterprise-api"
}
```

## Tips for Testing

1. **Try different HTTP methods**: GET, POST, PUT, DELETE all work
2. **Try different paths**: Any path works - be creative!
3. **Send different payloads**: JSON, form data, raw data
4. **Use different tools**: Browser, curl, Postman, Burp Suite, etc.
5. **Watch the dashboard**: See all your requests appear in real-time

## Troubleshooting

### CSS/UI Not Loading

If the dashboard looks unstyled:
- Check browser console for 404 errors on `/static/style.css`
- Hard refresh the page (Ctrl+F5 or Cmd+Shift+R)
- Clear browser cache

### Requests Not Appearing on Dashboard

- Wait 2-3 seconds (dashboard auto-refreshes every 2 seconds)
- Check that you're hitting the correct URL
- Verify the request was successful (check browser network tab)

### JSON Not Displaying in Browser

- Browsers may show raw JSON - this is normal
- Use browser developer tools (F12) → Network tab to see full response
- Or use curl/Postman for better JSON viewing

---

**Have fun testing your honeypot!** 🎉
