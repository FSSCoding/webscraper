#!/usr/bin/env python3
"""
Test package functionality through proper imports.
"""

import pytest
import os
import sys
import tempfile
from unittest.mock import Mock, patch

# Import as a package
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import the package
import src as WebScraperPortable


class TestPackageImports:
    """Test package imports work correctly"""

    def test_package_structure(self):
        """Test package structure is correct"""
        assert hasattr(WebScraperPortable, 'dependencies')
        assert hasattr(WebScraperPortable, 'utils')
        assert hasattr(WebScraperPortable, 'parser')
        assert hasattr(WebScraperPortable, 'storage')
        assert hasattr(WebScraperPortable, 'semantic')
        assert hasattr(WebScraperPortable, 'search')
        assert hasattr(WebScraperPortable, 'agent_interface')
        assert hasattr(WebScraperPortable, 'scraper')
        assert hasattr(WebScraperPortable, 'cli')

    def test_webscraper_api_available(self):
        """Test WebScraperAPI is available through package"""
        assert hasattr(WebScraperPortable, 'WebScraperAPI')
        assert WebScraperPortable.WebScraperAPI is not None
        
        # Test can create instance
        api = WebScraperPortable.WebScraperAPI(enable_semantic=False)
        assert api is not None

    def test_cli_main_available(self):
        """Test CLI main is available through package"""
        assert hasattr(WebScraperPortable, 'cli_main')
        assert WebScraperPortable.cli_main is not None
        assert callable(WebScraperPortable.cli_main)

    def test_convenience_functions(self):
        """Test convenience functions are available"""
        assert hasattr(WebScraperPortable, 'scrape_url')
        assert hasattr(WebScraperPortable, 'scrape_multiple')
        assert callable(WebScraperPortable.scrape_url)
        assert callable(WebScraperPortable.scrape_multiple)

    def test_module_attributes(self):
        """Test module-level attributes"""
        assert hasattr(WebScraperPortable, '__version__')
        assert hasattr(WebScraperPortable, '__author__')
        assert hasattr(WebScraperPortable, '__description__')
        
        assert WebScraperPortable.__version__ == "2.0.0"

    def test_dependencies_module(self):
        """Test dependencies module works"""
        deps = WebScraperPortable.dependencies
        assert hasattr(deps, 'FEATURES_AVAILABLE')
        assert isinstance(deps.FEATURES_AVAILABLE, dict)
        assert 'core' in deps.FEATURES_AVAILABLE

    def test_search_engine_through_package(self):
        """Test SearchEngine can be accessed through package"""
        search_module = WebScraperPortable.search
        assert hasattr(search_module, 'SearchEngine')
        
        # Test can create instance (may need mocking)
        with patch.object(search_module, 'app_logger'), \
             patch.object(search_module, 'is_valid_url', return_value=True):
            engine = search_module.SearchEngine(brave_api_key="test")
            assert engine is not None

    def test_agent_interface_through_package(self):
        """Test AgentSearchInterface through package"""
        agent_module = WebScraperPortable.agent_interface
        assert hasattr(agent_module, 'AgentSearchInterface')
        
        # Test can create instance with mocking
        with patch.object(agent_module, 'SearchEngine'), \
             patch.object(agent_module, 'WebScraperAPI'):
            agent = agent_module.AgentSearchInterface()
            assert agent is not None


class TestFunctionalComponents:
    """Test individual components work"""

    def test_content_parser(self):
        """Test ContentParser functionality"""
        parser_module = WebScraperPortable.parser
        parser = parser_module.ContentParser()
        assert parser is not None
        assert hasattr(parser, 'get_content_and_title')

    def test_storage_manager(self):
        """Test StorageManager functionality"""
        storage_module = WebScraperPortable.storage
        
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = storage_module.StorageManager(temp_dir)
            assert storage is not None
            assert hasattr(storage, 'save_content')

    def test_semantic_analyzer(self):
        """Test SemanticAnalyzer functionality"""
        semantic_module = WebScraperPortable.semantic
        analyzer = semantic_module.SemanticAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze_content')


class TestRealFunctionality:
    """Test actual functionality with real use cases"""

    def test_basic_scraping_api(self):
        """Test basic scraping functionality"""
        api = WebScraperPortable.WebScraperAPI(
            enable_semantic=False,
            max_workers=2
        )
        
        assert api.max_workers == 2
        assert api.enable_semantic is False
        assert hasattr(api, 'scrape')

    def test_search_engine_initialization(self):
        """Test SearchEngine initializes properly"""
        search_module = WebScraperPortable.search
        
        with patch.object(search_module, 'app_logger'), \
             patch.object(search_module, 'is_valid_url', return_value=True):
            
            engine = search_module.SearchEngine(
                brave_api_key="test_key",
                tavily_api_key="test_tavily"
            )
            
            assert engine.brave_api_key == "test_key"
            assert engine.tavily_api_key == "test_tavily"
            assert hasattr(engine, 'session')
            assert hasattr(engine, '_active_requests')

    def test_agent_interface_configuration(self):
        """Test AgentSearchInterface configuration"""
        agent_module = WebScraperPortable.agent_interface
        
        with patch.object(agent_module, 'SearchEngine'), \
             patch.object(agent_module, 'WebScraperAPI'):
            
            with tempfile.TemporaryDirectory() as temp_dir:
                agent = agent_module.AgentSearchInterface(
                    cache_dir=temp_dir,
                    cache_ttl_minutes=120
                )
                
                assert agent.cache_dir == temp_dir
                assert agent.cache_ttl.total_seconds() == 120 * 60
                assert hasattr(agent, 'domain_presets')
                assert 'github' in agent.domain_presets