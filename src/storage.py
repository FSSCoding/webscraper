"""
Storage Manager Module for WebScraperPortable

Handles data persistence and file storage with thread safety.
Spreadsheet functionality has been removed for simplicity.
"""

import os
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from urllib.parse import urlparse
import hashlib
import json

try:
    from .utils import app_logger, safe_filename
except (ImportError, ModuleNotFoundError):
    from .utils import app_logger, safe_filename

# Configuration
DEFAULT_OUTPUT_FOLDER = "scraped_data"


class StorageManager:
    """
    Thread-safe storage manager for web scraping data (file-based only)
    """

    def __init__(
        self, output_folder: Optional[str] = None, session_name: Optional[str] = None
    ):
        """
        Initialize storage manager

        Args:
            output_folder: Single output directory for markdown files
            session_name: Optional name for this scraping session (used in filenames)
        """
        self.output_folder = output_folder or DEFAULT_OUTPUT_FOLDER
        self.session_name = session_name or self._generate_session_name()

        # Thread safety for file operations
        self._file_lock = threading.Lock()

        # Cache for processed sources (file-based tracking)
        self.processed_sources_cache: Set[str] = set()

        # Initialize storage
        self._initialize_storage()

    def _generate_session_name(self) -> str:
        """Generate session name with incremental number"""
        session_file = os.path.join(
            os.path.dirname(self.output_folder), ".webscraper_sessions.json"
        )

        try:
            # Load existing sessions
            if os.path.exists(session_file):
                with open(session_file, "r") as f:
                    sessions = json.load(f)
            else:
                sessions = {"last_session": 0, "sessions": []}

            # Increment session number
            sessions["last_session"] += 1
            session_num = sessions["last_session"]

            # Save updated sessions
            os.makedirs(os.path.dirname(session_file), exist_ok=True)
            with open(session_file, "w") as f:
                json.dump(sessions, f)

            return f"webscrape_{session_num:03d}"

        except Exception:
            # Fallback to timestamp-based session
            return f"webscrape_{datetime.now().strftime('%H%M%S')}"

    def _initialize_storage(self):
        """Initialize single output directory"""
        # Create single output directory
        os.makedirs(self.output_folder, exist_ok=True)
        app_logger.debug(f"Created output directory: {self.output_folder}")

        # Load existing processed sources from files
        self._load_processed_sources_from_files()

    def _load_processed_sources_from_files(self):
        """Load list of processed sources from existing markdown files"""
        try:
            # Check single output directory for markdown files
            if os.path.exists(self.output_folder):
                for filename in os.listdir(self.output_folder):
                    if filename.endswith(".md"):
                        self.processed_sources_cache.add(filename)

            if self.processed_sources_cache:
                app_logger.info(
                    f"Loaded {len(self.processed_sources_cache)} processed sources "
                    "from existing files"
                )
            else:
                app_logger.info("No previously processed sources found")

        except Exception as e:
            app_logger.error(f"Error loading processed sources from files: {e}")

    def add_to_queue(self, items: List[str]):
        """Add new items to processing queue (simplified - no cache needed)"""
        if not items:
            return
        app_logger.info(f"Added {len(items)} new sources to queue")

    def save_crawled_data(
        self,
        source: str,
        title: str,
        metadata_summary: str,
        content_text: str,
        source_relevance_to_topic: Optional[float] = None,
    ):
        """
        Save crawled data to file system only (no spreadsheet)

        Args:
            source: Source URL or path
            title: Content title
            metadata_summary: Summary of metadata
            content_text: Main content text
            source_relevance_to_topic: Topic relevance score
        """
        # Save content to file
        self._save_content_file(
            source, title, content_text, metadata_summary, source_relevance_to_topic
        )

        # Mark as processed
        self.processed_sources_cache.add(source)

        app_logger.debug(f"Saved crawled data for {source}: {len(content_text)} chars")

    def _save_content_file(
        self,
        source: str,
        title: str,
        content: str,
        metadata_summary: str = "",
        source_relevance_to_topic: Optional[float] = None,
    ):
        """Save content as clean markdown file in single directory"""
        try:
            # Generate clean filename from title
            if title:
                filename_base = safe_filename(title)[:50]  # Limit length
            else:
                # Fallback to domain or file name
                if source.startswith(("http://", "https://")):
                    parsed_url = urlparse(source)
                    filename_base = safe_filename(parsed_url.netloc or "web_content")
                else:
                    filename_base = safe_filename(
                        os.path.basename(source) or "local_file"
                    )

            # Add hash to ensure uniqueness
            source_hash = hashlib.md5(source.encode("utf-8")).hexdigest()[:8]
            filename = f"{self.session_name}_{filename_base}_{source_hash}.md"

            # Write markdown file directly in output folder
            file_path = os.path.join(self.output_folder, filename)
            with open(file_path, "w", encoding="utf-8") as f:
                # Markdown header
                f.write(f"# {title or 'Untitled'}\n\n")

                # Metadata section
                f.write("## Metadata\n\n")
                f.write(f"- **Source:** {source}\n")
                f.write(
                    f"- **Scraped:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                )
                if metadata_summary:
                    f.write(f"- **Type:** {metadata_summary}\n")
                if source_relevance_to_topic is not None:
                    f.write(f"- **Topic Relevance:** {source_relevance_to_topic:.3f}\n")

                # Content section
                f.write("\n## Content\n\n")
                f.write(content)

            app_logger.debug(f"Saved markdown file: {file_path}")

        except Exception as e:
            app_logger.error(f"Error saving markdown file for {source}: {e}")

    def is_source_processed(self, source: str) -> bool:
        """Check if source has been processed"""
        return source in self.processed_sources_cache

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "processed_sources": len(self.processed_sources_cache),
            "output_folder": self.output_folder,
        }


# Factory function
def create_storage_manager(**kwargs) -> StorageManager:
    """Create a storage manager instance"""
    return StorageManager(**kwargs)


__all__ = ["StorageManager", "create_storage_manager", "DEFAULT_OUTPUT_FOLDER"]
