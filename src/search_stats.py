"""
Simple search statistics tracker
Maintains a JSON file counting search operations.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any
import fcntl


class SearchStats:
    """Simple search statistics tracker using JSON file"""

    def __init__(self, stats_file: str = "search_stats.json"):
        """Initialize with stats file path"""
        self.stats_file = stats_file
        self._ensure_stats_file()

    def _ensure_stats_file(self):
        """Create stats file if it doesn't exist"""
        if not os.path.exists(self.stats_file):
            initial_stats = {
                "total_searches": 0,
                "first_search": None,
                "last_search": None,
                "searches_by_date": {},
            }
            with open(self.stats_file, "w") as f:
                json.dump(initial_stats, f, indent=2)

    def increment_search_count(self, query: str = None) -> Dict[str, Any]:
        """
        Increment search count and return updated stats

        Args:
            query: Optional search query for logging

        Returns:
            Updated stats dictionary
        """
        current_time = datetime.now().isoformat()
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Use file locking with proper exception handling
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                with open(self.stats_file, "r+") as f:
                    # Apply exclusive lock - will wait if file is locked
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)

                    try:
                        f.seek(0)
                        content = f.read().strip()
                        if content:
                            stats = json.loads(content)
                        else:
                            raise json.JSONDecodeError("Empty file", "", 0)
                    except json.JSONDecodeError:
                        # Reset if corrupted or empty
                        stats = {
                            "total_searches": 0,
                            "first_search": None,
                            "last_search": None,
                            "searches_by_date": {},
                        }

                    # Update stats
                    stats["total_searches"] += 1
                    stats["last_search"] = current_time

                    if stats["first_search"] is None:
                        stats["first_search"] = current_time

                    # Update daily count
                    if current_date not in stats["searches_by_date"]:
                        stats["searches_by_date"][current_date] = 0
                    stats["searches_by_date"][current_date] += 1

                    # Write back to file
                    f.seek(0)
                    f.truncate()
                    json.dump(stats, f, indent=2)
                    f.flush()  # Force write to disk

                    # Lock will be released when 'with' block exits
                    return stats

            except (IOError, OSError):
                retry_count += 1
                if retry_count >= max_retries:
                    # Fallback - just return current stats without increment
                    return self.get_stats()
                import time

                time.sleep(0.01)  # Brief delay before retry

        return self.get_stats()

    def get_stats(self) -> Dict[str, Any]:
        """Get current search statistics"""
        try:
            with open(self.stats_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._ensure_stats_file()
            return self.get_stats()

    def get_search_count(self) -> int:
        """Get just the total search count"""
        stats = self.get_stats()
        return stats.get("total_searches", 0)


def log_search(query: str = None) -> int:
    """
    Convenience function to log a search and return total count

    Args:
        query: Optional search query

    Returns:
        Total number of searches performed
    """
    stats_tracker = SearchStats()
    updated_stats = stats_tracker.increment_search_count(query)
    return updated_stats["total_searches"]


def get_search_count() -> int:
    """Get current total search count"""
    stats_tracker = SearchStats()
    return stats_tracker.get_search_count()
