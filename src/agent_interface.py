"""
Agent-Optimized Interface for WebScraperPortable

Provides a simplified, powerful interface specifically designed for autonomous agents.
Focus on clean JSON input/output, batch operations, and intelligent result handling.
"""

import os
import time
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv

    load_dotenv()
    _dotenv_available = True
except (ImportError, ModuleNotFoundError):
    _dotenv_available = False

try:
    from .search import SearchEngine
    from scraper import WebScraperAPI
    from .utils import app_logger
except (ImportError, ModuleNotFoundError):
    from .search import SearchEngine
    from scraper import WebScraperAPI
    from .utils import app_logger


class AgentSearchInterface:
    """
    Agent-optimized search and scrape interface.

    Designed for autonomous agents that need:
    - Clean JSON input/output
    - Batch operations
    - Domain-specific targeting
    - Fast metadata extraction
    - Result quality validation
    - Intelligent caching
    """

    def __init__(
        self,
        brave_api_key: Optional[str] = None,
        tavily_api_key: Optional[str] = None,
        cache_dir: Optional[str] = None,
        cache_ttl_minutes: int = 90,
    ):
        """
        Initialize agent interface.

        Args:
            brave_api_key: Brave Search API key
            tavily_api_key: Tavily Search API key
            cache_dir: Directory for result caching (None = no caching)
            cache_ttl_minutes: Cache time-to-live in minutes (default: 90 minutes)
        """
        self.search_engine = SearchEngine(brave_api_key, tavily_api_key)
        # Agent interface defaults to fast mode (no slow embedding analysis)
        self.scraper_api = WebScraperAPI(
            enable_search=False, max_workers=8, enable_semantic=False
        )
        self.search_engine.scraper_api = self.scraper_api

        # Caching setup
        self.cache_dir = cache_dir
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        self.cache_max_files = 1000  # Simple limit to prevent cache overflow
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
            self._cleanup_expired_cache()  # Clean up old cache on startup

        # Domain targeting presets
        self.domain_presets = {
            "github": ["github.com"],
            "docs": [
                "readthedocs.io",
                "docs.python.org",
                "developer.mozilla.org",
                ".edu",
                ".gov",
            ],
            "tutorials": ["tutorial", "guide", "howto", "learn", "course"],
            "stackoverflow": ["stackoverflow.com", "stackexchange.com"],
            "academic": [
                ".edu",
                ".ac.uk",
                "arxiv.org",
                "scholar.google",
                "researchgate",
            ],
            "official": [".org", ".gov", "python.org", "nodejs.org", "reactjs.org"],
            "quality": [
                "github.com",
                "stackoverflow.com",
                "medium.com",
                "docs.",
                ".edu",
                ".gov",
            ],
        }

    def is_available(self) -> bool:
        """Check if search functionality is available"""
        return self.search_engine.check_availability()

    def _get_cache_key(self, query: str, options: Dict[str, Any]) -> str:
        """Generate cache key for query and options"""
        cache_input = f"{query}:{json.dumps(options, sort_keys=True)}"
        return hashlib.md5(cache_input.encode()).hexdigest()

    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached result if valid"""
        if not self.cache_dir:
            return None

        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        if not os.path.exists(cache_file):
            return None

        try:
            with open(cache_file, "r") as f:
                cached_data = json.load(f)

            # Check if cache is still valid
            cached_time = datetime.fromisoformat(cached_data["timestamp"])
            if datetime.now() - cached_time > self.cache_ttl:
                os.remove(cache_file)  # Remove expired cache
                return None

            app_logger.info(
                f"Using cached result for query (age: {datetime.now() - cached_time})"
            )
            return cached_data["result"]

        except Exception as e:
            app_logger.warning(f"Cache read error: {e}")
            return None

    def _cache_result(self, cache_key: str, result: Dict[str, Any]) -> None:
        """Cache result with timestamp and automatic cleanup"""
        if not self.cache_dir:
            return

        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        try:
            cache_data = {"timestamp": datetime.now().isoformat(), "result": result}
            with open(cache_file, "w") as f:
                json.dump(cache_data, f)

            # Simple cache size management - clean up if too many files
            self._check_cache_size()

        except Exception as e:
            app_logger.warning(f"Cache write error: {e}")

    def _cleanup_expired_cache(self) -> None:
        """Clean up expired cache files"""
        if not self.cache_dir or not os.path.exists(self.cache_dir):
            return

        try:
            now = datetime.now()
            expired_count = 0

            for filename in os.listdir(self.cache_dir):
                if not filename.endswith(".json"):
                    continue

                cache_file = os.path.join(self.cache_dir, filename)
                try:
                    # Check file modification time as fallback
                    file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
                    if now - file_time > self.cache_ttl:
                        os.remove(cache_file)
                        expired_count += 1
                except Exception:
                    # If file is corrupted or can't be read, remove it
                    try:
                        os.remove(cache_file)
                        expired_count += 1
                    except Exception:
                        pass

            if expired_count > 0:
                app_logger.info(f"Cleaned up {expired_count} expired cache files")

        except Exception as e:
            app_logger.warning(f"Cache cleanup error: {e}")

    def _check_cache_size(self) -> None:
        """Simple cache size management"""
        if not self.cache_dir:
            return

        try:
            cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith(".json")]
            if len(cache_files) > self.cache_max_files:
                # Remove oldest files when cache gets too large
                cache_files_with_time = []
                for filename in cache_files:
                    cache_file = os.path.join(self.cache_dir, filename)
                    try:
                        mtime = os.path.getmtime(cache_file)
                        cache_files_with_time.append((mtime, cache_file))
                    except Exception:
                        pass

                # Sort by modification time and remove oldest 20%
                cache_files_with_time.sort()
                files_to_remove = int(len(cache_files_with_time) * 0.2)

                for _, cache_file in cache_files_with_time[:files_to_remove]:
                    try:
                        os.remove(cache_file)
                    except Exception:
                        pass

                app_logger.info(
                    f"Cleaned up {files_to_remove} old cache files to manage cache size"
                )

        except Exception as e:
            app_logger.warning(f"Cache size check error: {e}")

    def search(
        self,
        query: str,
        max_results: int = 10,
        domain_filter: Optional[str] = None,
        include_metadata: bool = True,
        quality_threshold: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Agent-optimized search with domain filtering and quality thresholds.

        Args:
            query: Search query
            max_results: Maximum results to return
            domain_filter: Domain preset ("github", "docs", "tutorials", etc.) or None
            include_metadata: Include additional metadata in results
            quality_threshold: Minimum quality score (0.0-1.0)

        Returns:
            {
                "status": "success",
                "query": "original query",
                "results_found": 15,
                "results_returned": 10,
                "execution_time": 1.23,
                "cache_hit": false,
                "results": [
                    {
                        "url": "https://example.com",
                        "title": "Page Title",
                        "description": "Page description",
                        "domain": "example.com",
                        "quality_score": 0.8,
                        "source_engine": "brave",
                        "metadata": { ... }  # if include_metadata=True
                    }
                ]
            }
        """
        start_time = time.time()

        # Prepare options for caching
        options = {
            "max_results": max_results,
            "domain_filter": domain_filter,
            "include_metadata": include_metadata,
            "quality_threshold": quality_threshold,
        }

        # Check cache first
        cache_key = self._get_cache_key(query, options)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            cached_result["cache_hit"] = True
            return cached_result

        try:
            # Perform search
            raw_results = self.search_engine._search_with_fallback(
                query, max_results * 2
            )  # Get extra for filtering

            # Apply domain filtering if specified
            if domain_filter and domain_filter in self.domain_presets:
                target_domains = self.domain_presets[domain_filter]
                filtered_results = []
                for result in raw_results:
                    url_lower = result["url"].lower()
                    domain_lower = result["domain"].lower()
                    if any(
                        domain in url_lower or domain in domain_lower
                        for domain in target_domains
                    ):
                        filtered_results.append(result)
                raw_results = filtered_results

            # Apply quality threshold
            quality_filtered = [
                r for r in raw_results if r.get("quality_score", 0) >= quality_threshold
            ]

            # Enhance results with metadata if requested
            final_results = []
            for result in quality_filtered[:max_results]:
                enhanced_result = {
                    "url": result["url"],
                    "title": result["title"],
                    "description": result["description"],
                    "domain": result["domain"],
                    "quality_score": result["quality_score"],
                    "source_engine": result["source"].replace("_search", ""),
                }

                if include_metadata:
                    enhanced_result["metadata"] = {
                        "url_length": len(result["url"]),
                        "title_length": len(result["title"]),
                        "description_length": len(result["description"]),
                        "has_path": "/" in result["url"].split("://", 1)[1],
                        "is_https": result["url"].startswith("https://"),
                        "estimated_authority": self._estimate_domain_authority(
                            result["domain"]
                        ),
                    }

                final_results.append(enhanced_result)

            # Prepare response
            response = {
                "status": "success",
                "query": query,
                "results_found": len(raw_results),
                "results_returned": len(final_results),
                "execution_time": round(time.time() - start_time, 2),
                "cache_hit": False,
                "applied_filters": {
                    "domain_filter": domain_filter,
                    "quality_threshold": quality_threshold,
                },
                "results": final_results,
            }

            # Cache the result
            self._cache_result(cache_key, response)

            return response

        except Exception as e:
            return {
                "status": "error",
                "query": query,
                "error": str(e),
                "execution_time": round(time.time() - start_time, 2),
                "cache_hit": False,
            }

    def batch_search(self, queries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Batch search processing for agents.

        Args:
            queries: List of query dictionaries:
            [
                {
                    "query": "python tutorials",
                    "max_results": 5,
                    "domain_filter": "tutorials",
                },
                {"query": "react hooks", "max_results": 3, "domain_filter": "github"}
            ]

        Returns:
            {
                "status": "success",
                "total_queries": 2,
                "successful": 2,
                "failed": 0,
                "total_execution_time": 2.45,
                "results": {
                    "python tutorials": { ... },
                    "react hooks": { ... }
                }
            }
        """
        start_time = time.time()
        results = {}
        successful = 0
        failed = 0

        for query_config in queries:
            query = query_config["query"]
            max_results = query_config.get("max_results", 10)
            domain_filter = query_config.get("domain_filter", None)
            include_metadata = query_config.get("include_metadata", True)
            quality_threshold = query_config.get("quality_threshold", 0.0)

            result = self.search(
                query=query,
                max_results=max_results,
                domain_filter=domain_filter,
                include_metadata=include_metadata,
                quality_threshold=quality_threshold,
            )

            results[query] = result
            if result["status"] == "success":
                successful += 1
            else:
                failed += 1

        return {
            "status": "success",
            "total_queries": len(queries),
            "successful": successful,
            "failed": failed,
            "total_execution_time": round(time.time() - start_time, 2),
            "results": results,
        }

    def quick_metadata(self, urls: List[str]) -> Dict[str, Any]:
        """
        Extract quick metadata from URLs without full content scraping.
        Useful for agents to validate URLs before full scraping.

        Args:
            urls: List of URLs to check

        Returns:
            {
                "status": "success",
                "total_urls": 5,
                "successful": 4,
                "failed": 1,
                "results": {
                    "https://example.com": {
                        "status": "success",
                        "title": "Page Title",
                        "content_type": "text/html",
                        "status_code": 200,
                        "content_length": 45678,
                        "estimated_read_time": "3 minutes",
                        "has_code_blocks": true,
                        "language_detected": "en"
                    }
                }
            }
        """
        start_time = time.time()
        results = {}
        successful = 0
        failed = 0

        for url in urls:
            try:
                # Use content parser for lightweight metadata extraction
                content_text, title, raw_html, error_message = (
                    self.scraper_api.content_parser.get_content_and_title(url)
                )

                if error_message:
                    results[url] = {"status": "error", "error": error_message}
                    failed += 1
                else:
                    # Extract useful metadata without full processing
                    content_length = len(content_text) if content_text else 0
                    estimated_read_time = (
                        f"{max(1, content_length // 1000)} minutes"
                        if content_length > 500
                        else "< 1 minute"
                    )
                    has_code_blocks = bool(
                        raw_html
                        and (
                            "```" in content_text
                            or "<code>" in raw_html
                            or "<pre>" in raw_html
                        )
                    )

                    results[url] = {
                        "status": "success",
                        "title": title,
                        "content_length": content_length,
                        "estimated_read_time": estimated_read_time,
                        "has_code_blocks": has_code_blocks,
                        "is_likely_tutorial": "tutorial" in title.lower()
                        or "guide" in title.lower()
                        or "how to" in title.lower(),
                        "is_documentation": "docs" in url
                        or "documentation" in title.lower(),
                        "content_preview": (
                            content_text[:200] + "..."
                            if content_text and len(content_text) > 200
                            else content_text
                        ),
                    }
                    successful += 1

            except Exception as e:
                results[url] = {"status": "error", "error": str(e)}
                failed += 1

        return {
            "status": "success",
            "total_urls": len(urls),
            "successful": successful,
            "failed": failed,
            "execution_time": round(time.time() - start_time, 2),
            "results": results,
        }

    def search_and_validate(
        self,
        query: str,
        max_results: int = 10,
        domain_filter: Optional[str] = None,
        validation_sample: int = 3,
    ) -> Dict[str, Any]:
        """
        Search and validate a sample of results for quality before returning full list.
        Perfect for agents that need reliable results.

        Args:
            query: Search query
            max_results: Maximum results to return
            domain_filter: Domain preset filter
            validation_sample: Number of top results to validate

        Returns:
            Search results with validation scores and recommendations
        """
        # First, get search results
        search_result = self.search(query, max_results, domain_filter)

        if search_result["status"] != "success":
            return search_result

        if not search_result["results"]:
            return search_result

        # Validate top results
        top_urls = [r["url"] for r in search_result["results"][:validation_sample]]
        validation_result = self.quick_metadata(top_urls)

        # Add validation scores to search results
        for i, result in enumerate(search_result["results"]):
            if i < validation_sample:
                url = result["url"]
                if url in validation_result["results"]:
                    validation_data = validation_result["results"][url]
                    if validation_data["status"] == "success":
                        result["validation"] = {
                            "validated": True,
                            "accessible": True,
                            "content_length": validation_data["content_length"],
                            "estimated_read_time": validation_data[
                                "estimated_read_time"
                            ],
                            "has_code_blocks": validation_data["has_code_blocks"],
                            "is_likely_tutorial": validation_data["is_likely_tutorial"],
                            "is_documentation": validation_data["is_documentation"],
                            "recommendation": self._get_recommendation(validation_data),
                        }
                    else:
                        result["validation"] = {
                            "validated": True,
                            "accessible": False,
                            "error": validation_data["error"],
                            "recommendation": "skip",
                        }
                else:
                    result["validation"] = {"validated": False}
            else:
                result["validation"] = {"validated": False}

        # Add overall quality assessment
        validated_results = [
            r
            for r in search_result["results"]
            if r.get("validation", {}).get("validated", False)
        ]
        accessible_count = len(
            [r for r in validated_results if r["validation"].get("accessible", False)]
        )

        search_result["validation_summary"] = {
            "sample_size": validation_sample,
            "validated_count": len(validated_results),
            "accessible_count": accessible_count,
            "accessibility_rate": round(
                accessible_count / max(1, len(validated_results)), 2
            ),
            "recommended_action": (
                "proceed"
                if accessible_count >= validation_sample * 0.7
                else "review_query"
            ),
        }

        return search_result

    def _estimate_domain_authority(self, domain: str) -> float:
        """Simple domain authority estimation"""
        authority_scores = {
            "github.com": 0.9,
            "stackoverflow.com": 0.9,
            "docs.python.org": 0.9,
            "developer.mozilla.org": 0.9,
            "medium.com": 0.7,
            "readthedocs.io": 0.8,
        }

        domain_lower = domain.lower()

        # Direct match
        if domain_lower in authority_scores:
            return authority_scores[domain_lower]

        # Pattern matching
        if domain_lower.endswith(".edu") or domain_lower.endswith(".gov"):
            return 0.85
        elif domain_lower.endswith(".org"):
            return 0.7
        elif "docs." in domain_lower or "documentation" in domain_lower:
            return 0.75
        else:
            return 0.5

    def _get_recommendation(self, validation_data: Dict[str, Any]) -> str:
        """Get recommendation based on validation data"""
        content_length = validation_data.get("content_length", 0)
        has_code = validation_data.get("has_code_blocks", False)
        is_tutorial = validation_data.get("is_likely_tutorial", False)
        is_docs = validation_data.get("is_documentation", False)

        if content_length > 5000 and (has_code or is_tutorial or is_docs):
            return "high_priority"
        elif content_length > 1000 and (is_tutorial or is_docs):
            return "good"
        elif content_length < 500:
            return "brief_content"
        else:
            return "standard"

    def get_available_presets(self) -> Dict[str, List[str]]:
        """Get available domain filter presets"""
        return self.domain_presets.copy()


# Convenience function for agents
def create_agent_interface(cache_dir: str = "./search_cache") -> AgentSearchInterface:
    """Create a ready-to-use agent interface with caching enabled"""
    return AgentSearchInterface(cache_dir=cache_dir)


# Export main class
__all__ = ["AgentSearchInterface", "create_agent_interface"]
