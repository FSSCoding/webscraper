# 🎯 WebScraperPortable Usage Examples

## Quick Start Examples

### 🔍 Search and Discovery

#### Basic Search Operation
```python
from agent_interface import AgentSearchInterface

# Initialize agent
agent = AgentSearchInterface()

# Simple search
result = agent.search("python web scraping tutorials", max_results=10)
print(f"Found {result['results_returned']} results")

for item in result['results']:
    print(f"• {item['title']}: {item['url']}")
```

#### Domain-Targeted Research
```python
# Target specific domains for better results
github_results = agent.search(
    "machine learning algorithms", 
    domain_filter="github",
    max_results=15
)

docs_results = agent.search(
    "django authentication", 
    domain_filter="docs", 
    max_results=10
)

stackoverflow_results = agent.search(
    "python async performance", 
    domain_filter="stackoverflow",
    max_results=20
)
```

#### Batch Research Operations
```python
# Research multiple topics efficiently
research_queries = [
    {
        "query": "microservices architecture patterns",
        "domain_filter": "docs",
        "max_results": 10
    },
    {
        "query": "kubernetes security best practices", 
        "domain_filter": "official",
        "max_results": 15
    },
    {
        "query": "python asyncio examples",
        "domain_filter": "github",
        "max_results": 20
    }
]

batch_result = agent.batch_search(research_queries)
print(f"Completed {batch_result['successful']}/{batch_result['total_queries']} queries")

# Process each query result
for i, query_result in enumerate(batch_result['results']):
    print(f"\nQuery {i+1}: {research_queries[i]['query']}")
    print(f"Results: {query_result['results_returned']}")
    
    for result in query_result['results'][:3]:  # Show top 3
        print(f"  • {result['title']}")
```

---

## 🌐 Traditional Web Scraping

### Single URL Scraping
```python
from WebScraperPortable import scrape_url

# Basic scraping
result = scrape_url(
    "https://python.org", 
    output_dir="./python_research"
)

print(f"Results saved to: {result['output_directory']}")
print(f"Session: {result['session_name']}")
```

### Multiple URL Scraping
```python
from WebScraperPortable import scrape_multiple

urls = [
    "https://docs.python.org",
    "https://realpython.com", 
    "https://python-guide.org"
]

result = scrape_multiple(
    urls,
    output_dir="./python_resources",
    topic="python best practices",
    depth=2
)

print(f"Processed {result['targets_processed']} sources")
```

### Advanced Scraping with Semantic Analysis
```python
from WebScraperPortable import WebScraperAPI

# Initialize with semantic features enabled
api = WebScraperAPI(
    max_workers=8,
    enable_semantic=True
)

# Topic-focused deep crawling
result = api.scrape(
    sources=["https://news.ycombinator.com"],
    output_dir="./ai_research",
    topic="artificial intelligence",
    topic_threshold=0.7,  # Only highly relevant content
    depth=3,
    show_progress=True
)

print(f"AI-related content saved to: {result['web_content_dir']}")
```

---

## 🚀 Combined Search & Scrape

### Search-Driven Content Collection
```python
from WebScraperPortable import WebScraperAPI

# Initialize with search capabilities
api = WebScraperAPI(max_workers=10, enable_search=True)

# Search and automatically scrape results
result = api.search_and_scrape(
    query="django tutorial 2024",
    brave_api_key="your-brave-key",  # or set environment variable
    max_results=20,
    output_dir="./django_tutorials",
    topic="django web development",
    depth=2
)

print(f"Found and scraped {result['targets_processed']} Django tutorials")
```

### Discovery Mode (Search Only)
```python
# Use search for URL discovery without scraping
search_results = api.search_only(
    query="python machine learning libraries",
    max_results=50,
    brave_api_key="your-key"
)

# Process discovered URLs
for result in search_results:
    print(f"{result['title']}: {result['url']}")
    print(f"  Quality Score: {result['quality_score']}")
    print(f"  Domain: {result['domain']}")
```

---

## 🤖 Agent Integration Patterns

### Research Agent Workflow
```python
from agent_interface import AgentSearchInterface

# Initialize with persistent cache
agent = AgentSearchInterface(
    cache_dir="./research_cache",
    cache_ttl_minutes=120  # 2 hours
)

def research_topic(topic, max_urls=30):
    """Complete research workflow for a topic"""
    
    # 1. Initial broad search
    broad_results = agent.search(
        f"{topic} overview", 
        max_results=10
    )
    
    # 2. Targeted searches
    github_results = agent.search(
        f"{topic} implementation examples",
        domain_filter="github", 
        max_results=15
    )
    
    docs_results = agent.search(
        f"{topic} documentation",
        domain_filter="docs",
        max_results=10
    )
    
    # 3. Validation and metadata
    all_urls = []
    for result_set in [broad_results, github_results, docs_results]:
        all_urls.extend([r["url"] for r in result_set["results"]])
    
    # Quick validation of top results
    metadata = agent.quick_metadata(all_urls[:max_urls])
    
    return {
        "broad_search": broad_results,
        "github_examples": github_results, 
        "documentation": docs_results,
        "url_metadata": metadata
    }

# Research machine learning
ml_research = research_topic("machine learning", max_urls=20)
print(f"Found {len(ml_research['url_metadata']['results'])} validated URLs")
```

