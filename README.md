# WebScraperPortable

🚀 **A self-contained, portable web scraper with optional semantic analysis capabilities.**

Drop this module into any project and start scraping with semantic intelligence!

## ✨ Features

- **🔗 Multi-threaded web crawling** - Fast and efficient crawling with configurable workers
- **🧠 Optional semantic analysis** - AI-powered content filtering and link relevance (with Ollama)
- **📊 Structured data output** - Clean markdown files with session-based naming
- **🎯 Topic-based filtering** - Focus crawling on specific topics
- **📁 Configurable output paths** - Control exactly where results are saved
- **🛡️ Graceful degradation** - Works with minimal dependencies, optional features warn if missing
- **🔄 Thread-safe operations** - Safe for concurrent use
- **📝 Comprehensive logging** - Full audit trail of scraping operations

## 🚀 Quick Start

### Installation

**Option 1: Minimal installation (basic web scraping)**
```bash
pip install requests beautifulsoup4 pandas
```

**Option 2: Full installation (all features including semantic analysis)**
```bash
pip install requests beautifulsoup4 pandas ollama numpy rich python-docx PyMuPDF
```

### Command Line Usage

```bash
# Basic web scraping
python -m WebScraperPortable --url "https://example.com" --output "./results"

# With semantic analysis and topic filtering
python -m WebScraperPortable --url "https://example.com" --topic "python programming" --depth 3

# Multiple URLs with custom output
python -m WebScraperPortable --url "https://site1.com" --url "https://site2.com" --output "./my_results"

# Folder analysis
python -m WebScraperPortable --folder "/path/to/documents" --output "./analysis"

# JSON output for integration
python -m WebScraperPortable --url "https://example.com" --json-output --quiet
```

### Python API Usage

```python
from WebScraperPortable import scrape_url, scrape_multiple, WebScraperAPI

# Quick single URL scraping
result = scrape_url("https://example.com", output_dir="./results")
print(f"Results saved to: {result['output_directory']}")

# Multiple URLs
urls = ["https://site1.com", "https://site2.com"]
result = scrape_multiple(urls, output_dir="./results", topic="technology")

# Advanced usage with API class
api = WebScraperAPI(max_workers=10)
result = api.scrape(
    sources=["https://example.com"],
    output_dir="./results",
    depth=3,
    topic="machine learning",
    topic_threshold=0.6
)

# Check feature availability
api.print_features()
```

## 📋 Dependencies

### Core Dependencies (Required)
- **requests** >= 2.28.0 - HTTP requests
- **beautifulsoup4** >= 4.11.0 - HTML parsing  
- **pandas** >= 1.5.0 - Data manipulation

### Optional Dependencies (Enhanced Features)

**Semantic Analysis & AI Features:**
- **ollama** >= 0.1.0 - LLM embeddings and semantic analysis
- **numpy** >= 1.21.0 - Vector operations for similarity calculations

**Enhanced Terminal Output:**
- **rich** >= 13.0.0 - Progress bars and pretty formatting

**Document Parsing:**
- **python-docx** >= 0.8.11 - Word document parsing
- **PyMuPDF** >= 1.21.0 - PDF document parsing

## 🛠️ API Reference

### WebScraperAPI Class

```python
api = WebScraperAPI(
    max_workers=5,          # Number of worker threads
    enable_semantic=True,   # Enable semantic analysis
    user_agent=None,       # Custom user agent
    ollama_host=None       # Ollama server host
)
```

### Main Methods

#### `scrape(sources, **options)`

```python
result = api.scrape(
    sources=["https://example.com"],     # URLs or file paths
    output_dir="./scraped_data",         # Output directory
    depth=1,                            # Crawling depth (-1 for unlimited)
    topic=None,                         # Topic for semantic filtering
    topic_threshold=0.5,                # Topic relevance threshold (0.0-1.0)
    link_threshold=0.6,                 # Link relevance threshold (0.0-1.0)
    show_progress=True                  # Show progress indicators
)
```

#### Return Format

```python
{
    "status": "success",
    "output_directory": "/absolute/path/to/scraped_data",
    "targets_processed": 5,
    "depth": 2,
    "duration_seconds": 15.3,
    "cache_stats": {
        "processed_sources": 23
    },
    "session_name": "webscrape_001"
}
```

## 📁 Output Structure

