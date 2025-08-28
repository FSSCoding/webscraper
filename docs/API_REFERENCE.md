# 📚 WebScraperPortable API Reference

## Overview

WebScraperPortable provides three main APIs:

1. **Search Engine API** (`search.py`) - Dual search engine integration with Brave and Tavily
2. **Agent Interface API** (`agent_interface.py`) - Agent-optimized search and research operations 
3. **Traditional Scraper API** (`scraper.py`, `__init__.py`) - Core web scraping functionality

---

## 🔍 Search Engine API

### SearchEngine Class

Primary search engine integration providing Brave Search and Tavily API support.

```python
from search import SearchEngine

engine = SearchEngine(
    brave_api_key="your-brave-key",    # Optional: Brave Search API key
    tavily_api_key="your-tavily-key"   # Optional: Tavily API key
)
```

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `brave_available` | bool | True if Brave API key configured |
| `tavily_available` | bool | True if Tavily API key configured |
| `is_available` | bool | True if at least one API available |
| `session` | requests.Session | HTTP session with connection pooling |

#### Methods

##### `search_only(query, max_results=10)`
Performs search without scraping content.

**Parameters:**
- `query` (str): Search query
- `max_results` (int): Maximum results to return (default: 10)

**Returns:**
```python
[
    {
        "url": "https://example.com",
        "title": "Page Title",
        "description": "Page description",
        "domain": "example.com",
        "quality_score": 1,  # 0-2 quality score
        "source": "brave_search"  # or "tavily"
    }
]
```

**Example:**
```python
results = engine.search_only("python web scraping", max_results=5)
for result in results:
    print(f"{result['title']}: {result['url']}")
```

---

## 🤖 Agent Interface API

### AgentSearchInterface Class

Agent-optimized interface with intelligent caching, domain targeting, and batch operations.

```python
from agent_interface import AgentSearchInterface

agent = AgentSearchInterface(
    cache_dir="./search_cache",    # Optional: Cache directory
    cache_ttl_minutes=90,          # Cache TTL (default: 90 minutes) 
    cache_max_files=1000          # Max cache files (default: 1000)
)
```

#### Domain Presets

Built-in domain filters for targeted searching:

| Preset | Target Domains | Use Case |
|--------|----------------|----------|
| `github` | github.com, gitlab.com | Code repositories |
| `docs` | Official documentation sites | API docs, guides |
| `tutorials` | Educational content sites | Learning materials |
| `stackoverflow` | Stack Overflow, programming Q&A | Programming help |
| `academic` | .edu, research institutions | Academic papers |
| `official` | Official project websites | Authoritative sources |
| `quality` | High-quality, established sites | Reliable information |

#### Core Search Methods

##### `search(query, max_results=10, domain_filter=None)`
Primary search method with intelligent caching and filtering.

**Parameters:**
- `query` (str): Search query
- `max_results` (int): Maximum results to return
- `domain_filter` (str): Domain preset name (optional)

**Returns:**
```python
{
    "status": "success",
    "query": "python web scraping",
    "results_returned": 5,
    "execution_time": 1.23,
    "cache_hit": false,
    "results": [
        {
            "url": "https://example.com",
            "title": "Page Title", 
            "description": "Description",
            "domain": "example.com",
            "quality_score": 1,
            "source": "brave_search"
        }
    ]
}
```

**Example:**
```python
# Basic search
result = agent.search("machine learning tutorials")

# Domain-targeted search
result = agent.search("django authentication", domain_filter="docs")

# High-volume search
result = agent.search("python libraries", max_results=50)
```

##### `batch_search(queries)`
Process multiple queries efficiently with concurrent execution.

**Parameters:**
- `queries` (list): List of query dictionaries

**Query Format:**
```python
{
    "query": "search terms",
    "max_results": 10,        # Optional
    "domain_filter": "github" # Optional
}
```

**Returns:**
```python
{
    "status": "success",
    "total_queries": 3,
    "successful": 3,
    "failed": 0,
    "execution_time": 2.45,
    "results": [
        # Results for each query
    ]
}
```

**Example:**
```python
queries = [
    {"query": "python asyncio", "max_results": 5},
    {"query": "django REST framework", "domain_filter": "docs"},
    {"query": "machine learning pytorch", "domain_filter": "github"}
]
batch_result = agent.batch_search(queries)
```

##### `search_and_validate(query, max_results=10, domain_filter=None)`
Search with automatic content validation and metadata extraction.

**Returns:**
Extended search result with validation summary:
```python
{
    "status": "success",
    "query": "python tutorials",
    "results_returned": 5,
    "validation_summary": {
        "sample_size": 3,
        "avg_content_length": 2500,
        "has_code_examples": 2,
        "tutorial_content": 3
    },
    "results": [
        {
            # Standard result fields plus:
            "validation": {
                "validated": true,
                "content_length": 3200,
                "has_code_blocks": true,
                "is_likely_tutorial": true
            }
        }
    ]
}
```

#### Utility Methods

##### `quick_metadata(urls)`
Extract metadata from URLs without full scraping.

**Parameters:**
- `urls` (list): List of URLs to analyze

**Returns:**
```python
{
    "status": "success", 
    "total_urls": 3,
    "successful": 3,
    "failed": 0,
    "results": {
        "https://example.com": {
            "status": "success",
            "title": "Page Title",
            "content_length": 2500,
            "has_code_blocks": true,
            "is_likely_tutorial": false
        }
    }
}
```

##### `get_available_presets()`
Get list of available domain presets.

**Returns:**
```python
{
    "github": ["github.com", "gitlab.com"],
    "docs": ["docs.python.org", "developer.mozilla.org"],
    # ... other presets
}
```

