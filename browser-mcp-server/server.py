"""
Browser MCP Server

Main MCP server implementation using stdio transport for communicating with Claude.
Implements the Model Context Protocol with JSON-RPC 2.0 over stdin/stdout.
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, Optional, Callable
from dataclasses import dataclass, field

from config import MCPConfig, LogConfig
from browser_client import get_browser_client, close_browser_client

# Setup logging (to file only to avoid interfering with JSON-RPC on stdout)
logging.basicConfig(
    level=getattr(logging, LogConfig.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LogConfig.LOG_FILE),
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class JSONRPCRequest:
    """JSON-RPC 2.0 request."""
    jsonrpc: str = "2.0"
    method: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    id: Optional[int] = None


@dataclass
class JSONRPCResponse:
    """JSON-RPC 2.0 response."""
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[int] = None


class MCPServer:
    """Model Context Protocol server with stdio transport."""
    
    def __init__(self):
        """Initialize MCP server."""
        self.tools = self._build_tools()
        self.browser_client = None
        self.running = True
        
    def _build_tools(self) -> Dict[str, Dict[str, Any]]:
        """Build tool definitions from config."""
        tools = {}
        for tool in MCPConfig.TOOLS:
            tools[tool["name"]] = tool
        return tools
    
    async def initialize(self) -> None:
        """Initialize server and browser."""
        logger.info("Initializing MCP server...")
        self.browser_client = await get_browser_client()
        logger.info("MCP server initialized successfully")
    
    async def shutdown(self) -> None:
        """Shutdown server and cleanup resources."""
        logger.info("Shutting down MCP server...")
        await close_browser_client()
        self.running = False
    
    async def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a JSON-RPC request.
        
        Args:
            request_data: Parsed JSON-RPC request
            
        Returns:
            JSON-RPC response
        """
        try:
            request = JSONRPCRequest(
                jsonrpc=request_data.get("jsonrpc", "2.0"),
                method=request_data.get("method", ""),
                params=request_data.get("params", {}),
                id=request_data.get("id")
            )
            
            logger.info(f"Received request: {request.method}")
            
            # Handle special methods
            if request.method == "initialize":
                return self._response(request.id, {"capabilities": self._get_capabilities()})
            
            elif request.method == "tools/list":
                return self._response(request.id, {"tools": list(self.tools.values())})
            
            elif request.method == "tools/call":
                result = await self._call_tool(request.params)
                return self._response(request.id, result)
            
            elif request.method == "shutdown":
                await self.shutdown()
                return self._response(request.id, {"status": "shutdown"})
            
            else:
                return self._error_response(request.id, -32601, f"Method not found: {request.method}")
        
        except Exception as e:
            logger.exception(f"Error handling request: {e}")
            return self._error_response(
                request_data.get("id"),
                -32603,
                f"Internal error: {str(e)}"
            )
    
    async def _call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool with the given parameters.
        
        Args:
            params: Tool parameters {name, arguments}
            
        Returns:
            Tool result
        """
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        
        logger.info(f"Calling tool: {tool_name}")
        
        if not self.browser_client:
            raise RuntimeError("Browser client not initialized")
        
        # Navigate to URL
        if tool_name == "navigate_to":
            url = arguments.get("url", "")
            wait_for = arguments.get("wait_for")
            result = await self.browser_client.navigate_to(url, wait_for)
            return {"success": True, "result": result}
        
        # Extract content
        elif tool_name == "extract_content":
            selector = arguments.get("selector")
            include_metadata = arguments.get("include_metadata", True)
            content = await self.browser_client.extract_content(selector, include_metadata)
            return {"success": True, "result": content}
        
        # Set credentials
        elif tool_name == "set_credentials":
            username = arguments.get("username", "")
            password = arguments.get("password", "")
            await self.browser_client.set_credentials(username, password)
            return {"success": True, "result": "Credentials stored"}
        
        # Wait for login
        elif tool_name == "wait_for_login":
            timeout = arguments.get("timeout_seconds", 300)
            success_indicator = arguments.get("success_indicator")
            result = await self.browser_client.wait_for_login(timeout, success_indicator)
            return {"success": result, "result": "Login detected" if result else "Timeout"}
        
        # Fill form
        elif tool_name == "fill_form":
            fields = arguments.get("fields", {})
            submit_button = arguments.get("submit_button")
            await self.browser_client.fill_form(fields, submit_button)
            return {"success": True, "result": "Form submitted"}
        
        # Get page status
        elif tool_name == "get_page_status":
            status = await self.browser_client.get_page_status()
            return {"success": True, "result": status}
        
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    def _get_capabilities(self) -> Dict[str, Any]:
        """Get server capabilities."""
        return {
            "tools": {
                "listChanged": False
            },
            "resources": {},
            "logging": {}
        }
    
    def _response(self, request_id: Optional[int], result: Any) -> Dict[str, Any]:
        """Create a successful JSON-RPC response."""
        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        }
    
    def _error_response(self, request_id: Optional[int], code: int, message: str) -> Dict[str, Any]:
        """Create a JSON-RPC error response."""
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": code,
                "message": message
            },
            "id": request_id
        }
    
    async def run(self) -> None:
        """Run the MCP server, reading from stdin and writing to stdout."""
        logger.info("MCP server running on stdio transport")
        await self.initialize()
        
        try:
            loop = asyncio.get_event_loop()
            
            while self.running:
                try:
                    # Read JSON from stdin (non-blocking would be better, but this works for now)
                    line = await loop.run_in_executor(None, sys.stdin.readline)
                    
                    if not line:
                        # EOF detected
                        break
                    
                    # Parse JSON request
                    request_data = json.loads(line.strip())
                    
                    # Process request
                    response = await self.handle_request(request_data)
                    
                    # Write JSON response to stdout
                    json.dump(response, sys.stdout)
                    sys.stdout.write('\n')
                    sys.stdout.flush()
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        },
                        "id": None
                    }
                    json.dump(error_response, sys.stdout)
                    sys.stdout.write('\n')
                    sys.stdout.flush()
                
                except Exception as e:
                    logger.error(f"Error in server loop: {e}")
        
        except KeyboardInterrupt:
            logger.info("Received SIGINT, shutting down...")
        finally:
            await self.shutdown()


async def main():
    """Main entry point for the MCP server."""
    server = MCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