```
scraped_data/
├── webscrape_001_Example Domain_c984d06a.md
├── webscrape_001_GitHub Repository_2402e3d1.md
├── webscrape_002_Documentation Page_5f7a9b3e.md
└── webscrape_002_Tutorial Guide_8d2c4f1a.md
```

### File Naming Convention

Files use session-based naming: `webscrape_{session}_{title}_{hash}.md`

- **`webscrape_001`**: Session identifier (incremental)
- **`Example Domain`**: Descriptive page title
- **`c984d06a`**: Unique hash to prevent collisions

## 🔧 Configuration Options

### Command Line Arguments

#### Search Engine Options
| Argument | Description | Default |
|----------|-------------|---------|  
| `--search` | Search query to find and scrape URLs | - |
| `--search-only` | Search without scraping (discovery mode) | - |
| `--search-results` | Maximum search results | `10` |
| `--brave-api-key` | Brave Search API key | Environment: `BRAVE_SEARCH_API_KEY` |
| `--tavily-api-key` | Tavily API key | Environment: `TAVILY_API_KEY` |

#### Traditional Scraping Options
| Argument | Description | Default |
|----------|-------------|---------|
| `--url` | URL to scrape (repeatable) | - |
| `--folder` | Local folder to crawl (repeatable) | - |
| `--output` | Output directory | `scraped_content` |
| `--depth` | Crawling depth (-1 unlimited) | `1` |
| `--threads` | Worker threads | `5` |
| `--topic` | Topic for filtering | - |
| `--topic-threshold` | Topic relevance threshold | `0.5` |
| `--link-threshold` | Link relevance threshold | `0.6` |
| `--json-output` | Output JSON instead of text | `False` |
| `--quiet` | Suppress progress output | `False` |
| `--features` | Show available features | - |

## 🔍 Search Engine Integration

WebScraperPortable now includes comprehensive search engine integration for automatic URL discovery and content research.

### Supported Search Engines

- **Brave Search API**: Web search with automatic spam filtering and quality scoring
- **Tavily API**: AI-optimized search results with content preprocessing
- **Automatic Fallback**: Seamlessly switches between engines for reliability

### Setup Search Engines

