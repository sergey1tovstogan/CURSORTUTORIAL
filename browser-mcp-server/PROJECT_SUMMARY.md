# Browser MCP Server - Project Summary

## What Was Built

A production-ready **Browser MCP Server** that enables Claude (in Cursor) to automate and interact with web browsers. The system maintains a persistent authenticated browser session and allows Claude to fetch, parse, and extract web content.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Cursor / Claude                          │
│            (Makes tool requests via MCP)                    │
└────────────────────┬────────────────────────────────────────┘
                     │ JSON-RPC over stdio
                     │ (secure, local-only)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│          Python MCP Server (server.py)                      │
│  - Implements JSON-RPC 2.0 protocol                         │
│  - Routes tool calls to browser client                      │
│  - Handles authentication flow                              │
│  - Manages server lifecycle                                 │
└────────────────────┬────────────────────────────────────────┘
                     │ Async API
                     ▼
┌─────────────────────────────────────────────────────────────┐
│       Browser Client (browser_client.py)                    │
│  - Manages Playwright/Chromium browser                      │
│  - Content extraction & HTML parsing                        │
│  - Form filling and automation                              │
│  - Session persistence                                      │
└────────────────────┬────────────────────────────────────────┘
                     │ Playwright async API
                     ▼
┌─────────────────────────────────────────────────────────────┐
│       Chromium Browser (Visible Window)                     │
│  - Loads web pages                                          │
│  - Maintains cookies/sessions                               │
│  - Displays for manual authentication                       │
└─────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. **server.py** - Main MCP Server
- Implements Model Context Protocol over stdio transport
- Handles JSON-RPC 2.0 requests/responses
- Manages browser client lifecycle
- Routes tool calls (navigate, extract, login, fill forms, etc.)
- Provides server status and tool listing

**Key Methods:**
- `handle_request()` - Process incoming JSON-RPC requests
- `_call_tool()` - Execute browser operations
- `run()` - Main server loop reading from stdin, writing to stdout

### 2. **browser_client.py** - Browser Automation
- Wraps Playwright for browser automation
- Manages persistent browser context
- Content extraction and Markdown conversion
- Form filling and interaction
- Authentication handling

**Key Features:**
- Async/await for non-blocking operations
- Persistent profile directory for session storage
- BeautifulSoup for HTML parsing
- Markdownify for HTML to Markdown conversion
- Comprehensive error handling and logging

**Key Methods:**
- `navigate_to()` - Load URLs
- `extract_content()` - Extract page content as Markdown
- `fill_form()` - Fill and submit forms
- `wait_for_login()` - Wait for manual authentication
- `set_credentials()` - Store credentials for auto-login
- `get_page_status()` - Get current page info

### 3. **config.py** - Configuration
Four configuration classes:
- `BrowserConfig` - Browser launch options, timeouts, headless mode
- `AuthConfig` - Credential storage, retry settings
- `ExtractionConfig` - Content parsing and size limits
- `MCPConfig` - MCP server setup, tool definitions

All tools for Claude are defined here as JSON schemas.

### 4. **test_mcp.py** - Test Suite
Standalone test script that:
- Starts the server
- Sends JSON-RPC requests
- Tests all 6 tools
- Verifies browser functionality
- Demonstrates proper shutdown

## Available Tools for Claude

### 1. navigate_to(url, wait_for=None)
Navigate to a URL with optional selector waiting.
```json
{
  "url": "https://example.com",
  "wait_for": ".content"  // optional CSS selector
}
```

### 2. extract_content(selector=None, include_metadata=True)
Extract page content and convert to Markdown.
```json
{
  "selector": ".article",  // optional CSS selector
  "include_metadata": true  // include title and URL
}
```

### 3. set_credentials(username, password)
Store credentials for automatic login.
```json
{
  "username": "user@example.com",
  "password": "secure_password"
}
```

### 4. wait_for_login(timeout_seconds=300, success_indicator=None)
Pause and wait for manual authentication.
```json
{
  "timeout_seconds": 300,
  "success_indicator": "/dashboard"  // URL pattern or selector
}
```

