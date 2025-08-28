"""
Main WebScraper API Module for WebScraperPortable

Provides the core web scraping functionality with integrated components.
"""

import os
import time
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Dict, Optional, Any, Union

try:
    from .dependencies import FEATURES_AVAILABLE, print_feature_status
    from .utils import (
        app_logger,
        create_progress_display,
        normalize_url,
        DEFAULT_OUTPUT_FOLDER,
    )
    from .storage import StorageManager
    from .parser import ContentParser
    from .semantic import SemanticAnalyzer
except (ImportError, ModuleNotFoundError):
    from .dependencies import FEATURES_AVAILABLE, print_feature_status
    from .utils import (
        app_logger,
        create_progress_display,
        normalize_url,
        DEFAULT_OUTPUT_FOLDER,
    )
    from .storage import StorageManager
    from .parser import ContentParser
    from .semantic import SemanticAnalyzer


class WebScraperAPI:
    """
    Main API class for WebScraperPortable

    Provides a high-level interface for web scraping with optional semantic analysis.
    """

    def __init__(
        self,
        max_workers: int = 5,
        enable_semantic: bool = True,
        user_agent: str = None,
        ollama_host: str = None,
        enable_search: bool = True,
        brave_api_key: str = None,
        tavily_api_key: str = None,
    ):
        """
        Initialize WebScraper API

        Args:
            max_workers: Number of worker threads for concurrent processing
            enable_semantic: Whether to enable semantic analysis features
            user_agent: Custom user agent string
            ollama_host: Ollama server host (for semantic features)
            enable_search: Whether to enable search functionality
            brave_api_key: Brave Search API key for search functionality
            tavily_api_key: Tavily Search API key for search functionality
        """
        self.max_workers = max_workers
        self.enable_semantic = (
            enable_semantic and FEATURES_AVAILABLE["semantic_analysis"]
        )
        self.enable_search = enable_search

        # Initialize components
        self.content_parser = ContentParser(user_agent=user_agent)
        self.semantic_analyzer = (
            SemanticAnalyzer(ollama_host=ollama_host) if self.enable_semantic else None
        )

        # Initialize search engine if enabled
        self.search_engine = None
        if self.enable_search:
            try:
                from .search import SearchEngine

                self.search_engine = SearchEngine(
                    brave_api_key=brave_api_key,
                    tavily_api_key=tavily_api_key,
                    scraper_api=self,
                )
                if not self.search_engine.check_availability():
                    app_logger.warning(
                        "Search engine initialized but no API keys available"
                    )
                    self.search_engine = None
            except Exception as e:
                app_logger.warning(f"Failed to initialize search engine: {e}")
                self.search_engine = None

        # Runtime state
        self.crawl_queue = queue.Queue()
        self.visited_sources = set()
        self.user_topic_embedding = None

        app_logger.info(f"WebScraperAPI initialized with {max_workers} workers")
        if not self.enable_semantic:
            app_logger.info(
                "Semantic analysis disabled - using basic web scraping mode"
            )
        if self.search_engine:
            app_logger.info("Search functionality enabled")
        else:
            app_logger.info("Search functionality disabled")

    def scrape(
        self,
        sources: Union[str, List[str]],
        output_dir: Optional[str] = None,
        depth: int = 1,
        topic: Optional[str] = None,
        topic_threshold: float = 0.5,
        link_threshold: float = 0.6,
        show_progress: bool = True,
    ) -> Dict[str, Any]:
        """
        Main scraping function

        Args:
            sources: URL(s) or file path(s) to scrape
            output_dir: Output directory for results
            depth: Crawling depth (-1 for unlimited)
            topic: Optional topic for semantic filtering
            topic_threshold: Topic relevance threshold (0.0-1.0)
            link_threshold: Link relevance threshold (0.0-1.0)
            show_progress: Whether to show progress indicators

        Returns:
            Dictionary with result information and output paths
        """
        # Normalize inputs
        if isinstance(sources, str):
            sources = [sources]

        # Set up output paths
        output_dir = output_dir or DEFAULT_OUTPUT_FOLDER

        # Initialize storage manager (without spreadsheet)
        storage_manager = StorageManager(output_folder=output_dir)

        # Initialize crawler
        crawler = WebCrawler(
            storage_manager=storage_manager,
            content_parser=self.content_parser,
            semantic_analyzer=self.semantic_analyzer,
            max_workers=self.max_workers,
            default_depth=depth,
            user_topic=topic,
            topic_relevance_threshold=topic_threshold,
            link_relevance_threshold=link_threshold,
        )

        try:
            # Start crawling
            start_time = time.time()
            if show_progress:
                app_logger.info(
                    f"🚀 Starting scraper with {len(sources)} initial sources"
                )
                app_logger.info(f"📁 Output directory: {output_dir}")
                app_logger.info(f"📏 Depth: {depth}")
                if topic:
                    app_logger.info(f"🎯 Topic: {topic}")

            # Perform the crawl
            crawler.start_crawling(
                sources, crawl_depth=depth, show_progress=show_progress
            )

            # Results are already persisted as files during crawling

            end_time = time.time()
            duration = end_time - start_time

            # Prepare result information
            result = {
                "status": "success",
                "output_directory": os.path.abspath(output_dir),
                "web_content_dir": os.path.join(os.path.abspath(output_dir), "web"),
                "files_content_dir": os.path.join(os.path.abspath(output_dir), "files"),
                "logs_dir": os.path.join(os.path.abspath(output_dir), "logs"),
                "targets_processed": len(sources),
                "depth": depth,
                "duration_seconds": duration,
                "cache_stats": storage_manager.get_cache_stats(),
            }

            if show_progress:
                app_logger.info(f"✅ Scraping completed in {duration:.2f}s")
                app_logger.info(
                    f"📊 Processed {result['cache_stats']['processed_sources']} sources"
                )

            return result

        except Exception as e:
            app_logger.error(f"Error during scraping: {e}")
            return {
                "status": "error",
                "error_message": str(e),
                "output_directory": os.path.abspath(output_dir),
                "partial_results": True,
            }

    def scrape_url(self, url: str, **kwargs) -> Dict[str, Any]:
        """Convenience method to scrape a single URL"""
        return self.scrape([url], **kwargs)

    def scrape_file(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """Convenience method to scrape a single file"""
        return self.scrape([file_path], **kwargs)

    def get_feature_status(self) -> Dict[str, bool]:
        """Get status of available features"""
        return FEATURES_AVAILABLE.copy()

    def print_features(self):
        """Print feature availability status"""
        print_feature_status()

    def search_and_scrape(
        self, query: str, max_results: int = 10, **scraper_options
    ) -> Dict[str, Any]:
        """
        Search for URLs matching a query and scrape their content.

        Args:
            query: Search query (e.g., "python web scraping tutorial")
            max_results: Maximum number of search results to process
            **scraper_options: Additional options passed to scrape() method

        Returns:
            Dictionary combining search results and scraper results
        """
        if not self.search_engine:
            raise RuntimeError(
                "Search functionality not available. Please initialize with "
                "enable_search=True and provide brave_api_key."
            )

        return self.search_engine.search_and_scrape(
            query=query, max_results=max_results, scraper_options=scraper_options
        )

    def search_only(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for URLs without content extraction.

        Args:
            query: Search query
            max_results: Maximum number of results to return

        Returns:
            List of search results with metadata only
        """
        if not self.search_engine:
            raise RuntimeError(
                "Search functionality not available. Please initialize with "
                "enable_search=True and provide brave_api_key."
            )

        return self.search_engine.search_only(query, max_results)

    def is_search_available(self) -> bool:
        """Check if search functionality is available"""
        return (
            self.search_engine is not None and self.search_engine.check_availability()
        )


class WebCrawler:
    """
    Core web crawler implementation
    """

    def __init__(
        self,
        storage_manager: StorageManager,
        content_parser: ContentParser,
        semantic_analyzer: Optional[SemanticAnalyzer],
        max_workers: int = 5,
        default_depth: int = 1,
        user_topic: Optional[str] = None,
        topic_relevance_threshold: float = 0.5,
        link_relevance_threshold: float = 0.6,
    ):
        """
        Initialize web crawler

        Args:
            storage_manager: Storage manager instance
            content_parser: Content parser instance
            semantic_analyzer: Semantic analyzer instance (optional)
            max_workers: Number of worker threads
            default_depth: Default crawling depth
            user_topic: Topic for semantic filtering
            topic_relevance_threshold: Topic relevance threshold
            link_relevance_threshold: Link relevance threshold
        """
        if max_workers <= 0:
            raise ValueError("max_workers must be greater than 0")

        self.storage_manager = storage_manager
        self.content_parser = content_parser
        self.semantic_analyzer = semantic_analyzer
        self.max_workers = max_workers
        self.default_depth = default_depth
        self.user_topic = user_topic
        self.topic_relevance_threshold = topic_relevance_threshold
        self.link_relevance_threshold = link_relevance_threshold

        # Runtime state
        self.crawl_queue = queue.Queue()
        self.visited_sources = set()
        self.user_topic_embedding = None

        # Initialize topic embedding if semantic analysis is available
        if (
            self.user_topic
            and self.semantic_analyzer
            and self.semantic_analyzer.is_available()
        ):
            self.user_topic_embedding = self.semantic_analyzer.get_embedding(
                self.user_topic
            )
            if self.user_topic_embedding:
                app_logger.info(f"Generated embedding for topic: '{self.user_topic}'")
            else:
                app_logger.warning(
                    f"Could not generate embedding for topic: '{self.user_topic}'"
                )

    def start_crawling(
        self,
        initial_sources: List[str],
        crawl_depth: Optional[int] = None,
        show_progress: bool = True,
    ):
        """
        Start the crawling process

        Args:
            initial_sources: List of initial URLs/paths to crawl
            crawl_depth: Maximum crawling depth
            show_progress: Whether to show progress indicators
        """
        if crawl_depth is not None:
            self.default_depth = crawl_depth

        # Add initial sources to queue
        self.add_to_crawl_queue(initial_sources)

        # Set up progress tracking
        progress = create_progress_display() if show_progress else None
        task_id = None

        if progress:
            with progress as p:
                task_id = p.add_task("Crawling sources", total=self.crawl_queue.qsize())
                self._crawl_with_progress(p, task_id)
        else:
            self._crawl_without_progress()

    def _crawl_with_progress(self, progress, task_id):
        """Crawl with progress display"""
        with ThreadPoolExecutor(
            max_workers=self.max_workers, thread_name_prefix="crawl_worker"
        ) as executor:

            while not self.crawl_queue.empty():
                # Submit batch of tasks
                futures = []
                batch_size = min(self.max_workers * 2, self.crawl_queue.qsize())

                for _ in range(batch_size):
                    if self.crawl_queue.empty():
                        break

                    source, current_depth, origin = self.crawl_queue.get()
                    future = executor.submit(
                        self._process_source, source, current_depth, origin
                    )
                    futures.append(future)

                # Process completed tasks
                for future in as_completed(futures):
                    try:
                        future.result()
                        progress.update(task_id, advance=1)
                    except Exception as e:
                        app_logger.error(f"Error processing source: {e}")
                        progress.update(task_id, advance=1)

    def _crawl_without_progress(self):
        """Crawl without progress display"""
        with ThreadPoolExecutor(
            max_workers=self.max_workers, thread_name_prefix="crawl_worker"
        ) as executor:

            while not self.crawl_queue.empty():
                # Submit batch of tasks
                futures = []
                batch_size = min(self.max_workers * 2, self.crawl_queue.qsize())

                for _ in range(batch_size):
                    if self.crawl_queue.empty():
                        break

                    source, current_depth, origin = self.crawl_queue.get()
                    future = executor.submit(
                        self._process_source, source, current_depth, origin
                    )
                    futures.append(future)

                # Wait for completion
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        app_logger.error(f"Error processing source: {e}")

    def add_to_crawl_queue(
        self, sources: List[str], current_depth: int = 0, origin_source: str = "initial"
    ):
        """Add sources to crawl queue"""
        if isinstance(sources, str):
            sources = [sources]

        newly_added = []
        for source in sources:
            try:
                # Normalize source
                if source.startswith(("http://", "https://")):
                    normalized_source = normalize_url(source)
                else:
                    normalized_source = os.path.abspath(source)

                # Add to queue if not already visited
                if normalized_source not in self.visited_sources:
                    self.visited_sources.add(normalized_source)
                    self.crawl_queue.put(
                        (normalized_source, current_depth, origin_source)
                    )
                    newly_added.append(source)

            except Exception as e:
                app_logger.warning(f"Skipping invalid source '{source}': {e}")

        if newly_added:
            app_logger.info(
                f"Added {len(newly_added)} sources to crawl queue. "
                f"Queue size: {self.crawl_queue.qsize()}"
            )
            self.storage_manager.add_to_queue(newly_added)

    def _process_source(
        self, source: str, current_depth: int, origin_source: str
    ) -> int:
        """
        Process a single source (URL or file)

        Args:
            source: Source URL or file path
            current_depth: Current crawling depth
            origin_source: Source that led to this one

        Returns:
            Number of new links found
        """
        try:
            app_logger.info(
                f"Processing [Depth:{current_depth}]: {source} "
                f"(Origin: {origin_source})"
            )

            # Check if already processed
            if self.storage_manager.is_source_processed(source):
                app_logger.info(f"Source {source} already processed. Skipping.")
                return 0

            # Parse content
            content_text, title, raw_html, error_message = (
                self.content_parser.get_content_and_title(source)
            )

            # Prepare metadata
            crawl_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            metadata_parts = [f"crawled {crawl_date}"]

            is_web_source = source.startswith(("http://", "https://"))

            if error_message:
                app_logger.warning(f"Failed to process {source}: {error_message}")
                metadata_parts.append(f"Error: {error_message}")
                title = title or (
                    os.path.basename(source) if not is_web_source else source
                )
                content_text = ""
            else:
                if is_web_source:
                    metadata_parts.append("HTML page")
                else:
                    ext = os.path.splitext(source)[1].upper()
                    metadata_parts.append(f"{ext} document" if ext else "File")
                    try:
                        file_size = os.path.getsize(source)
                        metadata_parts.append(f"{file_size / 1024:.2f}KB")
                    except OSError:
                        pass

            if origin_source != "initial":
                metadata_parts.append(
                    f"found via {os.path.basename(origin_source)[:50]}"
                )

            metadata_summary = ", ".join(metadata_parts)

            # Semantic analysis
            source_relevance_to_topic = None
            if (
                content_text
                and self.semantic_analyzer
                and self.semantic_analyzer.is_available()
                and self.user_topic_embedding
            ):

                source_relevance_to_topic = (
                    self.semantic_analyzer.score_topic_relevance(
                        content_text[:2000], self.user_topic
                    )
                )
                app_logger.info(
                    f"Topic relevance for {source}: {source_relevance_to_topic:.4f}"
                )

            # Save crawled data
            self.storage_manager.save_crawled_data(
                source,
                title,
                metadata_summary,
                content_text or "",
                source_relevance_to_topic=source_relevance_to_topic,
            )

            # Extract links for further crawling
            new_links_count = 0
            if (
                content_text
                and is_web_source
                and raw_html
                and (self.default_depth == -1 or current_depth < self.default_depth)
            ):

                # Check topic relevance threshold
                if (
                    self.user_topic
                    and source_relevance_to_topic is not None
                    and source_relevance_to_topic < self.topic_relevance_threshold
                ):
                    app_logger.info(
                        f"Content relevance ({source_relevance_to_topic:.4f}) below "
                        f"threshold ({self.topic_relevance_threshold:.4f}). "
                        f"Skipping link extraction."
                    )
                else:
                    new_links_count = self._extract_and_queue_links(
                        raw_html, source, current_depth, content_text
                    )

            return new_links_count

        except Exception as e:
            app_logger.error(f"Error processing source {source}: {e}")
            return 0

    def _extract_and_queue_links(
        self, raw_html: str, source_url: str, current_depth: int, page_content: str
    ) -> int:
        """Extract links from HTML and add relevant ones to queue"""
        try:
            links_data = self.content_parser.extract_links(raw_html, source_url)

            if not links_data:
                return 0

            app_logger.info(f"Discovered {len(links_data)} links on {source_url}")

            # Filter links by relevance - ADVANCED MODE ONLY (can be slow)
            # Only enable if link_relevance_threshold is high (indicating user
            # wants this)
            relevant_links = []
            if (
                self.semantic_analyzer
                and self.semantic_analyzer.is_available()
                and self.link_relevance_threshold > 0.8
            ):  # High threshold = advanced mode

                app_logger.info(
                    f"Advanced link filtering enabled "
                    f"(threshold: {self.link_relevance_threshold})"
                )
                for link_info in links_data:
                    anchor_text = link_info.get("anchor", "")
                    if anchor_text:
                        relevance = self.semantic_analyzer.score_link_relevance(
                            page_content[:1000], anchor_text
                        )
                        if relevance >= self.link_relevance_threshold:
                            relevant_links.append(link_info["url"])
                    else:
                        # Include links without anchor text
                        relevant_links.append(link_info["url"])
            else:
                # Fast mode - include all links (no embedding computation for links)
                relevant_links = [link_info["url"] for link_info in links_data]
                if (
                    self.link_relevance_threshold > 0
                    and self.link_relevance_threshold <= 0.8
                ):
                    app_logger.info(
                        "Fast link processing mode (no embedding analysis for links)"
                    )

            # Add relevant links to crawl queue
            if relevant_links:
                self.add_to_crawl_queue(relevant_links, current_depth + 1, source_url)
                app_logger.info(
                    f"Added {len(relevant_links)} relevant links from {source_url}"
                )

            return len(relevant_links)

        except Exception as e:
            app_logger.error(f"Error extracting links from {source_url}: {e}")
            return 0


# Export main classes
__all__ = ["WebScraperAPI", "WebCrawler"]
