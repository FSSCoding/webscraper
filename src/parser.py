"""
Content Parser Module for WebScraperPortable

Parses web pages and documents with graceful fallbacks for missing dependencies.
"""

import os
from typing import Tuple, List, Dict, Optional, Any
from urllib.parse import urljoin, urlparse

try:
    from .dependencies import (
        requests,
        BeautifulSoup,
        fitz,
        docx,
        check_document_parsing_available,
    )
    from .utils import app_logger
except (ImportError, ModuleNotFoundError):
    from .dependencies import (
        requests,
        BeautifulSoup,
        fitz,
        docx,
        check_document_parsing_available,
    )
    from .utils import app_logger

# Configuration
MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024  # 2MB
DEFAULT_USER_AGENT = "WebScraperPortable/1.0"


class ContentParser:
    """
    Content parser with graceful fallbacks for missing dependencies
    """

    def __init__(self, user_agent: str = DEFAULT_USER_AGENT):
        """
        Initialize content parser

        Args:
            user_agent: User agent string for HTTP requests
        """
        self.user_agent = user_agent
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        self.document_parsing_available = check_document_parsing_available()

    def get_content_and_title(
        self, source_url_or_path: str
    ) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
        """
        Fetch and parse content from URL or local file

        Args:
            source_url_or_path: URL or file path to parse

        Returns:
            Tuple of (content_text, title, raw_html_content, error_message)
            raw_html_content is only for web pages, None for files
        """
        is_web = source_url_or_path.startswith(("http://", "https://"))

        if is_web:
            return self._parse_html_url(source_url_or_path)
        else:
            text, title, error = self._parse_local_file(source_url_or_path)
            return text, title, None, error

    def _parse_html_url(
        self, url: str
    ) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
        """
        Parse HTML content from URL

        Args:
            url: URL to parse

        Returns:
            Tuple of (text, title, raw_html, error)
        """
        raw_html = None

        try:
            app_logger.debug(f"Fetching URL: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            # Check content type
            content_type = response.headers.get("Content-Type", "").lower()
            if "html" not in content_type:
                error_msg = f"Non-HTML content type: {content_type}"
                app_logger.warning(f"URL {url} returned {content_type}, not HTML")
                return None, None, None, error_msg

            # Store raw HTML
            raw_html = response.text
            soup = BeautifulSoup(raw_html, "html.parser")

            # Extract title
            title = self._extract_title(soup, url)

            # Extract text content
            text = self._extract_text_content(soup)

            app_logger.info(
                f"Successfully parsed {url}: title='{title}', "
                f"content_length={len(text)}"
            )
            return text, title, raw_html, None

        except requests.exceptions.RequestException as e:
            error_msg = f"RequestException: {e}"
            app_logger.error(f"Error fetching {url}: {e}")
            return None, None, raw_html, error_msg

        except Exception as e:
            error_msg = f"ParsingError: {e}"
            app_logger.error(f"Error parsing HTML from {url}: {e}")
            return None, None, raw_html, error_msg

    def _extract_title(self, soup: BeautifulSoup, fallback: str) -> str:
        """Extract title from HTML soup"""
        # Try title tag first
        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            return title_tag.string.strip()

        # Try h1 tag
        h1_tag = soup.find("h1")
        if h1_tag:
            text = h1_tag.get_text(strip=True)
            if text:
                return text

        # Fallback to URL
        return fallback

    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract clean text content from HTML soup"""
        # Remove script and style elements
        for element in soup(["script", "style", "nav", "footer", "aside"]):
            element.decompose()

        # Get text content
        text = soup.get_text(separator=" ", strip=True)

        # Clean up whitespace
        return " ".join(text.split())

    def _parse_local_file(
        self, file_path: str
    ) -> Tuple[Optional[str], str, Optional[str]]:
        """
        Parse local file content

        Args:
            file_path: Path to file

        Returns:
            Tuple of (content, title, error)
        """
        try:
            if not os.path.exists(file_path):
                return None, os.path.basename(file_path), f"File not found: {file_path}"

            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > MAX_FILE_SIZE_BYTES:
                error_msg = (
                    f"File too large: {file_size} bytes > {MAX_FILE_SIZE_BYTES} bytes"
                )
                app_logger.warning(f"Skipping {file_path}: {error_msg}")
                return None, os.path.basename(file_path), error_msg

            # Determine file type and parse
            ext = self._get_file_extension(file_path).lower()
            title = os.path.basename(file_path)

            if ext == ".pdf":
                content = self._parse_pdf(file_path)
            elif ext == ".docx":
                content = self._parse_docx(file_path)
            elif ext in [".md", ".txt"] or self._is_text_file(ext):
                content = self._parse_text_file(file_path)
            else:
                error_msg = f"Unsupported file type: {ext}"
                app_logger.warning(f"Cannot parse {file_path}: {error_msg}")
                return None, title, error_msg

            app_logger.info(
                f"Successfully parsed {file_path}: content_length={len(content)}"
            )
            return content, title, None

        except Exception as e:
            error_msg = f"FileParsingError: {e}"
            app_logger.error(f"Error parsing {file_path}: {e}")
            return None, os.path.basename(file_path), error_msg

    def _get_file_extension(self, file_path: str) -> str:
        """Get file extension"""
        return os.path.splitext(file_path)[1]

    def _is_text_file(self, ext: str) -> bool:
        """Check if extension represents a text file"""
        text_extensions = {
            ".py",
            ".js",
            ".java",
            ".cpp",
            ".c",
            ".h",
            ".html",
            ".htm",
            ".css",
            ".xml",
            ".json",
            ".yaml",
            ".yml",
            ".sql",
            ".sh",
            ".bat",
            ".ps1",
            ".csv",
            ".tsv",
            ".log",
            ".ini",
            ".cfg",
            ".conf",
        }
        return ext in text_extensions

    def _parse_pdf(self, file_path: str) -> str:
        """Parse PDF file content"""
        if not self.document_parsing_available or not fitz:
            raise ValueError(
                "PDF parsing not available - install PyMuPDF: pip install PyMuPDF"
            )

        text = ""
        try:
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text("text") + "\n"
            doc.close()
            return " ".join(text.split())
        except Exception as e:
            app_logger.error(f"Error parsing PDF {file_path}: {e}")
            raise

    def _parse_docx(self, file_path: str) -> str:
        """Parse DOCX file content"""
        if not self.document_parsing_available or not docx:
            raise ValueError(
                "DOCX parsing not available - install python-docx: "
                "pip install python-docx"
            )

        text = ""
        try:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
            return " ".join(text.split())
        except Exception as e:
            app_logger.error(f"Error parsing DOCX {file_path}: {e}")
            raise

    def _parse_text_file(self, file_path: str) -> str:
        """Parse text-based file"""
        try:
            # Try different encodings
            encodings = ["utf-8", "utf-16", "iso-8859-1", "cp1252"]

            for encoding in encodings:
                try:
                    with open(file_path, "r", encoding=encoding) as f:
                        content = f.read()
                        return " ".join(content.split())
                except UnicodeDecodeError:
                    continue

            # If all encodings fail, read with error handling
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                return " ".join(content.split())

        except Exception as e:
            app_logger.error(f"Error parsing text file {file_path}: {e}")
            raise

    def extract_links(self, html_content: str, base_url: str) -> List[Dict[str, str]]:
        """
        Extract links from HTML content

        Args:
            html_content: Raw HTML content
            base_url: Base URL for resolving relative links

        Returns:
            List of link dictionaries with 'url' and 'anchor' keys
        """
        links_data = []

        if not html_content:
            return links_data

        try:
            soup = BeautifulSoup(html_content, "html.parser")

            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"]
                anchor_text = a_tag.get_text(separator=" ", strip=True) or ""

                # Skip certain link types
                if not href or href.startswith(("#", "mailto:", "javascript:", "tel:")):
                    continue

                try:
                    # Resolve relative URLs
                    absolute_url = urljoin(base_url, href.strip())
                    parsed_url = urlparse(absolute_url)

                    # Only include HTTP/HTTPS URLs
                    if parsed_url.scheme in ["http", "https"]:
                        # Remove fragment
                        clean_url = parsed_url._replace(fragment="").geturl()
                        links_data.append({"url": clean_url, "anchor": anchor_text})

                except Exception as e:
                    app_logger.warning(
                        f"Could not parse URL '{href}' from {base_url}: {e}"
                    )

            app_logger.debug(f"Extracted {len(links_data)} links from {base_url}")
            return links_data

        except Exception as e:
            app_logger.error(f"Error extracting links from {base_url}: {e}")
            return []

    def get_page_metadata(self, html_content: str) -> Dict[str, Any]:
        """
        Extract metadata from HTML page

        Args:
            html_content: Raw HTML content

        Returns:
            Dictionary with metadata
        """
        metadata = {
            "title": None,
            "description": None,
            "keywords": None,
            "author": None,
            "language": None,
            "charset": None,
        }

        if not html_content:
            return metadata

        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # Title
            title_tag = soup.find("title")
            if title_tag:
                metadata["title"] = title_tag.get_text(strip=True)

            # Meta tags
            for meta_tag in soup.find_all("meta"):
                name = meta_tag.get("name", "").lower()
                property_name = meta_tag.get("property", "").lower()
                content = meta_tag.get("content", "")

                if name == "description" or property_name == "og:description":
                    metadata["description"] = content
                elif name == "keywords":
                    metadata["keywords"] = content
                elif name == "author":
                    metadata["author"] = content
                elif (
                    name == "language"
                    or meta_tag.get("http-equiv", "").lower() == "content-language"
                ):
                    metadata["language"] = content
                elif meta_tag.get("charset"):
                    metadata["charset"] = meta_tag.get("charset")

            # Language from html tag
            html_tag = soup.find("html")
            if html_tag and not metadata["language"]:
                metadata["language"] = html_tag.get("lang")

            return metadata

        except Exception as e:
            app_logger.error(f"Error extracting metadata: {e}")
            return metadata


# Factory function
def create_content_parser(**kwargs) -> ContentParser:
    """
    Create a content parser instance

    Args:
        kwargs: Keyword arguments to pass to ContentParser constructor

    Returns:
        ContentParser instance
    """
    return ContentParser(**kwargs)


__all__ = [
    "ContentParser",
    "create_content_parser",
    "MAX_FILE_SIZE_BYTES",
    "DEFAULT_USER_AGENT",
]
