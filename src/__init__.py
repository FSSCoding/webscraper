"""
WebScraperPortable - Standalone Semantic Web Scraper Module

A self-contained, portable web scraper with optional semantic analysis capabilities.
Drop this module into any project and start scraping with semantic intelligence!

Features:
- 🔗 Multi-threaded web crawling
- 🧠 Optional semantic analysis (with Ollama)
- 📊 Structured data output (Excel, JSON)
- 🎯 Topic-based filtering
- 📁 Configurable output paths
- 🚀 Full API integration support

Usage:
    from WebScraperPortable import scraper
    result = scraper.scrape_url("https://example.com", output_dir="/my/output")

    # Or command line:
    python -m WebScraperPortable --url "https://example.com" --output "/my/output"
"""

__version__ = "1.0.0"
__author__ = "WebScraper Team"
__description__ = "Portable Semantic Web Scraper with Optional AI Features"

# Core imports for API usage
from .scraper import WebScraperAPI
from .cli import main as cli_main


# Convenience functions
def scrape_url(url, output_dir=None, **kwargs):
    """
    Quick function to scrape a single URL

    Args:
        url (str): URL to scrape
        output_dir (str): Output directory (optional)
        **kwargs: Additional options (depth, topic, etc.)

    Returns:
        dict: Result information including output paths
    """
    api = WebScraperAPI()
    return api.scrape([url], output_dir=output_dir, **kwargs)


def scrape_multiple(urls, output_dir=None, **kwargs):
    """
    Quick function to scrape multiple URLs

    Args:
        urls (list): List of URLs to scrape
        output_dir (str): Output directory (optional)
        **kwargs: Additional options (depth, topic, etc.)

    Returns:
        dict: Result information including output paths
    """
    api = WebScraperAPI()
    return api.scrape(urls, output_dir=output_dir, **kwargs)


# Make CLI accessible
__all__ = ["WebScraperAPI", "scrape_url", "scrape_multiple", "cli_main"]
