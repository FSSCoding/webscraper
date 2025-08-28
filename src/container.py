"""
Dependency Injection Container for WebScraperPortable

Clean, centralized dependency management to replace circular import mess.
"""

from typing import Optional, Dict, Any


class ServiceContainer:
    """
    Simple dependency injection container for WebScraperPortable.

    Solves the circular import and fragile relative import issues by
    centralizing all component initialization and dependencies.
    """

    def __init__(self):
        self._services = {}
        self._initialized = False

    def initialize(self, config: Optional[Dict[str, Any]] = None):
        """Initialize all services with proper dependency order"""
        if self._initialized:
            return

        config = config or {}

        # Initialize core services in dependency order
        self._init_logger(config)
        self._init_dependencies(config)
        self._init_content_parser(config)
        self._init_semantic_analyzer(config)
        self._init_storage_manager(config)
        self._init_scraper_api(config)
        self._init_search_engine(config)
        self._init_agent_interface(config)

        self._initialized = True

    def get(self, service_name: str):
        """Get service instance"""
        if not self._initialized:
            self.initialize()
        return self._services.get(service_name)

    def _init_logger(self, config):
        """Initialize logging service"""
        from .utils import app_logger

        self._services["logger"] = app_logger

    def _init_dependencies(self, config):
        """Initialize dependency checker"""
        from .dependencies import FEATURES_AVAILABLE

        self._services["features"] = FEATURES_AVAILABLE

    def _init_content_parser(self, config):
        """Initialize content parser"""
        from .parser import ContentParser

        user_agent = config.get("user_agent")
        self._services["content_parser"] = ContentParser(user_agent=user_agent)

    def _init_semantic_analyzer(self, config):
        """Initialize semantic analyzer (optional)"""
        try:
            from .semantic import SemanticAnalyzer

            ollama_host = config.get("ollama_host")
            enable_semantic = config.get("enable_semantic", False)
            if enable_semantic and self._services["features"].get(
                "semantic_analysis", False
            ):
                self._services["semantic_analyzer"] = SemanticAnalyzer(host=ollama_host)
            else:
                self._services["semantic_analyzer"] = None
        except Exception:
            self._services["semantic_analyzer"] = None

    def _init_storage_manager(self, config):
        """Initialize storage manager"""
        from .storage import StorageManager

        output_folder = config.get("output_dir") or config.get("output_folder")
        session_name = config.get("session_name")
        self._services["storage_manager"] = StorageManager(
            output_folder=output_folder, session_name=session_name
        )

    def _init_scraper_api(self, config):
        """Initialize web scraper API"""
        try:
            from .scraper import WebScraperAPI
        except ImportError:
            from scraper import WebScraperAPI

        scraper_config = {
            "max_workers": config.get("max_workers", 5),
            "enable_semantic": bool(self._services["semantic_analyzer"]),
            "user_agent": config.get("user_agent"),
            "ollama_host": config.get("ollama_host"),
        }

        self._services["scraper_api"] = WebScraperAPI(**scraper_config)

    def _init_search_engine(self, config):
        """Initialize search engine"""
        try:
            from .search import SearchEngine

            self._services["search_engine"] = SearchEngine(
                brave_api_key=config.get("brave_api_key"),
                tavily_api_key=config.get("tavily_api_key"),
            )
            # Link scraper to search engine
            self._services["search_engine"].scraper_api = self._services["scraper_api"]
        except Exception as e:
            self._services["logger"].warning(f"Failed to initialize search engine: {e}")
            self._services["search_engine"] = None

    def _init_agent_interface(self, config):
        """Initialize agent interface"""
        try:
            from .agent_interface import AgentSearchInterface

            cache_dir = config.get("cache_dir", "./search_cache")
            self._services["agent_interface"] = AgentSearchInterface(
                brave_api_key=config.get("brave_api_key"),
                tavily_api_key=config.get("tavily_api_key"),
                cache_dir=cache_dir,
            )
        except Exception as e:
            self._services["logger"].warning(
                f"Failed to initialize agent interface: {e}"
            )
            self._services["agent_interface"] = None


# Global container instance
container = ServiceContainer()


def get_service(name: str):
    """Convenience function to get service"""
    return container.get(name)


def initialize_services(config: Optional[Dict[str, Any]] = None):
    """Initialize all services with configuration"""
    container.initialize(config)


# Service getters for common use
def get_logger():
    return get_service("logger")


def get_scraper_api():
    return get_service("scraper_api")


def get_search_engine():
    return get_service("search_engine")


def get_agent_interface():
    return get_service("agent_interface")
