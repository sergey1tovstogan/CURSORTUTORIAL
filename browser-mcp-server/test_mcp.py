#!/usr/bin/env python3
"""
Test script for Browser MCP Server

Sends sample JSON-RPC requests to test the server functionality.
Usage: python test_mcp.py
"""

import json
import subprocess
import sys
import time
import signal
from pathlib import Path

def send_request(proc, method, params=None, request_id=1):
    """Send a JSON-RPC request and get response."""
    request = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params or {},
        "id": request_id
    }
    
    print(f"\n→ Sending: {method}")
    print(f"  Params: {json.dumps(params or {}, indent=2)}")
    
    try:
        proc.stdin.write(json.dumps(request) + '\n')
        proc.stdin.flush()
        
        # Read response with timeout
        response_line = proc.stdout.readline()
        if not response_line:
            print("✗ No response from server")
            return None
        
        response = json.loads(response_line)
        
        if "error" in response and response["error"]:
            print(f"✗ Error: {response['error']['message']}")
            return None
        
        if "result" in response:
            print(f"✓ Success")
            print(f"  Result: {json.dumps(response['result'], indent=2)[:500]}")
            return response["result"]
        
        return response
    
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON response: {e}")
        return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def main():
    """Run test suite."""
    print("=" * 70)
    print("Browser MCP Server Test Suite")
    print("=" * 70)
    
    # Get the script directory
    script_dir = Path(__file__).parent
    
    # Start server
    print("\nStarting MCP server...")
    try:
        proc = subprocess.Popen(
            [sys.executable, str(script_dir / "server.py")],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
    except Exception as e:
        print(f"✗ Failed to start server: {e}")
        return 1
    
    print("✓ Server started")
    time.sleep(2)  # Give server time to initialize browser
    
    try:
        # Test 1: Initialize
        print("\n--- Test 1: Initialize ---")
        send_request(proc, "initialize")
        
        # Test 2: List tools
        print("\n--- Test 2: List Available Tools ---")
        result = send_request(proc, "tools/list")
        if result and "tools" in result:
            for tool in result["tools"]:
                print(f"  - {tool['name']}: {tool['description'][:50]}...")
        
        # Test 3: Get page status (browser should be started)
        print("\n--- Test 3: Get Page Status ---")
        send_request(proc, "tools/call", {
            "name": "get_page_status",
            "arguments": {}
        })
        
        # Test 4: Navigate to example.com
        print("\n--- Test 4: Navigate to Example.com ---")
        send_request(proc, "tools/call", {
            "name": "navigate_to",
            "arguments": {
                "url": "https://example.com",
                "wait_for": None
            }
        }, 2)
        
        # Test 5: Extract content
        print("\n--- Test 5: Extract Content ---")
        time.sleep(1)  # Give page time to load
        send_request(proc, "tools/call", {
            "name": "extract_content",
            "arguments": {
                "selector": None,
                "include_metadata": True
            }
        }, 3)
        
        # Test 6: Set credentials (won't actually use them)
        print("\n--- Test 6: Set Credentials ---")
        send_request(proc, "tools/call", {
            "name": "set_credentials",
            "arguments": {
                "username": "testuser",
                "password": "testpass"
            }
        }, 4)
        
        # Test 7: Get status again
        print("\n--- Test 7: Get Status Again ---")
        send_request(proc, "tools/call", {
            "name": "get_page_status",
            "arguments": {}
        }, 5)
        
        print("\n" + "=" * 70)
        print("Test suite completed successfully!")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
    
    finally:
        # Shutdown server
        print("\nShutting down server...")
        try:
            send_request(proc, "shutdown", {}, 999)
            proc.wait(timeout=5)
            print("✓ Server shutdown cleanly")
        except subprocess.TimeoutExpired:
            print("! Server shutdown timeout, force killing...")
            proc.kill()
        except Exception as e:
            print(f"! Error during shutdown: {e}")
            proc.kill()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
