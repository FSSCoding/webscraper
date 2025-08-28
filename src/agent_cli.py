#!/usr/bin/env python3
"""
Agent CLI for WebScraperPortable

Simplified command-line interface designed specifically for autonomous agents.
Clean JSON input/output, batch operations, domain targeting.
"""

import sys
import json
import argparse
from typing import Dict, Any

from .agent_interface import AgentSearchInterface


def create_agent_parser() -> argparse.ArgumentParser:
    """Create agent-optimized argument parser"""
    parser = argparse.ArgumentParser(
        description=(
            "WebScraperPortable Agent Interface - JSON-focused search and scraping"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Agent-Optimized Examples:

  # Simple search with JSON output
  python -m WebScraperPortable.agent_cli --search "python asyncio tutorial"

  # Domain-filtered search
  python -m WebScraperPortable.agent_cli --search "react hooks" --domain github

  # Batch search from file
  python -m WebScraperPortable.agent_cli --batch queries.json

  # Quick URL validation
  python -m WebScraperPortable.agent_cli --validate-urls \
      "https://docs.python.org,https://github.com"

  # Search with validation
  python -m WebScraperPortable.agent_cli --search "machine learning" \
      --validate --domain academic

Available Domain Filters: github, docs, tutorials, stackoverflow, \
    academic, official, quality
        """,
    )

    # Operation modes (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--search", help="Search query")
    mode_group.add_argument("--batch", help="JSON file with batch queries")
    mode_group.add_argument("--validate-urls", help="Comma-separated URLs to validate")
    mode_group.add_argument(
        "--presets", action="store_true", help="Show available domain presets"
    )

    # Search options
    parser.add_argument(
        "--max-results", type=int, default=10, help="Maximum results (default: 10)"
    )
    parser.add_argument(
        "--domain", help="Domain filter preset (github, docs, tutorials, etc.)"
    )
    parser.add_argument(
        "--quality-threshold",
        type=float,
        default=0.0,
        help="Minimum quality score 0.0-1.0 (default: 0.0)",
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validate top results before returning"
    )
    parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="Exclude metadata from results (faster)",
    )
    parser.add_argument(
        "--no-cache", action="store_true", help="Disable result caching"
    )

    # API keys
    parser.add_argument("--brave-key", help="Brave Search API key")
    parser.add_argument("--tavily-key", help="Tavily Search API key")

    # Output options
    parser.add_argument("--output", help="Save results to file (JSON format)")
    parser.add_argument(
        "--pretty", action="store_true", help="Pretty-print JSON output"
    )

    return parser


def handle_search(interface: AgentSearchInterface, args) -> Dict[str, Any]:
    """Handle search operation"""
    if args.validate:
        return interface.search_and_validate(
            query=args.search, max_results=args.max_results, domain_filter=args.domain
        )
    else:
        return interface.search(
            query=args.search,
            max_results=args.max_results,
            domain_filter=args.domain,
            include_metadata=not args.no_metadata,
            quality_threshold=args.quality_threshold,
        )


def handle_batch(interface: AgentSearchInterface, args) -> Dict[str, Any]:
    """Handle batch search operation"""
    try:
        with open(args.batch, "r") as f:
            queries = json.load(f)

        if not isinstance(queries, list):
            return {
                "status": "error",
                "error": "Batch file must contain a JSON array of query objects",
            }

        return interface.batch_search(queries)

    except FileNotFoundError:
        return {"status": "error", "error": f"Batch file not found: {args.batch}"}
    except json.JSONDecodeError as e:
        return {"status": "error", "error": f"Invalid JSON in batch file: {str(e)}"}
    except Exception as e:
        return {"status": "error", "error": f"Batch processing error: {str(e)}"}


def handle_validate_urls(interface: AgentSearchInterface, args) -> Dict[str, Any]:
    """Handle URL validation operation"""
    try:
        urls = [url.strip() for url in args.validate_urls.split(",")]
        return interface.quick_metadata(urls)
    except Exception as e:
        return {"status": "error", "error": f"URL validation error: {str(e)}"}


def handle_presets(interface: AgentSearchInterface, args) -> Dict[str, Any]:
    """Handle presets display"""
    presets = interface.get_available_presets()
    return {
        "status": "success",
        "available_presets": presets,
        "usage": "Use --domain PRESET_NAME to filter results to specific domain types",
    }


def main():
    """Main agent CLI entry point"""
    parser = create_agent_parser()
    args = parser.parse_args()

    try:
        # Initialize agent interface
        cache_dir = None if args.no_cache else "./search_cache"
        interface = AgentSearchInterface(
            brave_api_key=args.brave_key,
            tavily_api_key=args.tavily_key,
            cache_dir=cache_dir,
        )

        # Check availability
        if not args.presets and not interface.is_available():
            result = {
                "status": "error",
                "error": (
                    "No search engines available. Set BRAVE_SEARCH_API_KEY or "
                    "TAVILY_API_KEY environment variable."
                ),
            }
        else:
            # Route to appropriate handler
            if args.search:
                result = handle_search(interface, args)
            elif args.batch:
                result = handle_batch(interface, args)
            elif args.validate_urls:
                result = handle_validate_urls(interface, args)
            elif args.presets:
                result = handle_presets(interface, args)
            else:
                result = {"status": "error", "error": "No operation specified"}

        # Output result
        if args.output:
            with open(args.output, "w") as f:
                json.dump(result, f, indent=2 if args.pretty else None)
            print(f"Results saved to {args.output}")
        else:
            print(json.dumps(result, indent=2 if args.pretty else None))

        # Exit with appropriate code
        return 0 if result.get("status") == "success" else 1

    except KeyboardInterrupt:
        print(
            json.dumps(
                {"status": "cancelled", "message": "Operation cancelled by user"}
            )
        )
        return 130
    except Exception as e:
        print(json.dumps({"status": "error", "error": f"Unexpected error: {str(e)}"}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