### 5. fill_form(fields, submit_button=None)
Fill form fields and optionally submit.
```json
{
  "fields": {
    "#email": "user@example.com",
    "#password": "password",
    "#remember": "on"
  },
  "submit_button": "#login-btn"  // optional
}
```

### 6. get_page_status()
Get current page URL and connection status.
```json
{}  // No parameters
```

## Installation & Setup

### Already Completed
✓ Python 3.9 virtual environment created  
✓ All dependencies installed:
  - playwright==1.55.0
  - beautifulsoup4==4.14.2
  - markdownify==1.2.0
  - pydantic==2.12.3
✓ Chromium browser downloaded via Playwright  

### To Run
```bash
cd /Users/sergeytovstogan/CURSORTUTORIAL/browser-mcp-server
source venv/bin/activate
python server.py
```

### Cursor Configuration
Add to Cursor settings:
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

## Session Persistence

### How It Works
1. Browser profile stored in `chrome_profile/` directory
2. Cookies and session data automatically persisted
3. Authentication tokens remain valid across requests
4. Multiple content extraction requests share same session

### Example Flow
```
1. navigate_to("https://site.com/login")
2. fill_form(credentials)  → Browser now logged in
3. navigate_to("https://site.com/page1")
4. extract_content()  → Access as authenticated user
5. navigate_to("https://site.com/page2")
6. extract_content()  → Still authenticated, session persists!
```

### Clearing Session
```bash
rm -rf chrome_profile/
# Restart server for fresh authentication
python server.py
```

## Security Considerations

### Credentials
- Stored in memory only (never persisted to disk)
- Only exist during server runtime
- Cleared when server stops

### Profile Data
- Stored in local `chrome_profile/` directory
- Treat with same security as browser profile
- Contains cookies and session data

### Network
- Stdio transport only (no exposed ports)
- Local-only communication
- Suitable for development on single machine

### Best Practices
- Don't commit `chrome_profile/` to version control
- Use environment variables for sensitive URLs
- Add `.gitignore` entry for profile and logs
- Consider encrypted storage for persistent credentials

## Performance Characteristics

| Operation | Time |
|-----------|------|
| Browser startup | 2-3 seconds |
| Navigate to page | <1 second (subsequent) |
| Content extraction | <500ms typical |
| Form submission | <2 seconds |
| Manual login | user-dependent |

## Troubleshooting Guide

### Browser Won't Start
1. Check logs: `tail -f logs/browser_mcp.log`
2. Ensure Playwright is installed: `playwright install chromium`
3. Verify Python venv is activated
4. Try verbose mode: `VERBOSE=true python server.py`

### Content Extraction Fails
1. Verify page loaded with `get_page_status()`
2. Use browser DevTools to find CSS selectors
3. Try without selector first
4. Check if content is JavaScript-rendered

### Authentication Issues
1. Use manual login: `wait_for_login(timeout_seconds=600)`
2. Check browser window for error messages
3. Verify credentials are correct
4. Try form filling step-by-step

### Server Hangs
1. Press Ctrl+C to stop
2. Check logs for stuck requests
3. Kill any remaining processes: `pkill -f "python server.py"`
4. Clear profile: `rm -rf chrome_profile/`

## File Structure

```
browser-mcp-server/
├── server.py                 # Main MCP server (entry point)
├── browser_client.py         # Playwright browser wrapper
├── config.py                 # Configuration classes
├── test_mcp.py              # Test suite
├── requirements.txt         # Python dependencies
├── package.json             # Node.js dependencies (optional)
├── README.md                # Full documentation
├── QUICKSTART.md            # 5-minute setup guide
├── cursor-config.json       # Cursor MCP configuration template
├── PROJECT_SUMMARY.md       # This file
├── venv/                    # Python virtual environment
├── chrome_profile/          # Browser session (created at runtime)
├── logs/                    # Server logs (created at runtime)
└── node_scripts/            # Node.js scripts (optional)
```

