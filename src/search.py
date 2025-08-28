"""
Search Module for WebScraperPortable

Provides web search capabilities using Brave Search API, integrating with
the existing content extraction and semantic analysis systems.
"""

import os
import requests
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv

    load_dotenv()
    _dotenv_available = True
except (ImportError, ModuleNotFoundError):
    _dotenv_available = False

try:
    from .utils import app_logger, is_valid_url
    from .search_stats import log_search
except (ImportError, ModuleNotFoundError):
    from .utils import app_logger, is_valid_url
    from .search_stats import log_search

# Configuration for search APIs
BRAVE_SEARCH_API_URL = "https://api.search.brave.com/res/v1/web/search"
BRAVE_SEARCH_API_KEY_ENV = "BRAVE_SEARCH_API_KEY"

TAVILY_SEARCH_API_URL = "https://api.tavily.com/search"
TAVILY_SEARCH_API_KEY_ENV = "TAVILY_API_KEY"


class SearchEngine:
    """
    A search engine that finds URLs matching a query and integrates with
    WebScraperPortable.
    Uses Brave Search API for results and can automatically scrape discovered URLs.
    """

    def __init__(
        self,
        brave_api_key: Optional[str] = None,
        tavily_api_key: Optional[str] = None,
        scraper_api=None,
    ):
        """
        Initialize the search engine with optional API keys and scraper.

        Args:
            brave_api_key: Brave Search API key (will check environment if not provided)
            tavily_api_key: Tavily Search API key (will check environment if not
                provided)
            scraper_api: WebScraperAPI instance for content extraction
        """
        self.brave_api_key = brave_api_key or os.getenv(BRAVE_SEARCH_API_KEY_ENV)
        self.tavily_api_key = tavily_api_key or os.getenv(TAVILY_SEARCH_API_KEY_ENV)
        self.scraper_api = scraper_api

        # Simple connection pooling with requests.Session
        self.session = requests.Session()
        self.session.timeout = 30  # Default timeout

        # Simple request deduplication
        self._active_requests = {}  # Track ongoing requests to avoid duplicates

        # Determine available engines
        self.brave_available = bool(self.brave_api_key)
        self.tavily_available = bool(self.tavily_api_key)
        self.is_available = self.brave_available or self.tavily_available

        # Log availability
        if self.brave_available:
            app_logger.info("Brave Search API available")
        else:
            app_logger.warning(
                f"Brave Search API key not found. Set {BRAVE_SEARCH_API_KEY_ENV} "
                "environment variable."
            )

        if self.tavily_available:
            app_logger.info("Tavily Search API available")
        else:
            app_logger.warning(
                f"Tavily Search API key not found. Set {TAVILY_SEARCH_API_KEY_ENV} "
                "environment variable."
            )

        if not self.is_available:
            app_logger.warning(
                "No search engines available. Please set either BRAVE_SEARCH_API_KEY "
                "or TAVILY_API_KEY environment variable."
            )

    def check_availability(self) -> bool:
        """Check if search functionality is available"""
        return self.is_available

    def _make_brave_search_request(
        self, query: str, max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Make a search request to the Brave Search API.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            Dictionary with search results from Brave API
        """
        if not self.brave_available:
            raise RuntimeError("Brave Search API not available.")

        params = {
            "q": query,
            "count": min(max_results, 20),  # Brave API limit
            "safesearch": "moderate",
            "search_lang": "en",
            "country": "US",
            "text_decorations": False,
            "spellcheck": True,
        }

        headers = {
            "X-Subscription-Token": self.brave_api_key,
            "Accept": "application/json",
        }

        try:
            app_logger.info(
                f"Searching with Brave API: '{query}' (max {max_results} results)"
            )
            response = self.session.get(
                BRAVE_SEARCH_API_URL, params=params, headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            app_logger.error(f"Brave Search API request failed: {e}")
            raise ConnectionError(f"Failed to connect to Brave Search API: {str(e)}")

    def _make_tavily_search_request(
        self, query: str, max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Make a search request to the Tavily Search API.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            Dictionary with search results from Tavily API
        """
        if not self.tavily_available:
            raise RuntimeError("Tavily Search API not available.")

        payload = {
            "api_key": self.tavily_api_key,
            "query": query,
            "search_depth": "basic",
            "include_domains": [],
            "exclude_domains": [],
            "max_results": min(max_results, 20),  # Tavily API limit
            "include_answer": False,
            "include_raw_content": False,
            "include_images": False,
        }

        headers = {"Content-Type": "application/json"}

        try:
            app_logger.info(
                f"Searching with Tavily API: '{query}' (max {max_results} results)"
            )
            response = self.session.post(
                TAVILY_SEARCH_API_URL, json=payload, headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            app_logger.error(f"Tavily Search API request failed: {e}")
            raise ConnectionError(f"Failed to connect to Tavily Search API: {str(e)}")

    def _filter_and_rank_results(
        self, raw_results: Dict[str, Any], source_engine: str, max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Filter and rank search results by quality and relevance.

        Args:
            raw_results: Raw results from search API
            source_engine: Engine that provided the results ("brave" or "tavily")
            max_results: Maximum number of results to return

        Returns:
            List of filtered and ranked results
        """
        # Extract results based on source engine format
        if source_engine == "brave":
            web_results = raw_results.get("web", {}).get("results", [])
        elif source_engine == "tavily":
            web_results = raw_results.get("results", [])
        else:
            web_results = []

        if not web_results:
            app_logger.warning(
                f"No web results found in {source_engine} search response"
            )
            return []

        filtered_results = []
        for result in web_results:
            # Handle different result formats
            if source_engine == "brave":
                url = result.get("url", "")
                title = result.get("title", "")
                description = result.get("description", "")
            elif source_engine == "tavily":
                url = result.get("url", "")
                title = result.get("title", "")
                description = result.get(
                    "content", ""
                )  # Tavily uses "content" instead of "description"
            else:
                continue

            # Skip invalid results
            if not url or not title or not is_valid_url(url):
                continue

            # Parse domain for filtering
            try:
                parsed_url = urlparse(url)
                domain = parsed_url.netloc.lower()

                # Skip low-quality domains
                skip_domains = [
                    "pinterest.com",
                    "youtube.com",
                    "facebook.com",
                    "twitter.com",
                    "instagram.com",
                    "reddit.com",
                    "tiktok.com",
                    "snapchat.com",
                ]
                if any(skip_domain in domain for skip_domain in skip_domains):
                    continue

                # Prefer quality domains
                quality_bonus = 0
                quality_domains = [
                    "github.com",
                    "stackoverflow.com",
                    "medium.com",
                    "docs.python.org",
                    "developer.mozilla.org",
                    ".edu",
                    ".gov",
                    "readthedocs.io",
                    "tutorial",
                    "guide",
                    "documentation",
                ]
                if any(
                    quality_domain in domain or quality_domain in url.lower()
                    for quality_domain in quality_domains
                ):
                    quality_bonus = 1

                filtered_results.append(
                    {
                        "url": url,
                        "title": title,
                        "description": description,
                        "domain": domain,
                        "quality_score": quality_bonus,
                        "source": f"{source_engine}_search",
                    }
                )

            except Exception as e:
                app_logger.warning(f"Error processing search result {url}: {e}")
                continue

        # Sort by quality score (higher first) and limit results
        filtered_results.sort(key=lambda x: x["quality_score"], reverse=True)
        return filtered_results[:max_results]

    def _search_with_fallback(
        self, query: str, max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search using available engines with fallback and request deduplication.

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            Combined and deduplicated search results
        """
        # Simple deduplication - check if same request is already in progress
        request_key = f"{query}:{max_results}"
        if request_key in self._active_requests:
            app_logger.info(
                f"Duplicate request detected for '{query}', using existing result"
            )
            return self._active_requests[request_key]

        # Mark request as active
        self._active_requests[request_key] = []

        try:
            all_results = []

            # Try Brave first (typically more comprehensive)
            if self.brave_available:
                try:
                    brave_results = self._make_brave_search_request(query, max_results)
                    brave_filtered = self._filter_and_rank_results(
                        brave_results, "brave", max_results
                    )
                    all_results.extend(brave_filtered)
                    app_logger.info(f"Brave API returned {len(brave_filtered)} results")
                except Exception as e:
                    app_logger.warning(f"Brave search failed, trying Tavily: {e}")

            # Try Tavily if Brave failed or to supplement results
            if self.tavily_available and len(all_results) < max_results:
                try:
                    remaining_results = max_results - len(all_results)
                    tavily_results = self._make_tavily_search_request(
                        query, remaining_results
                    )
                    tavily_filtered = self._filter_and_rank_results(
                        tavily_results, "tavily", remaining_results
                    )

                    # Deduplicate by URL
                    existing_urls = {result["url"] for result in all_results}
                    new_results = [
                        r for r in tavily_filtered if r["url"] not in existing_urls
                    ]
                    all_results.extend(new_results)
                    app_logger.info(f"Tavily API added {len(new_results)} new results")
                except Exception as e:
                    app_logger.warning(f"Tavily search also failed: {e}")

            if not all_results:
                app_logger.error("All search engines failed to return results")

            final_results = all_results[:max_results]
            self._active_requests[request_key] = final_results
            return final_results

        finally:
            # Clean up request tracking after a short delay to allow duplicate
            # requests to benefit
            # This is simple - just remove from active requests when done
            if request_key in self._active_requests:
                del self._active_requests[request_key]

    def search_only(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for URLs without content extraction.

        Args:
            query: The search query (e.g., "python web scraping examples")
            max_results: Maximum number of results to return

        Returns:
            List of search results with metadata only
        """
        if not self.is_available:
            raise RuntimeError(
                "Search functionality not available. Please set BRAVE_SEARCH_API_KEY "
                "or TAVILY_API_KEY environment variable."
            )

        try:
            # Log the search operation
            total_searches = log_search(query)

            # Use unified search with fallback
            filtered_results = self._search_with_fallback(query, max_results)

            app_logger.info(
                f"Found {len(filtered_results)} relevant results for query: "
                f"'{query}' (Search #{total_searches})"
            )
            return filtered_results

        except Exception as e:
            app_logger.error(f"Search operation failed: {e}")
            raise RuntimeError(f"Search failed: {str(e)}")

    def search_and_scrape(
        self,
        query: str,
        max_results: int = 10,
        scraper_options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Search for URLs matching the query and automatically scrape their content.

        Args:
            query: The search query (e.g., "python web scraping examples")
            max_results: Maximum number of results to return
            scraper_options: Options to pass to the scraper (depth, topic,
                output_dir, etc.)

        Returns:
            Dictionary with search results and scraper result information
        """
        if not self.is_available:
            raise RuntimeError(
                "Search functionality not available. Please set BRAVE_SEARCH_API_KEY "
                "or TAVILY_API_KEY environment variable."
            )

        if not self.scraper_api:
            raise RuntimeError(
                "No scraper API provided. Cannot extract content from search results."
            )

        # Default scraper options
        default_options = {"depth": 1, "show_progress": True}
        if scraper_options:
            default_options.update(scraper_options)

        try:
            # Log the search operation
            total_searches = log_search(query)

            # Step 1: Search for URLs using unified search
            app_logger.info(f"🔍 Searching for: '{query}' (Search #{total_searches})")
            search_results = self._search_with_fallback(query, max_results)

            if not search_results:
                app_logger.warning("No search results found.")
                return {
                    "search_query": query,
                    "search_results": [],
                    "scraped_urls": [],
                    "scraper_result": {"status": "no_results"},
                }

            # Step 2: Extract URLs for scraping
            urls_to_scrape = [result["url"] for result in search_results]
            app_logger.info(
                f"🚀 Scraping {len(urls_to_scrape)} URLs from search results"
            )

            # Step 3: Scrape the discovered URLs
            scraper_result = self.scraper_api.scrape(
                sources=urls_to_scrape, **default_options
            )

            # Step 4: Combine search metadata with scraper results
            return {
                "search_query": query,
                "search_results": search_results,
                "scraped_urls": urls_to_scrape,
                "scraper_result": scraper_result,
            }

        except Exception as e:
            app_logger.error(f"Search and scrape operation failed: {e}")
            raise RuntimeError(f"Search and scrape failed: {str(e)}")


# Export main class
__all__ = ["SearchEngine"]
