"""
Command-line interface for WebScraperPortable

Provides a CLI for web scraping with optional search capabilities.
"""

import sys
import argparse
import json

# Clean dependency injection - no more import mess!
try:
    from .container import initialize_services, get_service
    from .dependencies import print_feature_status
    from .search_stats import SearchStats
except (ImportError, ModuleNotFoundError):
    from .container import initialize_services, get_service
    from .dependencies import print_feature_status
    from .search_stats import SearchStats


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser"""
    parser = argparse.ArgumentParser(
        description="WebScraperPortable: Advanced web scraping with search integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape specific URLs
  python -m WebScraperPortable --url https://example.com --output ./results

  # Search and scrape automatically
  python -m WebScraperPortable --search "python web scraping tutorial" \\
      --output ./results

  # Search only (no content extraction)
  python -m WebScraperPortable --search "react hooks" --search-only \\
      --json-output

  # Search with topic filtering
  python -m WebScraperPortable --search "machine learning" \\
      --topic "neural networks" --depth 2
        """,
    )

    # Input source options (mutually exclusive)
    source_group = parser.add_mutually_exclusive_group(required=False)
    source_group.add_argument("--url", help="URL to scrape")
    source_group.add_argument("--folder", help="Folder containing files to process")
    source_group.add_argument("--search", help="Search query to find and scrape URLs")

    # Search-specific options
    parser.add_argument(
        "--search-results",
        type=int,
        default=10,
        help="Number of search results to process (default: 10)",
    )
    parser.add_argument(
        "--search-only",
        action="store_true",
        help="Search for URLs without content extraction",
    )

    # Output options
    parser.add_argument("--output", help="Output directory (default: ./results)")
    parser.add_argument(
        "--json-output", action="store_true", help="Output results as JSON to stdout"
    )

    # Crawling options
    parser.add_argument(
        "--depth",
        type=int,
        default=1,
        help="Crawling depth (-1 for unlimited, default: 1)",
    )
    parser.add_argument("--topic", help="Topic for semantic filtering")
    parser.add_argument(
        "--topic-threshold",
        type=float,
        default=0.5,
        help="Topic relevance threshold (0.0-1.0, default: 0.5)",
    )
    parser.add_argument(
        "--link-threshold",
        type=float,
        default=0.6,
        help="Link relevance threshold (0.0-1.0, default: 0.6)",
    )

    # Technical options
    parser.add_argument(
        "--max-workers",
        type=int,
        default=5,
        help="Number of worker threads (default: 5)",
    )
    parser.add_argument("--user-agent", help="Custom user agent string")
    parser.add_argument(
        "--ollama-host", help="Ollama server host for semantic analysis"
    )
    parser.add_argument(
        "--brave-api-key",
        help="Brave Search API key (can also use BRAVE_SEARCH_API_KEY env var)",
    )
    parser.add_argument(
        "--tavily-api-key",
        help="Tavily Search API key (can also use TAVILY_API_KEY env var)",
    )

    # Utility options
    parser.add_argument(
        "--features", action="store_true", help="Show available features and exit"
    )
    parser.add_argument(
        "--stats", action="store_true", help="Show search statistics and exit"
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress progress output")
    parser.add_argument(
        "--progress-json",
        action="store_true",
        help="Output progress as JSON lines to stderr (works with --json-output)",
    )

    return parser


def handle_search_operation(args, config: dict) -> dict:
    """Handle search-based operations using dependency injection"""
    # Initialize services with CLI config
    initialize_services(config)

    # Get services from container
    logger = get_service("logger")
    search_engine = get_service("search_engine")

    if not search_engine:
        return {
            "operation": "search_error",
            "error_message": "Search functionality not available. Please set API keys.",
            "status": "error",
        }

    if args.search_only:
        # Search only, return URLs without content extraction
        logger.info(f"Searching for: '{args.search}' (search only)")
        search_results = search_engine.search_only(args.search, args.search_results)

        return {
            "operation": "search_only",
            "query": args.search,
            "results_count": len(search_results),
            "results": search_results,
        }
    else:
        # Search and scrape
        logger.info(f"Searching and scraping: '{args.search}'")

        # Get scraper from container (already configured)
        scraper = get_service("scraper_api")

        # Connect search engine to scraper
        search_engine.scraper_api = scraper

        # Prepare scraper options
        scraper_options = {
            "output_dir": args.output,
            "depth": args.depth,
            "topic": args.topic,
            "topic_threshold": args.topic_threshold,
            "link_threshold": args.link_threshold,
            "show_progress": not args.quiet,
        }

        # Perform search and scrape
        result = search_engine.search_and_scrape(
            query=args.search,
            max_results=args.search_results,
            scraper_options=scraper_options,
        )

        return {"operation": "search_and_scrape", **result}


def handle_direct_scrape(args, config: dict) -> dict:
    """Handle direct URL/folder scraping using dependency injection"""
    # Initialize services with CLI config
    initialize_services(config)

    # Get scraper from container (already configured)
    scraper = get_service("scraper_api")

    # Determine source
    source = args.url or args.folder

    # Perform scraping
    result = scraper.scrape(
        sources=source,
        output_dir=args.output,
        depth=args.depth,
        topic=args.topic,
        topic_threshold=args.topic_threshold,
        link_threshold=args.link_threshold,
        show_progress=not args.quiet,
    )

    return {"operation": "direct_scrape", "source": source, **result}


def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()

    # Handle feature status request
    if args.features:
        print_feature_status()
        return 0

    # Handle search statistics request
    if args.stats:
        stats = SearchStats()
        stats_data = stats.get_stats()

        print("\n📊 Search Statistics:")
        print(f"  Total searches: {stats_data.get('total_searches', 0)}")
        if stats_data.get("first_search"):
            print(f"  First search: {stats_data['first_search']}")
        if stats_data.get("last_search"):
            print(f"  Last search: {stats_data['last_search']}")

        # Show recent daily counts
        searches_by_date = stats_data.get("searches_by_date", {})
        if searches_by_date:
            print("\n  Recent daily activity:")
            sorted_dates = sorted(searches_by_date.keys())[-7:]  # Last 7 days
            for date in sorted_dates:
                count = searches_by_date[date]
                print(f"    {date}: {count} searches")

        return 0

    # Validate that a source is provided for non-utility operations
    if not any([args.url, args.folder, args.search]):
        parser.error("One of --url, --folder, or --search is required")

    try:
        # Build clean configuration from CLI arguments
        config = {
            "max_workers": args.max_workers,
            "enable_semantic": bool(args.topic),
            "user_agent": args.user_agent,
            "ollama_host": args.ollama_host,
            "brave_api_key": args.brave_api_key,
            "tavily_api_key": args.tavily_api_key,
            "cache_dir": "./search_cache",
        }

        if args.search:
            # Handle search operation with clean dependency injection
            result = handle_search_operation(args, config)
        else:
            # Handle direct scraping with clean dependency injection
            result = handle_direct_scrape(args, config)

        # Output results
        if args.json_output:
            # Add progress tracking metadata to JSON output
            # Determine success based on operation type
            operation_successful = False
            if (
                result.get("operation") == "search_only"
                and result.get("results_count", 0) >= 0
            ):
                operation_successful = True
            elif result.get("operation") == "search_and_scrape":
                scraper_result = result.get("scraper_result", {})
                operation_successful = scraper_result.get("status") == "success"
            elif result.get("status") == "success":
                operation_successful = True

            if operation_successful:
                result["progress"] = {
                    "completed": True,
                    "message": "Operation completed successfully",
                    "timestamp": result.get("timestamp", ""),
                    "duration": result.get(
                        "duration_seconds", result.get("execution_time", 0)
                    ),
                }
                # Add operation-specific progress info
                if result.get("operation") == "search_only":
                    result["progress"][
                        "details"
                    ] = f"Found {result['results_count']} results"
                elif result.get("operation") == "search_and_scrape":
                    scraper_result = result.get("scraper_result", {})
                    result["progress"]["details"] = (
                        f"Found {len(result.get('search_results', []))} results, "
                        f"scraped {scraper_result.get('targets_processed', 0)} pages"
                    )
                elif "targets_processed" in result:
                    result["progress"][
                        "details"
                    ] = f"Processed {result['targets_processed']} sources"
            else:
                result["progress"] = {
                    "completed": False,
                    "message": result.get("error_message", "Operation failed"),
                    "timestamp": result.get("timestamp", ""),
                    "error": True,
                }

            print(json.dumps(result, indent=2, default=str))
        else:
            # Handle different result types
            if result.get("operation") == "search_only":
                try:
                    logger = get_service("logger")
                    logger.info("✅ Search completed successfully!")
                    logger.info(
                        f"🔍 Found {result['results_count']} results for: "
                        f"'{result['query']}'"
                    )
                    for i, search_result in enumerate(result["results"], 1):
                        logger.info(
                            f"  {i}. {search_result['title']} - {search_result['url']}"
                        )
                except Exception:
                    print("✅ Search completed successfully!")
            elif result.get("operation") == "search_and_scrape":
                # Check scraper result status
                scraper_result = result.get("scraper_result", {})
                if scraper_result.get("status") == "success":
                    logger = get_service("logger")
                    logger.info("✅ Search and scrape completed successfully!")
                    logger.info(
                        f"🔍 Found {len(result.get('search_results', []))} results "
                        "for: "
                        f"'{result.get('search_query', args.search)}'"
                    )
                    logger.info(
                        f"📊 Scraped {scraper_result['targets_processed']} total pages"
                    )
                    if "output_directory" in scraper_result:
                        logger.info(
                            f"📁 Results saved to: {scraper_result['output_directory']}"
                        )
                else:
                    logger = get_service("logger")
                    logger.error(
                        f"❌ Scraping failed: "
                        f"{scraper_result.get('error_message', 'Unknown error')}"
                    )
                    return 1
            elif result.get("status") == "success":
                logger = get_service("logger")
                logger.info("✅ Operation completed successfully!")
                if "output_directory" in result:
                    logger.info(f"📁 Results saved to: {result['output_directory']}")
            else:
                logger = get_service("logger")
                logger.error(
                    f"❌ Operation failed: "
                    f"{result.get('error_message', 'Unknown error')}"
                )
                return 1

        return 0

    except KeyboardInterrupt:
        try:
            logger = get_service("logger")
            logger.info("🛑 Operation cancelled by user")
        except Exception:
            print("🛑 Operation cancelled by user")
        return 130
    except Exception as e:
        try:
            logger = get_service("logger")
            logger.error(f"❌ Unexpected error: {e}")
        except Exception:
            print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
