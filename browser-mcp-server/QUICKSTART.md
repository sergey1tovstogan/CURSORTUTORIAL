# Browser MCP Server - Quick Start Guide

Get the Browser MCP Server running in 5 minutes!

## Step 1: Already Done! ✓

Environment is already set up with:
- Python virtual environment: `venv/`
- All dependencies installed
- Chromium browser downloaded

Verify:
```bash
cd /Users/sergeytovstogan/CURSORTUTORIAL/browser-mcp-server
source venv/bin/activate
python -c "import playwright; print('✓ Playwright installed')"
```

## Step 2: Start the Server

```bash
cd /Users/sergeytovstogan/CURSORTUTORIAL/browser-mcp-server
source venv/bin/activate
python server.py
```

You should see:
```
2025-01-20 10:00:00 - browser_client - INFO - Starting Playwright...
2025-01-20 10:00:05 - browser_client - INFO - Browser started successfully
2025-01-20 10:00:05 - server - INFO - MCP server running on stdio transport
```

A Chromium browser window will also open.

## Step 3: Test the Server (Optional)

In another terminal:

```bash
cd /Users/sergeytovstogan/CURSORTUTORIAL/browser-mcp-server
source venv/bin/activate
python test_mcp.py
```

This will:
1. Navigate to example.com
2. Extract content as Markdown
3. Test all available tools
4. Shutdown cleanly

## Step 4: Configure Cursor

### Option A: Through Cursor UI
1. Open Cursor Settings
2. Search for "MCP"
3. Find "Model Context Protocol" section
4. Click "Add Server"
5. Enter:
   - **Name:** `browser`
   - **Command:** `/Users/sergeytovstogan/CURSORTUTORIAL/browser-mcp-server/venv/bin/python`
   - **Args:** `/Users/sergeytovstogan/CURSORTUTORIAL/browser-mcp-server/server.py`

### Option B: Manual JSON Config
1. Open Cursor settings file (usually `~/.cursor/settings.json` or similar)
2. Add:

```json
{
  "mcpServers": {
    "browser": {
      "command": "/Users/sergeytovstogan/CURSORTUTORIAL/browser-mcp-server/venv/bin/python",
      "args": ["/Users/sergeytovstogan/CURSORTUTORIAL/browser-mcp-server/server.py"],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

3. Save and restart Cursor

## Step 5: Use with Claude

Now Claude in Cursor has access to browser tools!

### Example 1: Extract Website Content

**You:** "Extract the main content from example.com as Markdown"

**Claude will:**
1. Call `navigate_to("https://example.com")`
2. Call `extract_content()`
3. Return Markdown formatted text

### Example 2: Login and Extract Data

**You:** "Log in to our corporate site with username 'john' and password 'secret123', then extract all tables from the dashboard"

**Claude will:**
1. Call `navigate_to("https://corp-site.com/login")`
2. Call `fill_form()` with login credentials
3. Call `wait_for_login()` if needed
4. Call `extract_content()` with table selectors

### Example 3: Multiple Pages

**You:** "Visit pages 1, 2, and 3 of the report and extract all content"

**Claude will:**
1. Call `navigate_to(page1_url)`
2. Call `extract_content()`
3. Repeat for pages 2 and 3

Session persists - browser stays logged in!

## Available Tools for Claude

```
1. navigate_to(url, wait_for)
   - Go to a URL
   
2. extract_content(selector, include_metadata)
   - Get page content as Markdown
   
3. set_credentials(username, password)
   - Store credentials for auto-login
   
4. fill_form(fields, submit_button)
   - Fill form fields and submit
   
5. wait_for_login(timeout_seconds, success_indicator)
   - Wait for manual authentication
   
6. get_page_status()
   - Check current page URL and status
```

## Troubleshooting

### Server won't start
```bash
# Check if port/process issue
ps aux | grep server.py
# Kill if needed
pkill -f "python server.py"
# Try again
python server.py
```

### Browser window doesn't appear
- Check if headless mode is enabled in `config.py`
- Set `HEADLESS = False` if needed

### Content extraction fails
- Use browser DevTools to find correct CSS selectors
- Try without selector first: `extract_content(selector=None)`

### Authentication issues
- Use `wait_for_login()` for manual authentication
- Check logs: `tail -f logs/browser_mcp.log`

### Clear session and start fresh
```bash
rm -rf chrome_profile/
# Restart server
python server.py
```

## Next Steps

1. **Read the full README** for detailed documentation
2. **Check logs**: `logs/browser_mcp.log` for debugging
3. **Customize config.py** for your needs
4. **Add more tools** by editing browser_client.py and server.py

## Getting Help

1. Check `logs/browser_mcp.log` for errors
2. Enable verbose logging: `VERBOSE=true python server.py`
3. Review README.md troubleshooting section
4. Run test script: `python test_mcp.py`

---

**That's it!** You're now ready to use Claude with browser automation. 🚀
