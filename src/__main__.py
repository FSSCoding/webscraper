"""
Entry point for running WebScraperPortable as a module

Usage: python -m WebScraperPortable --url "https://example.com"
       webscraper --url "https://example.com"
"""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
