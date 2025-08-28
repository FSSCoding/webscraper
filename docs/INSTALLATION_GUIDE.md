# 🚀 WebScraperPortable Installation Guide

## Quick Start

### Minimal Installation (Basic Features)
For basic web scraping without search engines or semantic analysis:

```bash
pip install requests beautifulsoup4 pandas
```

### Full Installation (All Features)
For complete functionality including search engines and semantic analysis:

```bash
pip install requests beautifulsoup4 pandas ollama numpy rich python-docx PyMuPDF
```

---

## 📦 Dependency Breakdown

### Core Dependencies (Always Required)

| Package | Version | Purpose |
|---------|---------|---------|
| **requests** | ≥ 2.28.0 | HTTP requests, search API calls |
| **beautifulsoup4** | ≥ 4.11.0 | HTML parsing and content extraction |
| **pandas** | ≥ 1.5.0 | Data manipulation and statistics |

```bash
# Core installation
pip install requests beautifulsoup4 pandas
```

### Search Engine Features (Optional)

**API Keys Required:**
- **Brave Search API**: [brave.com/search/api](https://brave.com/search/api) (Free tier available)
- **Tavily API**: [tavily.com](https://tavily.com) (Free tier available)

No additional Python packages required - uses core `requests` library.

### Semantic Analysis Features (Optional)

| Package | Version | Purpose |
|---------|---------|---------|
| **ollama** | ≥ 0.1.0 | Local LLM integration for embeddings |
| **numpy** | ≥ 1.21.0 | Vector operations and similarity calculations |

```bash
# Semantic analysis
pip install ollama numpy

# Setup Ollama (see below)
```

### Enhanced Terminal Output (Optional)

| Package | Version | Purpose |
|---------|---------|---------|
| **rich** | ≥ 13.0.0 | Progress bars, tables, and colorized output |

```bash
pip install rich
```

### Document Parsing (Optional)

| Package | Version | Purpose |
|---------|---------|---------|
| **python-docx** | ≥ 0.8.11 | Microsoft Word document parsing |
| **PyMuPDF** | ≥ 1.21.0 | PDF document parsing and text extraction |

```bash
pip install python-docx PyMuPDF
```

---

## 🔧 Environment Setup

### Search Engine APIs

#### Method 1: Environment Variables (Recommended)
```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export BRAVE_SEARCH_API_KEY="your-brave-api-key-here"
export TAVILY_API_KEY="your-tavily-api-key-here"

# Reload shell or source the file
source ~/.bashrc
```

#### Method 2: Command Line Arguments
```bash
# Use with CLI
python -m WebScraperPortable --search "query" --brave-api-key "your-key"

# Or in Python
from agent_interface import AgentSearchInterface
# Keys will be passed through SearchEngine initialization
```

#### Method 3: Configuration File
Create `.env` file in your project directory:
```bash
# .env file
BRAVE_SEARCH_API_KEY=your-brave-key-here
TAVILY_API_KEY=your-tavily-key-here
```

### Ollama Setup (For Semantic Analysis)

#### Step 1: Install Ollama
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows - Download from https://ollama.ai
```

#### Step 2: Start Ollama Server
```bash
ollama serve
```

#### Step 3: Pull Embedding Model
```bash
ollama pull mxbai-embed-large
```

#### Step 4: Verify Setup
```bash
# Test the model
ollama run mxbai-embed-large "test embedding"
```

---

## 🔍 Feature Verification

### Check Installation Status
```bash
# Command line check
python -m WebScraperPortable --features
```

Expected output:
```
WebScraperPortable Feature Status:

Core Features:
✅ HTTP Requests (requests 2.31.0)
✅ HTML Parsing (beautifulsoup4 4.12.2)
✅ Data Processing (pandas 2.0.3)
✅ Markdown Output (native)

Search Engines:
✅ Brave Search API (API key configured)
✅ Tavily Search API (API key configured)
❌ Search functionality not available (no API keys)

Semantic Analysis:
✅ Ollama Integration (ollama 0.2.1)
✅ Vector Operations (numpy 1.24.3)
✅ Embedding Model Available (mxbai-embed-large)

Enhanced Features:
✅ Rich Terminal Output (rich 13.4.2)
✅ Document Parsing - PDF (PyMuPDF 1.23.3)
✅ Document Parsing - Word (python-docx 0.8.11)

System Status:
✅ All core features operational
✅ Search engines ready
✅ Semantic analysis ready
✅ All optional features available
```

### Python API Check
```python
from WebScraperPortable import WebScraperAPI
from agent_interface import AgentSearchInterface
from search import SearchEngine

# Check core API
api = WebScraperAPI()
api.print_features()

# Check search capabilities
engine = SearchEngine()
print(f"Search available: {engine.is_available}")
print(f"Brave API: {engine.brave_available}")
print(f"Tavily API: {engine.tavily_available}")

# Check agent interface
agent = AgentSearchInterface()
presets = agent.get_available_presets()
print(f"Domain presets available: {len(presets)}")
```

---

## 🛠️ Platform-Specific Instructions

### Ubuntu/Debian
```bash
# Update package list
sudo apt update

# Install Python and pip if needed
sudo apt install python3 python3-pip

# Install WebScraperPortable dependencies
pip3 install -r requirements.txt

# For full features (optional)
pip3 install ollama numpy rich python-docx PyMuPDF

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Set up environment variables
python3 setup_env.py
```

### CentOS/RHEL/Fedora
```bash
# Install Python and pip
sudo dnf install python3 python3-pip  # Fedora
# or
sudo yum install python3 python3-pip  # CentOS/RHEL

# Install dependencies
pip3 install -r requirements.txt

# For full features (optional)
pip3 install ollama numpy rich python-docx PyMuPDF

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Set up environment variables
python3 setup_env.py
```

### macOS
```bash
# Install using Homebrew (recommended)
brew install python3 ollama

# Install Python dependencies
pip3 install -r requirements.txt

# For full features (optional)
pip3 install ollama numpy rich python-docx PyMuPDF

# Set up environment variables
python3 setup_env.py
```

### Windows
```powershell
# Install Python dependencies
pip install -r requirements.txt

# For full features (optional)
pip install ollama numpy rich python-docx PyMuPDF

# Download and install Ollama from https://ollama.ai
# Follow the Windows installer instructions

# Set up environment variables
python setup_env.py
```

---

## 🐳 Docker Setup (Optional)

### Dockerfile Example
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy WebScraperPortable
COPY . /app
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app

# Expose port for Ollama (optional)
EXPOSE 11434

CMD ["python", "-m", "WebScraperPortable", "--help"]
```

### Docker Compose (Full Stack)
```yaml
version: '3.8'

services:
  webscraper:
    build: .
    environment:
      - BRAVE_SEARCH_API_KEY=${BRAVE_SEARCH_API_KEY}
      - TAVILY_API_KEY=${TAVILY_API_KEY}
      - OLLAMA_HOST=ollama:11434
    volumes:
      - ./data:/app/data
      - ./cache:/app/cache
    depends_on:
      - ollama

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    command: ["ollama", "serve"]

volumes:
  ollama_data:
```

---

## ⚡ Performance Optimization

### System Requirements

**Minimum:**
- Python 3.8+
- 512MB RAM
- 1GB disk space

**Recommended:**
- Python 3.11+
- 2GB RAM (4GB for semantic analysis)
- 5GB disk space (for Ollama models)
- SSD storage for better cache performance

### Ollama Optimization
```bash
# Pull optimized model for better performance
ollama pull mxbai-embed-large:latest

# For lower memory usage (if needed)
ollama pull all-minilm:l6-v2

# Set Ollama memory limits (optional)
export OLLAMA_HOST=0.0.0.0:11434
export OLLAMA_MODELS=/path/to/models
```

### Python Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv webscraper_env

# Activate virtual environment
source webscraper_env/bin/activate  # Linux/macOS
# or
webscraper_env\Scripts\activate     # Windows

# Install dependencies in isolated environment
pip install requests beautifulsoup4 pandas ollama numpy rich python-docx PyMuPDF

# Deactivate when done
deactivate
```

---

## 🔧 Troubleshooting

### Common Installation Issues

#### "No module named 'WebScraperPortable'"
```bash
# Ensure you're in the correct directory
cd /path/to/WebScraperPortable

# Or add to Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/WebScraperPortable"
```

#### Ollama Connection Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Start Ollama if not running
ollama serve

# Check available models
ollama list
```

#### Permission Errors
```bash
# Use user installation
pip install --user requests beautifulsoup4 pandas

# Or fix permissions (Linux/macOS)
sudo chown -R $USER ~/.local/
```

#### SSL Certificate Errors
```bash
# Update certificates (macOS)
/Applications/Python\ 3.x/Install\ Certificates.command

# Or disable SSL verification (not recommended for production)
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org requests
```

### Feature-Specific Issues

#### Search APIs Not Working
1. Verify API keys are set correctly
2. Check API key permissions and quotas
3. Test with simple curl commands:
```bash
# Test Brave API
curl -H "X-Subscription-Token: YOUR_BRAVE_KEY" \
     "https://api.search.brave.com/res/v1/web/search?q=test"
```

#### Semantic Analysis Errors
1. Ensure Ollama is running: `ollama serve`
2. Verify model is downloaded: `ollama list`
3. Test model directly: `ollama run mxbai-embed-large "test"`

#### Document Parsing Issues
```bash
# PDF parsing issues - try alternative installation
pip uninstall PyMuPDF
pip install --no-binary PyMuPDF PyMuPDF

# Word document issues
pip install --upgrade python-docx
```

---

## ✅ Verification Steps

### Final Installation Check
```bash
# 1. Set up environment variables
python setup_env.py

# 2. Run feature check
python -m WebScraperPortable --features

# 3. Test basic functionality
python -m WebScraperPortable --url "https://httpbin.org/html" --output "./test_output"

# 4. Test search functionality (if API keys configured)
python -m WebScraperPortable --search-only "python tutorial"

# 5. Test agent interface
python -c "from agent_interface import AgentSearchInterface; print('Agent interface ready')"

# 6. Clean up test output
rm -rf ./test_output
```

### Expected Output
If all features are working correctly, you should see:
- ✅ All core features operational
- ✅ Search engines ready (if API keys provided)
- ✅ Semantic analysis ready (if Ollama configured)
- ✅ Successful test scraping
- ✅ Agent interface imports without errors

---

**Installation Complete!** 🎉

Your WebScraperPortable installation is ready for research and scraping operations. Check the [Usage Examples](USAGE_EXAMPLES.md) for next steps.