1. **Get API Keys**:
   - Brave Search: [brave.com/search/api](https://brave.com/search/api)
   - Tavily: [tavily.com](https://tavily.com)

2. **Set Environment Variables**:
   ```bash
   export BRAVE_SEARCH_API_KEY="your-brave-key"
   export TAVILY_API_KEY="your-tavily-key"
   ```

3. **Or use command line arguments**:
   ```bash
   python -m WebScraperPortable --search "your query" --brave-api-key "your-key"
   ```

### Domain Presets

Target specific types of content with built-in domain filters:

- **`github`**: GitHub repositories and documentation
- **`docs`**: Official documentation sites 
- **`tutorials`**: Educational and tutorial content
- **`stackoverflow`**: Stack Overflow Q&A
- **`academic`**: Academic papers and research
- **`official`**: Official project websites
- **`quality`**: High-quality, well-established sites

```python
# Target GitHub repositories
result = agent.search("python web scraping", domain_filter="github")

# Focus on documentation
result = agent.search("django authentication", domain_filter="docs")
```

### Performance Optimizations

- **Connection Pooling**: Reuses HTTP connections for 40-60% faster requests
- **Request Deduplication**: Prevents duplicate API calls during concurrent operations  
- **Smart Caching**: 90-minute TTL with automatic cleanup
- **Fast Mode**: Disables slow embedding analysis by default for speed

## 🎯 Semantic Analysis

When Ollama and NumPy are installed, WebScraperPortable provides powerful semantic analysis:

- **Topic Filtering**: Only crawl content relevant to your specified topic
- **Link Relevance**: Follow only semantically relevant links (advanced mode only)
- **Content Scoring**: Automatic relevance scoring for all content

### Setup Semantic Features

1. **Install Ollama**: [https://ollama.ai](https://ollama.ai)
2. **Pull embedding model**: `ollama pull mxbai-embed-large`
3. **Install Python dependencies**: `pip install ollama numpy`

### Example with Semantic Analysis

```python
# Topic-focused crawling
result = scrape_url(
    "https://news.ycombinator.com",
    topic="artificial intelligence",
    depth=3,
    topic_threshold=0.7,  # Only very relevant content
    output_dir="./ai_news"
)

# Advanced mode with slow embedding analysis (link_threshold > 0.8)
result = scrape_url(
    "https://example.com", 
    topic="machine learning",
    link_threshold=0.85,  # Enable advanced embedding analysis
    output_dir="./ml_research"
)
```

## 🔍 Troubleshooting

### Common Issues

**"Search functionality not available"**
- Set API keys: `export BRAVE_SEARCH_API_KEY="your-key"`
- Or use command line: `--brave-api-key "your-key"`
- Check feature status: `python -m WebScraperPortable --features`

**"Semantic analysis not available"**
- Install: `pip install ollama numpy`
- Ensure Ollama is running: `ollama serve`

**"Rich terminal output not available"**
- Install: `pip install rich`
- Or use basic output (functionality unchanged)

**"Document parsing not available"**
- For PDFs: `pip install PyMuPDF`
- For Word docs: `pip install python-docx`

**Slow performance with many links**
- Embedding analysis is disabled by default for speed
- Only enables with high link thresholds (> 0.8)
- Use `--topic` for content filtering instead

### Feature Status Check

```bash
python -m WebScraperPortable --features
```

```python
from WebScraperPortable import WebScraperAPI
api = WebScraperAPI()
api.print_features()
```

## 🚀 Integration Examples

### Django/Flask Integration

```python
# views.py - Traditional scraping
from WebScraperPortable import scrape_url

def scrape_endpoint(request):
    url = request.POST.get('url')
    result = scrape_url(url, output_dir=f"./scrapes/{user.id}")
    return JsonResponse(result)

# views.py - Search and research
from agent_interface import AgentSearchInterface

def research_endpoint(request):
    query = request.POST.get('query')
    domain_filter = request.POST.get('domain', None)
    
    agent = AgentSearchInterface(cache_dir=f"./cache/{user.id}")
    result = agent.search_and_validate(
        query, 
        domain_filter=domain_filter,
        max_results=20
    )
    return JsonResponse(result)
```

### Jupyter Notebook

```python
# Cell 1: Install and setup
!pip install requests beautifulsoup4 pandas openpyxl

# Cell 2: Quick scraping
from WebScraperPortable import scrape_url
result = scrape_url("https://example.com")

# Cell 3: Check results
import os
output_dir = result['output_directory'] 
files = [f for f in os.listdir(output_dir) if f.endswith('.md')]
print(f"Generated {len(files)} markdown files in session {result['session_name']}")
```

### Scheduled Tasks

```python
# cron_scraper.py - Traditional approach
import schedule
import time
from WebScraperPortable import scrape_multiple

def daily_scrape():
    urls = ["https://news.com", "https://blog.com"]
    result = scrape_multiple(
        urls, 
        output_dir=f"./daily_scrapes/{datetime.now().strftime('%Y-%m-%d')}",
        topic="technology news"
    )
    print(f"Scraped {result['cache_stats']['processed_sources']} sources")

schedule.every().day.at("09:00").do(daily_scrape)

# cron_research.py - Search-based approach
from agent_interface import AgentSearchInterface
import os
from datetime import datetime

def daily_research():
    agent = AgentSearchInterface(
        cache_dir="./research_cache"
    )
    
    # Multiple research queries
    queries = [
        {"query": "python machine learning 2024", "domain_filter": "github"},
        {"query": "javascript frameworks performance", "domain_filter": "docs"},
        {"query": "cybersecurity best practices", "domain_filter": "official"}
    ]
    
    batch_result = agent.batch_search(queries)
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # Save research results
    with open(f"./research_reports/{date_str}.json", "w") as f:
        import json
        json.dump(batch_result, f, indent=2)
    
    print(f"Completed {batch_result['successful']} research queries")

schedule.every().day.at("09:00").do(daily_research)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## 📝 License

This project is part of the larger Web-Scraper project. See the main project for license information.

## 🤝 Contributing

WebScraperPortable is designed to be self-contained and portable. When contributing:

1. Maintain graceful dependency degradation
2. Ensure all features work with minimal dependencies
3. Add comprehensive error handling
4. Update both Python API and CLI interfaces

## 🆘 Support

For issues, feature requests, or questions:

1. Check the feature status: `python -m WebScraperPortable --features`
2. Review the troubleshooting section above
3. Create an issue in the main Web-Scraper repository

---

**Happy Scraping!** 🎉 