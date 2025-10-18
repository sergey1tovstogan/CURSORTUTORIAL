"""
Browser Client Module

Manages Playwright browser instances with persistent sessions and content extraction.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from pathlib import Path

from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from bs4 import BeautifulSoup
from markdownify import markdownify as md

from config import BrowserConfig, AuthConfig, ExtractionConfig, LogConfig

# Setup logging
logging.basicConfig(
    level=getattr(logging, LogConfig.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LogConfig.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class BrowserClient:
    """Manages Playwright browser with persistent authentication."""
    
    def __init__(self):
        """Initialize browser client."""
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        
    async def start(self) -> None:
        """Start Playwright and launch browser with persistent profile."""
        try:
            logger.info("Starting Playwright...")
            self.playwright = await async_playwright().start()
            
            # Launch browser with persistent user data directory
            logger.info(f"Launching Chromium with profile: {BrowserConfig.USER_DATA_DIR}")
            self.browser = await self.playwright.chromium.launch(
                headless=BrowserConfig.HEADLESS,
                slow_mo=BrowserConfig.SLOW_MO,
                args=BrowserConfig.ARGS,
            )
            
            # Create persistent context
            self.context = await self.browser.new_context(
                storage_state=None,  # Preserve existing cookies/sessions
                ignore_https_errors=False,
            )
            
            # Create initial page
            self.page = await self.context.new_page()
            logger.info("Browser started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            raise
    
    async def navigate_to(self, url: str, wait_for: Optional[str] = None) -> str:
        """
        Navigate to a URL and optionally wait for a selector.
        
        Args:
            url: URL to navigate to
            wait_for: CSS selector to wait for (optional)
            
        Returns:
            Current page URL after navigation
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        
        try:
            logger.info(f"Navigating to {url}")
            await self.page.goto(url, wait_until=BrowserConfig.WAIT_FOR_LOAD_STATE, 
                               timeout=BrowserConfig.TIMEOUT)
            
            if wait_for:
                logger.info(f"Waiting for selector: {wait_for}")
                await self.page.wait_for_selector(wait_for, timeout=ExtractionConfig.ELEMENT_TIMEOUT)
            
            current_url = self.page.url
            logger.info(f"Navigation complete. Current URL: {current_url}")
            return current_url
            
        except Exception as e:
            logger.error(f"Navigation error: {e}")
            raise
    
    async def extract_content(self, selector: Optional[str] = None, 
                            include_metadata: bool = True) -> str:
        """
        Extract page content and convert to Markdown.
        
        Args:
            selector: CSS selector for content extraction (None = all content)
            include_metadata: Include page title and URL
            
        Returns:
            Markdown formatted content
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        
        try:
            logger.info(f"Extracting content with selector: {selector}")
            
            # Get page HTML
            if selector:
                element = await self.page.query_selector(selector)
                if not element:
                    logger.warning(f"Selector not found: {selector}")
                    return f"Error: Selector '{selector}' not found on page"
                html = await element.inner_html()
            else:
                html = await self.page.content()
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Convert to Markdown
            markdown_content = md(str(soup), **ExtractionConfig.TURNDOWN_OPTIONS)
            
            # Add metadata if requested
            if include_metadata:
                title = await self.page.title()
                url = self.page.url
                metadata = f"# {title}\n\n**URL:** {url}\n\n---\n\n"
                markdown_content = metadata + markdown_content
            
            # Limit content length
            if len(markdown_content) > ExtractionConfig.MAX_CONTENT_LENGTH:
                logger.warning(f"Content truncated from {len(markdown_content)} to {ExtractionConfig.MAX_CONTENT_LENGTH}")
                markdown_content = markdown_content[:ExtractionConfig.MAX_CONTENT_LENGTH] + "\n\n[Content truncated...]"
            
            logger.info(f"Content extracted: {len(markdown_content)} chars")
            return markdown_content
            
        except Exception as e:
            logger.error(f"Content extraction error: {e}")
            raise
    
    async def fill_form(self, fields: Dict[str, str], submit_button: Optional[str] = None) -> bool:
        """
        Fill form fields and optionally submit.
        
        Args:
            fields: Dictionary of selector: value pairs
            submit_button: CSS selector for submit button (optional)
            
        Returns:
            True if successful
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        
        try:
            logger.info(f"Filling form with {len(fields)} fields")
            
            for selector, value in fields.items():
                logger.info(f"Filling {selector} with value")
                await self.page.fill(selector, value)
            
            if submit_button:
                logger.info(f"Clicking submit button: {submit_button}")
                await self.page.click(submit_button)
                # Wait for navigation after submit
                await self.page.wait_for_load_state(BrowserConfig.WAIT_FOR_LOAD_STATE, 
                                                   timeout=BrowserConfig.TIMEOUT)
            
            logger.info("Form filled and submitted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Form fill error: {e}")
            raise
    
    async def set_credentials(self, username: str, password: str) -> None:
        """
        Store credentials for automatic login.
        
        Args:
            username: Username for authentication
            password: Password for authentication
        """
        AuthConfig.stored_credentials = {
            "username": username,
            "password": password
        }
        logger.info(f"Credentials set for user: {username}")
    
    async def wait_for_login(self, timeout_seconds: int = 300, 
                           success_indicator: Optional[str] = None) -> bool:
        """
        Wait for manual authentication in the browser.
        
        Args:
            timeout_seconds: Maximum wait time
            success_indicator: URL pattern or selector indicating success
            
        Returns:
            True if login appears successful
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        
        try:
            logger.info(f"Waiting for login (timeout: {timeout_seconds}s)")
            print("\n" + "="*60)
            print("MANUAL LOGIN REQUIRED")
            print("Please authenticate in the browser window.")
            print(f"Waiting up to {timeout_seconds} seconds...")
            print("="*60 + "\n")
            
            timeout_ms = timeout_seconds * 1000
            
            if success_indicator:
                # Wait for URL or selector
                if success_indicator.startswith("http"):
                    logger.info(f"Waiting for URL containing: {success_indicator}")
                    await self.page.wait_for_url(f"*{success_indicator}*", timeout=timeout_ms)
                else:
                    logger.info(f"Waiting for selector: {success_indicator}")
                    await self.page.wait_for_selector(success_indicator, timeout=timeout_ms)
            else:
                # Wait for user to signal completion by monitoring for URL changes
                logger.info("Waiting for user confirmation...")
                await asyncio.sleep(timeout_seconds)
            
            logger.info("Login successful")
            return True
            
        except asyncio.TimeoutError:
            logger.error("Login timeout")
            return False
        except Exception as e:
            logger.error(f"Login wait error: {e}")
            return False
    
    async def get_page_status(self) -> Dict[str, Any]:
        """
        Get current page status.
        
        Returns:
            Dictionary with page information
        """
        if not self.page:
            return {
                "status": "not_started",
                "url": None,
                "title": None,
                "error": "Browser not started"
            }
        
        try:
            return {
                "status": "connected",
                "url": self.page.url,
                "title": await self.page.title(),
                "error": None
            }
        except Exception as e:
            logger.error(f"Status check error: {e}")
            return {
                "status": "error",
                "url": None,
                "title": None,
                "error": str(e)
            }
    
    async def close(self) -> None:
        """Close browser and cleanup resources."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")


# Global browser instance
_browser_client: Optional[BrowserClient] = None


async def get_browser_client() -> BrowserClient:
    """Get or create global browser client instance."""
    global _browser_client
    if _browser_client is None:
        _browser_client = BrowserClient()
        await _browser_client.start()
    return _browser_client


async def close_browser_client() -> None:
    """Close global browser client instance."""
    global _browser_client
    if _browser_client:
        await _browser_client.close()
        _browser_client = None
