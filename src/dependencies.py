"""
Dependency Management for WebScraperPortable

Handles optional imports gracefully and provides fallbacks for missing packages.
This allows the scraper to work with minimal dependencies while warning users
about missing features.
"""

import sys
import warnings
from typing import Optional, Any

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv

    load_dotenv()
    _dotenv_available = True
except (ImportError, ModuleNotFoundError):
    _dotenv_available = False

# Track what features are available
FEATURES_AVAILABLE = {
    "semantic_analysis": False,
    "rich_output": False,
    "document_parsing": False,
    "numpy_operations": False,
    "search_capability": False,
}

# Core dependencies (should always be available)
try:
    import requests
    import pandas as pd
    from bs4 import BeautifulSoup

    FEATURES_AVAILABLE["core"] = True
except ImportError as e:
    print(f"❌ CRITICAL: Missing core dependency: {e}")
    print(
        "Please install core requirements: pip install requests beautifulsoup4 pandas"
    )
    sys.exit(1)

# Optional: Semantic Analysis
try:
    import ollama
    import numpy as np

    FEATURES_AVAILABLE["semantic_analysis"] = True
    FEATURES_AVAILABLE["numpy_operations"] = True
except (ImportError, ModuleNotFoundError):
    ollama = None
    np = None

# Optional: Rich Terminal Output
try:
    from rich.console import Console
    from rich.progress import Progress, TaskID
    from rich.table import Table
    from rich.panel import Panel

    FEATURES_AVAILABLE["rich_output"] = True
except (ImportError, ModuleNotFoundError):
    Console = None
    Progress = None
    TaskID = None
    Table = None
    Panel = None

# Optional: Document Parsing
try:
    import docx
    import fitz  # PyMuPDF

    FEATURES_AVAILABLE["document_parsing"] = True
except (ImportError, ModuleNotFoundError):
    docx = None
    fitz = None


# Optional: Search Capability
def check_search_available() -> bool:
    """Check if search functionality is available"""
    import os

    brave_api_key = os.getenv("BRAVE_SEARCH_API_KEY")
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    return brave_api_key is not None or tavily_api_key is not None


FEATURES_AVAILABLE["search_capability"] = check_search_available()


def warn_missing_feature(feature_name: str, functionality: str, install_command: str):
    """Warn user about missing optional features"""
    warning_msg = (
        f"⚠️  {feature_name} not available: {functionality}\n"
        f"   Install with: {install_command}\n"
        f"   Continuing with reduced functionality..."
    )
    warnings.warn(warning_msg, UserWarning)
    print(warning_msg)


def check_semantic_available() -> bool:
    """Check if semantic analysis is available"""
    if not FEATURES_AVAILABLE["semantic_analysis"]:
        warn_missing_feature(
            "Semantic Analysis",
            "Topic filtering and AI-powered link relevance disabled",
            "pip install ollama numpy",
        )
        return False
    return True


def check_rich_available() -> bool:
    """Check if rich terminal output is available"""
    if not FEATURES_AVAILABLE["rich_output"]:
        warn_missing_feature(
            "Rich Terminal Output",
            "Progress bars and pretty formatting disabled",
            "pip install rich",
        )
        return False
    return True


def check_document_parsing_available() -> bool:
    """Check if document parsing is available"""
    if not FEATURES_AVAILABLE["document_parsing"]:
        warn_missing_feature(
            "Document Parsing",
            "Word/PDF document processing disabled",
            "pip install python-docx PyMuPDF",
        )
        return False
    return True


def check_search_capability() -> bool:
    """Check if search capability is available"""
    if not FEATURES_AVAILABLE["search_capability"]:
        warn_missing_feature(
            "Search Capability",
            "Web search and URL discovery disabled",
            "Set BRAVE_SEARCH_API_KEY or TAVILY_API_KEY environment variable",
        )
        return False
    return True


def get_console() -> Optional[Any]:
    """Get rich console or return None"""
    if Console:
        return Console()
    return None


def safe_print(*args, **kwargs):
    """Safe print function that works with or without rich"""
    console = get_console()
    if console:
        console.print(*args, **kwargs)
    else:
        print(*args, **kwargs)


def create_progress_bar():
    """Create progress bar or return None if rich not available"""
    if Progress:
        return Progress()
    return None


def print_feature_status():
    """Print status of all optional features"""
    print("\n🔍 WebScraperPortable Feature Status:")
    features = [
        (
            "Core Web Scraping",
            FEATURES_AVAILABLE.get("core", True),
            "✅ Always Available",
        ),
        (
            "Semantic Analysis",
            FEATURES_AVAILABLE["semantic_analysis"],
            "Ollama + NumPy",
        ),
        ("Rich Terminal Output", FEATURES_AVAILABLE["rich_output"], "Rich"),
        (
            "Document Parsing",
            FEATURES_AVAILABLE["document_parsing"],
            "python-docx + PyMuPDF",
        ),
        (
            "Search Capability",
            FEATURES_AVAILABLE["search_capability"],
            "BRAVE_SEARCH_API_KEY or TAVILY_API_KEY env var",
        ),
    ]

    for feature, available, requirement in features:
        status = "✅ Available" if available else "❌ Missing"
        print(f"   {feature:<20} {status:<12} ({requirement})")

    if not FEATURES_AVAILABLE["semantic_analysis"]:
        print("\n💡 Install semantic features: pip install ollama numpy")
    if not FEATURES_AVAILABLE["rich_output"]:
        print("💡 Install rich output: pip install rich")
    if not FEATURES_AVAILABLE["document_parsing"]:
        print("💡 Install document parsing: pip install python-docx PyMuPDF")
    if not FEATURES_AVAILABLE["search_capability"]:
        print(
            "💡 Enable search: export BRAVE_SEARCH_API_KEY=your_key or "
            "TAVILY_API_KEY=your_key"
        )

    print()


# Export what's available
__all__ = [
    "FEATURES_AVAILABLE",
    "check_semantic_available",
    "check_rich_available",
    "check_document_parsing_available",
    "check_search_capability",
    "check_search_available",
    "get_console",
    "safe_print",
    "create_progress_bar",
    "print_feature_status",
    "requests",
    "pd",
    "BeautifulSoup",
    "ollama",
    "np",
    "Console",
    "Progress",
    "docx",
    "fitz",
]
