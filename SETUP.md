# WebScraperPortable Setup Guide

🚀 **Get WebScraperPortable running in minutes!**

## 📋 Quick Start Checklist

### ✅ Step 1: Copy the Module
Copy the entire `WebScraperPortable` folder into your project:

```bash
cp -r WebScraperPortable /path/to/your/project/
```

### ✅ Step 2: Install Core Dependencies
**Minimum requirements for basic web scraping:**

```bash
pip install requests beautifulsoup4 pandas openpyxl
```

### ✅ Step 3: Test Basic Functionality
```bash
cd /path/to/your/project
python -m WebScraperPortable --url "https://httpbin.org/html" --output "./test_results"
```

If this works, you're ready to go! 🎉

## 🔧 Optional Enhancements

### 🧠 Semantic Analysis (AI Features)
For topic filtering and intelligent link following:

1. **Install Ollama**: [https://ollama.ai/download](https://ollama.ai/download)
2. **Start Ollama server**: `ollama serve`
3. **Pull embedding model**: `ollama pull mxbai-embed-large`
4. **Install Python packages**: `pip install ollama numpy`

**Test semantic features:**
```bash
python -m WebScraperPortable --url "https://example.com" --topic "technology" --depth 2
```

### 🎨 Enhanced Terminal Output
For progress bars and pretty formatting:

```bash
pip install rich
```

### 📄 Document Parsing
For PDF and Word document support:

```bash
pip install PyMuPDF python-docx
```

## 🔍 Verify Installation

### Check Feature Status
```bash
python -m WebScraperPortable --features
```

This will show you which features are available:
```
🔍 WebScraperPortable Feature Status:
   Core Web Scraping    ✅ Available     (✅ Always Available)
   Semantic Analysis    ❌ Missing       (Ollama + NumPy)
   Rich Terminal Output ✅ Available     (Rich)
   Document Parsing     ✅ Available     (python-docx + PyMuPDF)

💡 Install semantic features: pip install ollama numpy
```

### Run Test Suite
```python
# test_installation.py
from WebScraperPortable import scrape_url, WebScraperAPI

# Test basic functionality
result = scrape_url("https://httpbin.org/html", output_dir="./test_output")
print(f"✅ Test successful! Results in: {result['output_directory']}")

# Test API
api = WebScraperAPI()
api.print_features()
```

## 🚀 Usage Examples

### Command Line
```bash
# Basic scraping
python -m WebScraperPortable --url "https://example.com" --output "./results"

# Multiple URLs
python -m WebScraperPortable --url "https://site1.com" --url "https://site2.com"

# With topic filtering (requires semantic features)
python -m WebScraperPortable --url "https://news.ycombinator.com" --topic "artificial intelligence"

# Quiet mode for scripts
python -m WebScraperPortable --url "https://example.com" --json-output --quiet
```

### Python API
```python
from WebScraperPortable import scrape_url, scrape_multiple, WebScraperAPI

# Simple URL scraping
result = scrape_url("https://example.com", output_dir="./my_results")

# Multiple URLs with options
result = scrape_multiple(
    ["https://site1.com", "https://site2.com"],
    output_dir="./results",
    depth=2,
    topic="programming"
)

# Advanced API usage
api = WebScraperAPI(max_workers=10)
result = api.scrape(
    sources=["https://example.com"],
    depth=3,
    topic="machine learning",
    topic_threshold=0.7
)
```

## 🛠️ Integration Patterns

### As a Subprocess
```python
import subprocess
import json

result = subprocess.run([
    "python", "-m", "WebScraperPortable",
    "--url", "https://example.com",
    "--output", "./scrape_results",
    "--json-output", "--quiet"
], capture_output=True, text=True)

if result.returncode == 0:
    data = json.loads(result.stdout)
    print(f"Scraping successful: {data['output_directory']}")
else:
    print(f"Error: {result.stderr}")
```

### In a Flask App
```python
from flask import Flask, request, jsonify
from WebScraperPortable import scrape_url

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape_endpoint():
    url = request.json.get('url')
    topic = request.json.get('topic')
    
    result = scrape_url(
        url, 
        output_dir=f"./scrapes/{session_id}",
        topic=topic
    )
    
    return jsonify(result)
```

### In a Jupyter Notebook
```python
# Install in notebook
!pip install requests beautifulsoup4 pandas openpyxl

# Use in cell
from WebScraperPortable import scrape_url
import pandas as pd

result = scrape_url("https://example.com")
df = pd.read_excel(result['spreadsheet_path'])
df.head()
```

## 🔧 Configuration

### Environment Variables
```bash
# Optional: Set Ollama host
export OLLAMA_HOST=http://localhost:11434

# Optional: Set default output directory
export WEBSCRAPER_OUTPUT_DIR=./default_scrapes
```

### Custom Configuration
```python
from WebScraperPortable import WebScraperAPI

# Custom configuration
api = WebScraperAPI(
    max_workers=20,           # More threads for faster processing
    enable_semantic=True,     # Enable AI features
    user_agent="MyBot/1.0",  # Custom user agent
    ollama_host="http://custom-ollama:11434"  # Custom Ollama server
)
```

## 🆘 Troubleshooting

### Common Issues

**"Missing core dependency"**
```bash
pip install requests beautifulsoup4 pandas openpyxl
```

**"Semantic analysis not available"**
```bash
# Install Ollama from https://ollama.ai
ollama serve
ollama pull mxbai-embed-large
pip install ollama numpy
```

**"Permission denied" on output directory**
```bash
mkdir -p ./scrape_results
chmod 755 ./scrape_results
```

**"Rich terminal output not available"**
```bash
pip install rich
# OR: use without rich (basic functionality still works)
```

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

from WebScraperPortable import scrape_url
result = scrape_url("https://example.com", output_dir="./debug_output")
```

### Feature Detection
```python
from WebScraperPortable import WebScraperAPI

api = WebScraperAPI()
features = api.get_feature_status()

if features['semantic_analysis']:
    print("✅ AI features available")
else:
    print("❌ AI features not available - install ollama and numpy")
```

## 📦 Deployment

### Docker Example
```dockerfile
FROM python:3.9-slim

# Install core dependencies
RUN pip install requests beautifulsoup4 pandas openpyxl

# Copy WebScraperPortable module
COPY WebScraperPortable /app/WebScraperPortable

WORKDIR /app

# Run scraper
CMD ["python", "-m", "WebScraperPortable", "--url", "https://example.com"]
```

### AWS Lambda
```python
# lambda_function.py
import json
from WebScraperPortable import scrape_url

def lambda_handler(event, context):
    url = event.get('url')
    result = scrape_url(url, output_dir='/tmp/scrape_results')
    
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
```

## 🎯 Next Steps

1. **Start with basic scraping** to verify everything works
2. **Add semantic features** if you need AI-powered filtering
3. **Integrate into your application** using the Python API
4. **Scale up** with more threads and advanced options
5. **Monitor performance** and adjust configurations as needed

## 📚 Further Reading

- **README.md** - Complete feature documentation
- **API Reference** - Detailed method documentation
- **Main project** - Web-Scraper repository for latest updates

---

**You're all set!** 🚀 Happy scraping with WebScraperPortable! 