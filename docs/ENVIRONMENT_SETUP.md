# 🌍 Environment Setup Guide

## Quick Setup with Script

The easiest way to configure WebScraperPortable with your API keys:

```bash
# Run the interactive setup script
python setup_env.py

# Check your configuration status
python setup_env.py --status
```

---

## Manual .env File Setup

### Step 1: Create .env File

Copy the example file and edit it:

```bash
cp .env.example .env
```

### Step 2: Add Your API Keys

Edit `.env` with your favorite editor:

```bash
# Search Engine API Keys (at least one required for search functionality)
BRAVE_SEARCH_API_KEY=your-actual-brave-search-api-key
TAVILY_API_KEY=your-actual-tavily-api-key

# Ollama Configuration (for semantic analysis)
OLLAMA_HOST=http://localhost:11434

# Cache Configuration (optional)
WEBSCRAPER_CACHE_DIR=/path/to/your/cache
WEBSCRAPER_CACHE_TTL_MINUTES=90

# Performance Settings (optional)
WEBSCRAPER_MAX_WORKERS=8
WEBSCRAPER_REQUEST_TIMEOUT=30

# User Agent (optional)
WEBSCRAPER_USER_AGENT=WebScraperPortable/1.0
```

---

## Getting API Keys

### Brave Search API
1. Visit [brave.com/search/api](https://brave.com/search/api)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Free tier includes 2,000 queries/month

### Tavily API  
1. Visit [tavily.com](https://tavily.com)
2. Sign up for an account
3. Get your API key from the dashboard
4. Free tier includes 1,000 queries/month

---

## Environment Variables Reference

### Search Engine Configuration

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `BRAVE_SEARCH_API_KEY` | Brave Search API key | No* | None |
| `TAVILY_API_KEY` | Tavily Search API key | No* | None |

*At least one search API key is required for search functionality

### Ollama Configuration

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OLLAMA_HOST` | Ollama server URL | No | `http://localhost:11434` |

### Cache Configuration

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `WEBSCRAPER_CACHE_DIR` | Cache directory path | No | System temp directory |
| `WEBSCRAPER_CACHE_TTL_MINUTES` | Cache time-to-live in minutes | No | `90` |

### Performance Settings

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `WEBSCRAPER_MAX_WORKERS` | Maximum worker threads | No | `8` |
| `WEBSCRAPER_REQUEST_TIMEOUT` | HTTP request timeout (seconds) | No | `30` |

### User Agent

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `WEBSCRAPER_USER_AGENT` | Custom User-Agent string | No | `WebScraperPortable/1.0` |

---

## Security Best Practices

### ✅ DO:
- Keep your `.env` file in the project root
- Add `.env` to `.gitignore` (already included)
- Use strong, unique API keys
- Rotate API keys periodically
- Set appropriate file permissions: `chmod 600 .env`

### ❌ DON'T:
- Commit `.env` files to version control
- Share API keys in chat, email, or documentation
- Use the same API keys across multiple projects
- Store API keys in code comments or print statements

---

## Verification and Testing

### Check Environment Status
```bash
# Using the setup script
python setup_env.py --status

# Manual verification
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('Brave:', bool(os.getenv('BRAVE_SEARCH_API_KEY'))); print('Tavily:', bool(os.getenv('TAVILY_API_KEY')))"
```

### Test WebScraperPortable Features
```bash
# Check feature availability
python -m WebScraperPortable --features

# Test search functionality (if API keys configured)
python -m WebScraperPortable --search-only "test query"

# Test semantic analysis (if Ollama configured)
python -c "from WebScraperPortable import WebScraperAPI; api = WebScraperAPI(); api.print_features()"
```

---

## Global vs Project-Specific Configuration

### Option 1: Global Configuration
Place `.env` in your WebScraperPortable directory for use across all projects:
```bash
# Global configuration
/path/to/WebScraperPortable/.env
```

### Option 2: Project-Specific Configuration  
Copy WebScraperPortable to each project and configure separately:
```bash
# Project-specific configuration
/your-project/WebScraperPortable/.env
```

### Option 3: System Environment Variables
Set system-wide environment variables (most secure):
```bash
# Add to ~/.bashrc, ~/.zshrc, etc.
export BRAVE_SEARCH_API_KEY="your-key"
export TAVILY_API_KEY="your-key"
```

---

## Troubleshooting

### "Search functionality not available"
```bash
# Check if .env file exists
ls -la .env

# Check if API keys are loaded
python setup_env.py --status

# Verify file permissions
chmod 600 .env

# Test manual import
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(bool(os.getenv('BRAVE_SEARCH_API_KEY')))"
```

### "python-dotenv not found"
```bash
# Install python-dotenv
pip install python-dotenv

# Or install all requirements
pip install -r requirements.txt
```

### ".env file not loading"
```bash
# Check current directory
pwd

# Check if .env is in the same directory as your Python files
ls -la

# Try absolute path loading
python -c "from dotenv import load_dotenv; load_dotenv('/full/path/to/.env')"
```

### "Invalid API key" errors
1. Verify API key format (no spaces, correct length)
2. Check API key permissions in your dashboard
3. Verify API key quotas haven't been exceeded
4. Test API keys with curl:

```bash
# Test Brave API
curl -H "X-Subscription-Token: YOUR_BRAVE_KEY" \
     "https://api.search.brave.com/res/v1/web/search?q=test"

# Test Tavily API  
curl -X POST "https://api.tavily.com/search" \
     -H "Content-Type: application/json" \
     -d '{"api_key": "YOUR_TAVILY_KEY", "query": "test"}'
```

---

## Advanced Configuration

### Custom Cache Location
```bash
# Set custom cache directory
WEBSCRAPER_CACHE_DIR=/home/user/webscraper_cache

# Ensure directory exists and is writable
mkdir -p /home/user/webscraper_cache
chmod 755 /home/user/webscraper_cache
```

### Performance Tuning
```bash
# For high-performance scenarios
WEBSCRAPER_MAX_WORKERS=16
WEBSCRAPER_REQUEST_TIMEOUT=60
WEBSCRAPER_CACHE_TTL_MINUTES=120

# For low-resource scenarios
WEBSCRAPER_MAX_WORKERS=2
WEBSCRAPER_REQUEST_TIMEOUT=10
WEBSCRAPER_CACHE_TTL_MINUTES=30
```

### Custom User Agent
```bash
# Professional user agent
WEBSCRAPER_USER_AGENT=WebScraperPortable/1.0 (Research Bot; +https://yoursite.com/bot)

# Stealth user agent
WEBSCRAPER_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
```

---

## Integration with Development Tools

### VS Code Integration
Create `.vscode/settings.json`:
```json
{
    "python.envFile": "${workspaceFolder}/.env",
    "python.terminal.activateEnvironment": true
}
```

### PyCharm Integration
1. Go to **File** → **Settings** → **Build, Execution, Deployment** → **Console** → **Python Console**
2. Add environment variables or point to `.env` file

### Jupyter Notebook Integration
```python
# Load environment in notebook
from dotenv import load_dotenv
load_dotenv()

# Verify loading
import os
print("API Keys loaded:", bool(os.getenv('BRAVE_SEARCH_API_KEY')))
```

---

## Deployment Considerations

### Docker
```dockerfile
# Copy .env file (be careful not to include in public images)
COPY .env .env

# Or use Docker secrets/environment variables
ENV BRAVE_SEARCH_API_KEY=${BRAVE_SEARCH_API_KEY}
ENV TAVILY_API_KEY=${TAVILY_API_KEY}
```

### Production Deployment
- Use proper secrets management (Azure Key Vault, AWS Secrets Manager, etc.)
- Don't deploy `.env` files to production
- Use infrastructure-as-code for environment configuration
- Monitor API key usage and set up alerts

---

**Environment Setup Complete!** 🎉

Your WebScraperPortable is now configured and ready to use globally on your machine without exposing API keys to version control.