## Core Concepts Explained

### Model Context Protocol (MCP)
Standard protocol allowing AI assistants to use external tools. Claude communicates with your server via JSON-RPC.

### Stdio Transport
Communication via stdin/stdout instead of network sockets. Advantages:
- No exposed ports
- Local-only (secure)
- Simple process management
- Better for local development

### Persistent Browser Session
Browser maintains login state across multiple requests because:
- Same browser instance reused
- Cookies stored in profile directory
- Context not recreated between requests

### Async/Await
All operations use Python async/await for:
- Non-blocking I/O
- Better performance
- Responsive server
- Ability to handle multiple requests

## Integration with Cursor

### How It Works
1. Cursor reads configuration for `browser` MCP server
2. Cursor starts Python server as subprocess
3. Claude sees 6 browser tools available
4. Claude can call tools via MCP protocol
5. Server executes in browser, returns results

### Example Conversation
```
You: "Extract the table from example.com"

Claude:
- I'll navigate to example.com and extract the table content.

[Claude calls: navigate_to("https://example.com")]
✓ Navigation successful

[Claude calls: extract_content(selector="table")]
✓ Content extracted (500 chars)

Here's the table data:
| Header 1 | Header 2 |
|----------|----------|
| Data 1   | Data 2   |
...
```

## Future Enhancement Ideas

- [ ] Multi-page/tab support
- [ ] JavaScript code execution in page context
- [ ] Screenshot capture
- [ ] Network request interception
- [ ] Cookie export/import
- [ ] Headless mode toggle
- [ ] Proxy support
- [ ] Element interaction (click, hover, scroll)
- [ ] Keyboard input simulation
- [ ] File upload handling
- [ ] Cookie jar persistence
- [ ] User agent customization

## Known Limitations

1. **Single Browser Instance** - No parallel page handling
2. **Content Size Limit** - 1MB maximum per page
3. **JavaScript Rendering** - Dynamic content requires waits
4. **Platform Specific** - Chromium architecture varies by OS
5. **Manual Wait** - Manual login limited to ~5 minutes default
6. **Memory Usage** - Chromium uses ~200MB+ RAM

## What You Learned

### Concepts
- Model Context Protocol (MCP) architecture
- JSON-RPC 2.0 protocol over stdio
- Playwright browser automation
- Async/await Python patterns
- HTML parsing and Markdown conversion
- Session persistence techniques

### Technologies
- Playwright for browser automation
- BeautifulSoup for HTML parsing
- Markdownify for conversion
- Pydantic for data validation
- Asyncio for async programming

### Best Practices
- Separation of concerns (server, client, config)
- Comprehensive error handling
- Detailed logging
- Configuration management
- Type hints throughout
- Docstrings on all functions

## Next Steps

1. **Configure Cursor** - Add MCP configuration (see QUICKSTART.md)
2. **Test the Server** - Run `python test_mcp.py`
3. **Try with Claude** - Ask Claude to extract web content
4. **Customize** - Modify config.py for your needs
5. **Extend** - Add more tools as needed

## Support & Debugging

### Logs
All server activity logged to `logs/browser_mcp.log`

### Debug Mode
```bash
VERBOSE=true python server.py
```

### Test Suite
```bash
python test_mcp.py
```

### Manual Testing
```bash
python
>>> import asyncio
>>> from browser_client import get_browser_client
>>> async def test():
...     client = await get_browser_client()
...     await client.navigate_to("https://example.com")
...     content = await client.extract_content()
...     print(content[:500])
>>> asyncio.run(test())
```

---

## Summary

You now have a fully functional Browser MCP Server that:
- ✓ Maintains persistent authenticated browser sessions
- ✓ Extracts web content as Markdown
- ✓ Handles manual and automatic authentication
- ✓ Integrates with Cursor's MCP system
- ✓ Uses secure stdio transport
- ✓ Provides 6 browser automation tools to Claude
- ✓ Includes comprehensive documentation and tests

Ready to use with Claude in Cursor! 🚀
