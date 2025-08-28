"""
Utility functions for WebScraperPortable

Provides logging, file operations, and other helper functions with graceful fallbacks.
"""

import os
import logging
import hashlib
from typing import Optional, List, Dict, Any
from urllib.parse import urljoin, urlparse

try:
    from .dependencies import create_progress_bar, FEATURES_AVAILABLE
except (ImportError, ModuleNotFoundError):
    from .dependencies import create_progress_bar, FEATURES_AVAILABLE

# Default configuration
DEFAULT_OUTPUT_FOLDER = "scraped_content"
LOGS_DIR = "logs"


def setup_logger(
    name: str = "WebScraperPortable", log_dir: Optional[str] = None
) -> logging.Logger:
    """
    Set up logger with file and console handlers

    Args:
        name: Logger name
        log_dir: Directory for log files (optional)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler (always available)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if log directory specified)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"{name.lower()}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Global logger instance
app_logger = setup_logger()


def create_output_directories(
    output_folder: str, logs_folder: Optional[str] = None
) -> Dict[str, str]:
    """
    Create necessary output directories

    Args:
        output_folder: Main output directory
        logs_folder: Logs directory (optional)

    Returns:
        Dictionary with created directory paths
    """
    directories = {
        "output": output_folder,
        "web": os.path.join(output_folder, "web"),
        "files": os.path.join(output_folder, "files"),
        "logs": logs_folder or os.path.join(output_folder, "logs"),
    }

    for dir_type, path in directories.items():
        os.makedirs(path, exist_ok=True)
        app_logger.debug(f"Created directory: {path}")

    return directories


def safe_filename(filename: str, max_length: int = 200) -> str:
    """
    Create a safe filename by removing/replacing problematic characters

    Args:
        filename: Original filename
        max_length: Maximum filename length

    Returns:
        Safe filename string
    """
    # Remove/replace problematic characters
    unsafe_chars = '<>:"/\\|?*'
    safe_name = filename
    for char in unsafe_chars:
        safe_name = safe_name.replace(char, "_")

    # Remove multiple consecutive underscores
    while "__" in safe_name:
        safe_name = safe_name.replace("__", "_")

    # Trim to max length and remove trailing dots/spaces
    safe_name = safe_name[:max_length].strip(". ")

    # Ensure we have something
    if not safe_name:
        safe_name = "unnamed_file"

    return safe_name


def get_url_hash(url: str) -> str:
    """
    Generate a hash for a URL for caching/naming purposes

    Args:
        url: URL to hash

    Returns:
        MD5 hash of the URL
    """
    return hashlib.md5(url.encode("utf-8")).hexdigest()


def is_valid_url(url: str) -> bool:
    """
    Check if a string is a valid URL

    Args:
        url: String to validate

    Returns:
        True if valid URL, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def normalize_url(url: str, base_url: Optional[str] = None) -> str:
    """
    Normalize a URL (handle relative URLs, etc.)

    Args:
        url: URL to normalize
        base_url: Base URL for relative URLs

    Returns:
        Normalized absolute URL
    """
    if base_url and not is_valid_url(url):
        # Handle relative URLs
        return urljoin(base_url, url)
    return url


def get_domain(url: str) -> str:
    """
    Extract domain from URL

    Args:
        url: URL to extract domain from

    Returns:
        Domain string
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return "unknown_domain"


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0B"

    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f}{size_names[i]}"


def format_duration(seconds: float) -> str:
    """
    Format duration in human readable format

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def create_progress_display():
    """Create progress display (rich or basic fallback)"""
    if FEATURES_AVAILABLE["rich_output"]:
        return create_progress_bar()
    else:
        return BasicProgress()


class BasicProgress:
    """Basic progress display fallback when rich is not available"""

    def __init__(self):
        self.tasks = {}
        self.task_counter = 0

    def add_task(self, description: str, total: Optional[int] = None):
        """Add a progress task"""
        task_id = self.task_counter
        self.task_counter += 1
        self.tasks[task_id] = {
            "description": description,
            "total": total,
            "completed": 0,
        }
        print(f"🚀 {description}")
        return task_id

    def update(self, task_id: int, completed: int = None, advance: int = None):
        """Update progress"""
        if task_id not in self.tasks:
            return

        task = self.tasks[task_id]
        if advance:
            task["completed"] += advance
        elif completed is not None:
            task["completed"] = completed

        if task["total"]:
            percentage = (task["completed"] / task["total"]) * 100
            print(
                f"📊 {task['description']}: {task['completed']}/{task['total']} "
                f"({percentage:.1f}%)"
            )
        else:
            print(f"📊 {task['description']}: {task['completed']} completed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("✅ Progress tracking completed")


def print_status_table(data: List[Dict[str, Any]], title: str = "Status"):
    """
    Print a status table (with rich formatting if available)

    Args:
        data: List of dictionaries with table data
        title: Table title
    """
    if not data:
        return

    if FEATURES_AVAILABLE["rich_output"]:
        from .dependencies import Table, Console

        table = Table(title=title)

        # Add columns from first row
        for key in data[0].keys():
            table.add_column(key.replace("_", " ").title())

        # Add rows
        for row in data:
            table.add_row(*[str(v) for v in row.values()])

        console = Console()
        console.print(table)
    else:
        # Basic table fallback
        print(f"\n📊 {title}:")
        print("-" * 50)
        for i, row in enumerate(data):
            print(f"Row {i + 1}:")
            for key, value in row.items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
            print()


# Export functions
__all__ = [
    "setup_logger",
    "app_logger",
    "create_output_directories",
    "safe_filename",
    "get_url_hash",
    "is_valid_url",
    "normalize_url",
    "get_domain",
    "format_file_size",
    "format_duration",
    "create_progress_display",
    "BasicProgress",
    "print_status_table",
    "DEFAULT_OUTPUT_FOLDER",
    "LOGS_DIR",
]
