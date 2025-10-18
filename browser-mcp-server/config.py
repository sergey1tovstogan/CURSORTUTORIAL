"""
Configuration module for Browser MCP Server

Handles settings for browser automation, authentication, and session management.
"""

import os
from pathlib import Path
from typing import Optional


# Project paths
PROJECT_ROOT = Path(__file__).parent
CHROME_PROFILE_DIR = PROJECT_ROOT / "chrome_profile"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create required directories
CHROME_PROFILE_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)


# Browser configuration
class BrowserConfig:
    """Configuration for Playwright browser automation."""
    
    # Use persistent user data directory for session persistence
    USER_DATA_DIR = str(CHROME_PROFILE_DIR)
    
    # Browser launch options
    HEADLESS = False  # Keep visible for authentication
    SLOW_MO = 100  # Slow down operations by 100ms for visibility
    ARGS = [
        "--disable-blink-features=AutomationControlled",
        "--disable-dev-shm-usage",
        "--no-sandbox",
    ]
    
    # Page navigation
    TIMEOUT = 30000  # 30 seconds
    WAIT_FOR_LOAD_STATE = "networkidle"  # Wait for network to be idle
    
    # Browser executable path (optional, Playwright finds it automatically)
    EXECUTABLE_PATH = None


# Authentication configuration
class AuthConfig:
    """Configuration for authentication handling."""
    
    # Credentials are stored in memory during session
    # In production, use a secure credential manager
    stored_credentials: Optional[dict] = None
    
    # Authentication retry settings
    MAX_RETRY_ATTEMPTS = 3
    RETRY_WAIT_MS = 1000
    
    # Session validation interval (ms)
    SESSION_CHECK_INTERVAL = 300000  # 5 minutes


# Content extraction configuration
class ExtractionConfig:
    """Configuration for HTML parsing and content extraction."""
    
    # Markdown conversion settings
    TURNDOWN_OPTIONS = {
        "headingStyle": "atx",
        "br": "\\n",
        "bulletListMarker": "-",
        "codeBlockStyle": "fenced",
    }
    
    # Timeout for element visibility checks
    ELEMENT_TIMEOUT = 10000  # 10 seconds
    
    # Maximum content length to extract (chars)
    MAX_CONTENT_LENGTH = 1000000


# Logging configuration
class LogConfig:
    """Configuration for logging and debugging."""
    
    LOG_DIR = LOGS_DIR
    LOG_FILE = LOG_DIR / "browser_mcp.log"
    
    # Log levels: DEBUG, INFO, WARNING, ERROR
    LOG_LEVEL = "INFO"
    
    # Enable detailed logging for debugging
    VERBOSE = os.getenv("VERBOSE", "false").lower() == "true"


# MCP Server configuration
class MCPConfig:
    """Configuration for Model Context Protocol server."""
    
    # Stdio transport (no network ports)
    TRANSPORT = "stdio"
    
    # Server name and version
    SERVER_NAME = "browser-mcp-server"
    SERVER_VERSION = "1.0.0"
    
    # Tool definitions for Claude
    TOOLS = [
        {
            "name": "navigate_to",
            "description": "Navigate to a URL in the persistent browser",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to navigate to"
                    },
                    "wait_for": {
                        "type": "string",
                        "description": "Wait for selector before returning (optional)",
                        "default": None
                    }
                },
                "required": ["url"]
            }
        },
        {
            "name": "extract_content",
            "description": "Extract page content and convert to Markdown",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "CSS selector for content to extract (optional, extracts all if not provided)",
                        "default": None
                    },
                    "include_metadata": {
                        "type": "boolean",
                        "description": "Include page title and URL in output",
                        "default": True
                    }
                }
            }
        },
        {
            "name": "set_credentials",
            "description": "Set username and password for automatic login",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Username for authentication"
                    },
                    "password": {
                        "type": "string",
                        "description": "Password for authentication"
                    }
                },
                "required": ["username", "password"]
            }
        },
        {
            "name": "wait_for_login",
            "description": "Pause and wait for manual authentication in the browser",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "timeout_seconds": {
                        "type": "integer",
                        "description": "Maximum wait time in seconds",
                        "default": 300
                    },
                    "success_indicator": {
                        "type": "string",
                        "description": "URL pattern or selector indicating successful login",
                        "default": None
                    }
                }
            }
        },
        {
            "name": "fill_form",
            "description": "Fill and submit a form with provided values",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "fields": {
                        "type": "object",
                        "description": "Dictionary of selector: value pairs",
                        "additionalProperties": {"type": "string"}
                    },
                    "submit_button": {
                        "type": "string",
                        "description": "CSS selector for submit button (optional)",
                        "default": None
                    }
                },
                "required": ["fields"]
            }
        },
        {
            "name": "get_page_status",
            "description": "Get current page URL and connection status",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        }
    ]


if __name__ == "__main__":
    print("Browser MCP Server Configuration")
    print(f"Chrome Profile: {BrowserConfig.USER_DATA_DIR}")
    print(f"Logs: {LogConfig.LOG_DIR}")
    print(f"Browser Headless: {BrowserConfig.HEADLESS}")
    print(f"Available Tools: {len(MCPConfig.TOOLS)}")
