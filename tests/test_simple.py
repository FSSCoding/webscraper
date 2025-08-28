#!/usr/bin/env python3
"""
Simple integration tests to verify basic functionality.
"""

import pytest
import os
import sys
import tempfile
import json
from unittest.mock import Mock, patch

# Add src to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)


class TestBasicFunctionality:
    """Test basic system functionality"""

    def test_package_imports(self):
        """Test that all main modules can be imported"""
        import dependencies
        import utils
        import parser
        import storage
        import semantic
        import search
        import agent_interface
        import scraper
        import cli
        
        # Basic sanity checks
        assert hasattr(dependencies, 'FEATURES_AVAILABLE')
        assert hasattr(utils, 'app_logger')
        assert hasattr(parser, 'ContentParser')
        assert hasattr(storage, 'StorageManager')
        assert hasattr(semantic, 'SemanticAnalyzer')
        assert hasattr(search, 'SearchEngine')
        assert hasattr(agent_interface, 'AgentSearchInterface')
        assert hasattr(scraper, 'WebScraperAPI')
        assert hasattr(cli, 'main')

    def test_webscraper_api_creation(self):
        """Test WebScraperAPI can be created"""
        from scraper import WebScraperAPI
        
        api = WebScraperAPI(enable_semantic=False)
        assert api is not None
        assert hasattr(api, 'scrape')
        assert hasattr(api, 'content_parser')
        assert hasattr(api, 'storage_manager')

    def test_search_engine_creation(self):
        """Test SearchEngine can be created"""
        from search import SearchEngine
        
        # Mock the utils to avoid logging setup issues
        with patch('search.app_logger'), patch('search.is_valid_url', return_value=True):
            engine = SearchEngine(brave_api_key="test_key")
            assert engine is not None
            assert hasattr(engine, 'session')
            assert hasattr(engine, '_active_requests')

    def test_agent_interface_creation(self):
        """Test AgentSearchInterface can be created"""
        from agent_interface import AgentSearchInterface
        
        # Mock dependencies to avoid initialization issues
        with patch('agent_interface.SearchEngine'), \
             patch('agent_interface.WebScraperAPI'):
            
            agent = AgentSearchInterface()
            assert agent is not None
            assert hasattr(agent, 'domain_presets')
            assert hasattr(agent, 'search')
            assert hasattr(agent, 'batch_search')

    def test_content_parser_creation(self):
        """Test ContentParser can be created"""
        from parser import ContentParser
        
        parser = ContentParser()
        assert parser is not None
        assert hasattr(parser, 'get_content_and_title')

    def test_storage_manager_creation(self):
        """Test StorageManager can be created"""
        from storage import StorageManager
        
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager(temp_dir)
            assert storage is not None
            assert hasattr(storage, 'save_content')
            assert hasattr(storage, 'create_excel_output')

    def test_semantic_analyzer_creation(self):
        """Test SemanticAnalyzer can be created"""
        from semantic import SemanticAnalyzer
        
        analyzer = SemanticAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze_content')
        assert hasattr(analyzer, 'check_ollama_availability')

    def test_cli_main_function(self):
        """Test CLI main function exists"""
        from cli import main
        
        assert callable(main)

    def test_dependencies_features(self):
        """Test dependencies module functionality"""
        import dependencies
        
        assert isinstance(dependencies.FEATURES_AVAILABLE, dict)
        assert 'requests' in dependencies.FEATURES_AVAILABLE
        assert 'bs4' in dependencies.FEATURES_AVAILABLE
        assert hasattr(dependencies, 'print_feature_status')

    def test_utils_functions(self):
        """Test utility functions"""
        import utils
        
        assert hasattr(utils, 'setup_logger')
        assert hasattr(utils, 'safe_filename')
        assert hasattr(utils, 'normalize_url')
        assert hasattr(utils, 'is_valid_url')
        assert hasattr(utils, 'DEFAULT_OUTPUT_FOLDER')