### Validation-First Approach
```python
# Search with automatic content validation
validated_results = agent.search_and_validate(
    "python web scraping best practices",
    max_results=25
)

print("Validation Summary:")
print(f"• Sample size: {validated_results['validation_summary']['sample_size']}")
print(f"• Avg content length: {validated_results['validation_summary']['avg_content_length']}")
print(f"• Has code examples: {validated_results['validation_summary']['has_code_examples']}")

# Filter for high-quality tutorial content
quality_results = [
    result for result in validated_results['results']
    if result['validation']['is_likely_tutorial'] 
    and result['validation']['has_code_blocks']
]

print(f"\nFound {len(quality_results)} high-quality tutorial results")
```

---

## 📊 Data Analysis Integration

### Jupyter Notebook Research
```python
# Cell 1: Setup
from agent_interface import AgentSearchInterface
import pandas as pd
import json

agent = AgentSearchInterface(cache_dir="./notebook_cache")

# Cell 2: Research queries
research_data = []
topics = ["pandas", "numpy", "matplotlib", "scikit-learn"]

for topic in topics:
    results = agent.search(f"{topic} tutorial examples", max_results=20)
    research_data.append({
        "topic": topic,
        "results_count": results["results_returned"],
        "execution_time": results["execution_time"],
        "cache_hit": results["cache_hit"],
        "urls": [r["url"] for r in results["results"]]
    })

# Cell 3: Analysis
df = pd.DataFrame(research_data)
print(df[['topic', 'results_count', 'execution_time']])

# Cell 4: URL validation
all_urls = []
for data in research_data:
    all_urls.extend(data['urls'][:5])  # Top 5 per topic

metadata = agent.quick_metadata(all_urls)
print(f"Validated {len(metadata['results'])} URLs")
```

### Data Export and Processing
```python
# Export research results for external processing
def export_research_results(search_result, filename):
    """Export search results to various formats"""
    
    # JSON export
    with open(f"{filename}.json", "w") as f:
        json.dump(search_result, f, indent=2)
    
    # Export for analysis
    df = pd.DataFrame(search_result["results"])
    df.to_csv(f"{filename}.csv", index=False)
    
    # Summary report
    with open(f"{filename}_summary.txt", "w") as f:
        f.write(f"Search Query: {search_result['query']}\n")
        f.write(f"Results Found: {search_result['results_returned']}\n")
        f.write(f"Execution Time: {search_result['execution_time']:.2f}s\n")
        f.write(f"Cache Hit: {search_result['cache_hit']}\n\n")
        
        f.write("Top Results:\n")
        for i, result in enumerate(search_result["results"][:10], 1):
            f.write(f"{i}. {result['title']}\n")
            f.write(f"   {result['url']}\n")
            f.write(f"   Quality: {result['quality_score']}/2\n\n")

# Use the export function
results = agent.search("python data science libraries", max_results=30)
export_research_results(results, "python_datascience_research")
```

---

## 🔄 Automation and Scheduling

### Daily Research Automation
```python
import schedule
import time
from datetime import datetime
from agent_interface import AgentSearchInterface

class ResearchAutomation:
    def __init__(self, cache_dir="./auto_research_cache"):
        self.agent = AgentSearchInterface(cache_dir=cache_dir)
        
    def daily_tech_research(self):
        """Daily technology research routine"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        # Define daily research topics
        daily_queries = [
            {"query": "python new features 2024", "domain_filter": "official"},
            {"query": "machine learning breakthroughs", "domain_filter": "academic"},
            {"query": "web development trends", "domain_filter": "quality"},
            {"query": "cybersecurity updates", "domain_filter": "official"}
        ]
        
        # Execute batch research
        batch_result = self.agent.batch_search(daily_queries)
        
        # Save daily report
        report_path = f"./daily_reports/tech_research_{date_str}.json"
        os.makedirs("./daily_reports", exist_ok=True)
        
        with open(report_path, "w") as f:
            json.dump(batch_result, f, indent=2)
            
        print(f"Daily research completed: {batch_result['successful']} queries successful")
        return batch_result
    
    def weekly_deep_dive(self):
        """Weekly deep research on trending topics"""
        # More comprehensive research for weekly reports
        deep_queries = [
            {
                "query": "artificial intelligence developments",
                "domain_filter": "academic",
                "max_results": 50
            },
            {
                "query": "cloud computing innovations", 
                "domain_filter": "official",
                "max_results": 40
            }
        ]
        
        # Execute with validation
        results = []
        for query in deep_queries:
            result = self.agent.search_and_validate(
                query["query"],
                domain_filter=query["domain_filter"], 
                max_results=query["max_results"]
            )
            results.append(result)
            
        return results

# Setup automation
automation = ResearchAutomation()

# Schedule daily research
schedule.every().day.at("09:00").do(automation.daily_tech_research)
schedule.every().monday.at("10:00").do(automation.weekly_deep_dive)

# Keep the scheduler running
while True:
    schedule.run_pending()
    time.sleep(60)
```

