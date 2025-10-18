# Browser MCP Server

A Python-based Model Context Protocol (MCP) server that provides Claude with browser automation capabilities. Features persistent authentication, content extraction, and form filling through a visible Chrome instance.

## Architecture

```
Cursor/Claude → Python MCP Server → Playwright Browser (Chromium)
                (stdio transport)      (persistent profile)
```

### Key Features

- **Persistent Browser Session**: Maintains cookies and session data across requests
- **Visible Browser**: Keep Chrome window open for manual authentication
- **Content Extraction**: Convert web pages to Markdown format
- **Form Automation**: Fill forms and interact with pages
- **Authentication Support**: Handle both manual and automatic login flows
- **Stdio Transport**: Secure local-only communication with zero network overhead

## Prerequisites

- Python 3.9+
- Chromium browser (installed via Playwright)

## Installation

### 1. Setup Python Virtual Environment

```bash
cd browser-mcp-server
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Download Browser

```bash
playwright install chromium
```

## Running the Server

### Start the MCP Server

```bash
source venv/bin/activate
python server.py
```

The server will:
1. Launch Chromium browser (visible window)
2. Start listening for JSON-RPC requests on stdin
3. Respond with results on stdout
4. Create persistent profile in `chrome_profile/` directory

### Logs

Server logs are written to `logs/browser_mcp.log` for debugging.

## Cursor Integration

### Configure Cursor MCP

Add to your Cursor settings (`.cursor/settings.json` or equivalent):

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

Replace the paths with your actual paths.

## Available Tools for Claude

### 1. navigate_to
Navigate to a URL in the persistent browser.

```python
navigate_to(
    url: str,                    # URL to navigate to
    wait_for: Optional[str] = None  # CSS selector to wait for before returning
)
```

### 2. extract_content
Extract page content and convert to Markdown.

```python
extract_content(
    selector: Optional[str] = None,     # CSS selector for specific content
    include_metadata: bool = True        # Include title and URL
)
```

### 3. set_credentials
Store username and password for automatic login (stored in memory only).

```python
set_credentials(
    username: str,
    password: str
)
```

### 4. wait_for_login
Pause and wait for manual authentication in the browser.

```python
wait_for_login(
    timeout_seconds: int = 300,           # Max wait time
    success_indicator: Optional[str] = None # URL pattern or selector
)
```

### 5. fill_form
Fill form fields and optionally submit.

```python
fill_form(
    fields: Dict[str, str],          # Selector: value pairs
    submit_button: Optional[str] = None  # Submit button selector
)
```

### 6. get_page_status
Get current page URL and connection status.

```python
get_page_status()
```

## Usage Examples

### Example 1: Extract Corporate Data

```python
# Claude commands:
1. navigate_to("https://corporate-site.com/data")
2. wait_for_login(timeout_seconds=300, success_indicator="/dashboard")
3. extract_content(selector=".main-content", include_metadata=True)
```

### Example 2: Automatic Login and Extract

```python
# Claude commands:
1. set_credentials("username", "password")
2. navigate_to("https://corporate-site.com/login")
3. fill_form(
     fields={
       "#username": "{{username}}",
       "#password": "{{password}}"
     },
     submit_button="#submit"
   )
4. extract_content()
```

### Example 3: Multiple Content Extractions

```python
# First extraction
1. navigate_to("https://site.com/page1")
2. extract_content()

# Session persists, navigate again
3. navigate_to("https://site.com/page2")
4. extract_content()
```

## Session Persistence

### How It Works

1. Browser profile stored in `chrome_profile/` directory
2. Cookies, session data, and authentication tokens persist
3. Each request uses the same browser instance
4. Authentication happens once per server startup

### Clearing Session

To reset authentication and start fresh:

```bash
rm -rf chrome_profile/
# Restart the server
```

## Authentication Flows

### Manual Authentication

Use when automatic login isn't available:

```python
# Tell Claude to:
1. navigate_to("https://site.com")
2. wait_for_login(timeout_seconds=300, success_indicator="/after-login-page")
# Browser window appears, you authenticate manually
# Server detects successful login and continues
```

### Automatic Authentication

Use when login can be automated:

```python
# Tell Claude to:
1. set_credentials("user", "pass")
2. navigate_to("https://site.com/login")
3. fill_form({
     "#email": "user",
     "#password": "pass"
   }, submit_button="#login")
4. extract_content()
```

### Re-authentication

If authentication fails or expires during extraction:

```python
# Claude can retry:
1. wait_for_login(timeout_seconds=300)
2. extract_content()
```

## Configuration

Edit `config.py` to customize:

- **BrowserConfig**: Browser launch options, timeouts, headless mode
- **AuthConfig**: Authentication retry behavior
- **ExtractionConfig**: Content extraction settings
- **LogConfig**: Logging level and verbosity

## Troubleshooting

### Browser Won't Launch

```bash
# Enable verbose logging
VERBOSE=true python server.py

# Check logs
cat logs/browser_mcp.log
```

### Content Not Extracting

1. Navigate to the page first with correct selector
2. Use `get_page_status()` to verify page loaded
3. Check if selector is correct with browser DevTools

### Authentication Fails

1. Use `wait_for_login()` for manual authentication
2. Check logs for error messages
3. Try with `timeout_seconds=600` for slower networks

### Server Hangs

- Press Ctrl+C to stop server
- Check `logs/browser_mcp.log` for error details
- Restart with fresh profile: `rm -rf chrome_profile/`

## Development

### Project Structure

```
browser-mcp-server/
├── server.py              # Main MCP server (entry point)
├── browser_client.py      # Playwright browser wrapper
├── config.py              # Configuration classes
├── requirements.txt       # Python dependencies
├── package.json           # Node.js dependencies (optional)
├── chrome_profile/        # Persistent browser session (created at runtime)
├── logs/                  # Server logs (created at runtime)
└── README.md             # This file
```

### Adding New Tools

1. Add tool definition to `MCPConfig.TOOLS` in `config.py`
2. Implement handler in `BrowserClient` class in `browser_client.py`
3. Add tool call handler in `_call_tool()` method in `server.py`

### Testing

Create a test script to send JSON-RPC requests:

```python
import json
import subprocess

# Start server
proc = subprocess.Popen(
    ["python", "server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

# Send request
request = {
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
}
proc.stdin.write(json.dumps(request) + '\n')
proc.stdin.flush()

# Read response
response = proc.stdout.readline()
print(json.loads(response))
```

## Security Considerations

- **Credentials**: Stored in memory only, never persisted to disk
- **Profile Data**: Stored locally in `chrome_profile/` - handle with care
- **Network**: Stdio transport means no exposed ports
- **Local Only**: Server only runs locally, suitable for development

## Performance

- First navigation: ~2-3 seconds (browser startup)
- Subsequent navigations: <1 second
- Content extraction: <500ms for typical pages
- Session reuse: Near-instant for repeated requests

## Limitations

- Single browser instance (no parallel requests)
- Content extraction limited to 1MB per page
- Manual authentication timeout: 5 minutes default
- Chromium on macOS requires specific permissions

## Future Improvements

- [ ] Multi-tab support
- [ ] JavaScript execution
- [ ] Screenshot capture
- [ ] Network interception
- [ ] Cookie export/import
- [ ] Headless mode option

## License

MIT

## Support

For issues or questions:
1. Check `logs/browser_mcp.log`
2. Enable verbose logging: `VERBOSE=true python server.py`
3. Review this README's troubleshooting section