#### Cache Management

##### `_cache_result(cache_key, result)`
Manually cache search results.

##### `_get_cached_result(cache_key)`
Retrieve cached results.

##### `_cleanup_expired_cache()`
Remove expired cache entries.

##### `_check_cache_size()`
Manage cache size limits.

---

## 🌐 Traditional Scraper API

### WebScraperAPI Class

Core scraping functionality with optional search integration.

```python
from WebScraperPortable import WebScraperAPI

api = WebScraperAPI(
    max_workers=5,           # Worker threads
    enable_semantic=True,    # Semantic analysis  
    enable_search=True,      # Search integration
    user_agent=None,         # Custom user agent
    ollama_host=None         # Ollama server host
)
```

#### Core Methods

##### `scrape(sources, **options)`
Main scraping method with full feature support.

**Parameters:**
- `sources` (list): URLs or file paths to scrape
- `output_dir` (str): Output directory 
- `depth` (int): Crawling depth (-1 for unlimited)
- `topic` (str): Topic for semantic filtering
- `topic_threshold` (float): Topic relevance threshold (0.0-1.0)
- `link_threshold` (float): Link relevance threshold (0.0-1.0)
- `show_progress` (bool): Show progress indicators

**Returns:**
```python
{
    "status": "success",
    "output_directory": "/path/to/scraped_data",
    "targets_processed": 5,
    "depth": 2,
    "session_name": "webscrape_001",
    "duration_seconds": 15.3,
    "cache_stats": {
        "total_sources": 25,
        "processed_sources": 23,
        "unprocessed_sources": 2
    }
}
```

##### `search_and_scrape(query, **options)`
Search for URLs and scrape the results.

**Parameters:**
- `query` (str): Search query
- `brave_api_key` (str): Brave API key (optional)
- `tavily_api_key` (str): Tavily API key (optional)
- `max_results` (int): Maximum search results
- All standard scraping options

**Returns:**
Combined search and scraping results.

##### `search_only(query, **options)`
Search without scraping (discovery mode).

**Parameters:**
- `query` (str): Search query
- `brave_api_key` (str): Brave API key (optional)
- `tavily_api_key` (str): Tavily API key (optional)
- `max_results` (int): Maximum search results

**Returns:**
List of search results without scraping.

#### Utility Methods

##### `print_features()`
Display available feature status.

##### `print_configuration()`
Display current configuration.

---

## 🛠️ Convenience Functions

### Quick Access Functions

```python
from WebScraperPortable import scrape_url, scrape_multiple
```

##### `scrape_url(url, **options)`
Quick single URL scraping.

##### `scrape_multiple(urls, **options)`
Quick multiple URL scraping.

---

## 🎯 Performance Optimizations

### Connection Pooling
- Automatic HTTP session reuse
- Reduces connection overhead by 200-300ms per request
- Uses `requests.Session()` with 30-second timeout

### Request Deduplication
- Prevents duplicate concurrent API calls
- In-memory tracking with automatic cleanup
- Thread-safe implementation

### Intelligent Caching
- 90-minute TTL by default
- Automatic expired cache cleanup
- Size management (removes oldest 20% when > 1000 files)
- Error handling with corrupted file removal

### Fast Mode Operation
- Embedding analysis disabled by default
- Only enables with `link_threshold > 0.8` (advanced mode)
- Optimized for agent usage patterns

---

## 🚨 Error Handling

### Common Exceptions

#### `RuntimeError`
- Search functionality not available (no API keys)
- Required dependencies missing

#### `ConnectionError`  
- API request failures
- Network connectivity issues

#### `ValueError`
- Invalid parameters
- Malformed URLs

### Error Response Format

```python
{
    "status": "error",
    "error_type": "ConnectionError",
    "message": "Failed to connect to search API",
    "details": "Specific error details"
}
```

---

## 📋 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BRAVE_SEARCH_API_KEY` | Brave Search API key | No |
| `TAVILY_API_KEY` | Tavily API key | No |
| `OLLAMA_HOST` | Ollama server host | No |

### Feature Detection

Check feature availability:

```python
# CLI
python -m WebScraperPortable --features

# Python API
api = WebScraperAPI()
api.print_features()

# Search availability
engine = SearchEngine()
print(f"Search available: {engine.is_available}")
```

---

## 🎯 Usage Patterns

### Agent Integration

```python
# Initialize agent with cache
agent = AgentSearchInterface(cache_dir="./cache")

# Research workflow
research_result = agent.search_and_validate(
    "python web frameworks 2024",
    domain_filter="github", 
    max_results=20
)

# Extract URLs for further processing
urls = [r["url"] for r in research_result["results"]]
metadata = agent.quick_metadata(urls[:5])
```

### Batch Research Operations

```python
# Define research queries
research_plan = [
    {"query": "microservices architecture", "domain_filter": "docs"},
    {"query": "kubernetes security", "domain_filter": "official"},
    {"query": "python async performance", "domain_filter": "stackoverflow"}
]

# Execute batch research
batch_result = agent.batch_search(research_plan)

# Process results
for i, query_result in enumerate(batch_result["results"]):
    print(f"Query {i+1}: {query_result['results_returned']} results")
```

### Traditional Web Scraping

```python
# Full-featured scraping
api = WebScraperAPI(max_workers=10, enable_semantic=True)

result = api.scrape(
    sources=["https://example.com"],
    output_dir="./research",
    depth=3,
    topic="machine learning",
    topic_threshold=0.7
)

print(f"Processed {result['targets_processed']} pages")
```

---

**Happy Researching!** 🎉