### Monitoring and Alerts
```python
class ResearchMonitor:
    def __init__(self, agent):
        self.agent = agent
        self.performance_threshold = 2.0  # seconds
        
    def monitor_search_performance(self, query, expected_results=5):
        """Monitor search performance and alert on issues"""
        
        result = self.agent.search(query, max_results=expected_results)
        
        # Performance checks
        if result["execution_time"] > self.performance_threshold:
            print(f"⚠️ Slow search detected: {result['execution_time']:.2f}s")
            
        if result["results_returned"] < expected_results * 0.5:
            print(f"⚠️ Low result count: {result['results_returned']} (expected ~{expected_results})")
            
        if not result["cache_hit"] and result["execution_time"] < 0.1:
            print("✅ Fast API response - good performance")
            
        return result
        
    def health_check(self):
        """Comprehensive system health check"""
        test_queries = [
            "python tutorial",
            "javascript framework", 
            "machine learning"
        ]
        
        results = []
        for query in test_queries:
            try:
                result = self.monitor_search_performance(query)
                results.append({"query": query, "status": "success", "time": result["execution_time"]})
            except Exception as e:
                results.append({"query": query, "status": "error", "error": str(e)})
                
        avg_time = sum(r.get("time", 0) for r in results if r["status"] == "success") / len(results)
        success_rate = len([r for r in results if r["status"] == "success"]) / len(results)
        
        print(f"Health Check Results:")
        print(f"• Success Rate: {success_rate:.1%}")
        print(f"• Average Response Time: {avg_time:.2f}s")
        
        return results

# Usage
agent = AgentSearchInterface()
monitor = ResearchMonitor(agent)
health_results = monitor.health_check()
```

---

## 🎯 Advanced Use Cases

### Content Quality Analysis
```python
def analyze_content_quality(search_results):
    """Analyze the quality of search results"""
    
    quality_metrics = {
        "high_quality": [],
        "medium_quality": [],
        "low_quality": []
    }
    
    for result in search_results["results"]:
        score = result["quality_score"]
        
        if score >= 2:
            quality_metrics["high_quality"].append(result)
        elif score >= 1:
            quality_metrics["medium_quality"].append(result)
        else:
            quality_metrics["low_quality"].append(result)
    
    return quality_metrics

# Usage
results = agent.search("python best practices", max_results=30)
quality_analysis = analyze_content_quality(results)

print(f"Quality Distribution:")
print(f"• High Quality: {len(quality_analysis['high_quality'])} results")
print(f"• Medium Quality: {len(quality_analysis['medium_quality'])} results") 
print(f"• Low Quality: {len(quality_analysis['low_quality'])} results")
```

### Research Report Generation
```python
def generate_research_report(topic, output_file="research_report.md"):
    """Generate comprehensive research report"""
    
    agent = AgentSearchInterface()
    
    # Multi-angle research
    searches = {
        "overview": agent.search(f"{topic} overview introduction", max_results=10),
        "tutorials": agent.search(f"{topic} tutorial examples", domain_filter="tutorials", max_results=15),
        "documentation": agent.search(f"{topic} documentation", domain_filter="docs", max_results=10),
        "github": agent.search(f"{topic} examples", domain_filter="github", max_results=20),
        "discussions": agent.search(f"{topic} problems solutions", domain_filter="stackoverflow", max_results=15)
    }
    
    # Generate markdown report
    with open(output_file, "w") as f:
        f.write(f"# {topic.title()} Research Report\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for category, results in searches.items():
            f.write(f"## {category.title()}\n\n")
            f.write(f"Found {results['results_returned']} results in {results['execution_time']:.2f}s\n\n")
            
            for result in results["results"][:5]:  # Top 5 per category
                f.write(f"### [{result['title']}]({result['url']})\n")
                f.write(f"**Domain**: {result['domain']} | **Quality**: {result['quality_score']}/2\n\n")
                f.write(f"{result['description']}\n\n")
        
        # Summary statistics
        total_results = sum(r['results_returned'] for r in searches.values())
        avg_quality = sum(
            sum(item['quality_score'] for item in r['results'])
            for r in searches.values()
        ) / total_results
        
        f.write(f"## Summary\n\n")
        f.write(f"- **Total Results**: {total_results}\n")
        f.write(f"- **Average Quality**: {avg_quality:.2f}/2\n")
        f.write(f"- **Categories Researched**: {len(searches)}\n")

# Generate report
generate_research_report("machine learning", "ml_research_report.md")
print("Research report generated: ml_research_report.md")
```

---

**Happy Researching!** 🎉

These examples showcase the full power of WebScraperPortable's search and scraping capabilities. Mix and match patterns based on your specific research needs!