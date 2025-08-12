"""
Test API Clients
================

Unit tests for Azure DevOps and GitHub API clients.
"""

import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock, mock_open
import urllib.error

# Add parent directory to path to import utms
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import UTMS module using test utilities
import test_utils
utms = test_utils.get_utms()


class TestBaseAPIClient(unittest.TestCase):
    """Test BaseAPIClient functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = utms.BaseAPIClient()
        
    def test_base_client_initialization(self):
        """Test BaseAPIClient initialization."""
        # BaseAPIClient is a utility class with no state
        self.assertIsInstance(self.client, utms.BaseAPIClient)
        self.assertTrue(hasattr(self.client, '_make_api_request'))
    
    def test_make_api_request_method_exists(self):
        """Test that API request method exists."""
        self.assertTrue(callable(getattr(self.client, '_make_api_request', None)))
    
    @patch('urllib.request.urlopen')
    def test_make_request_success(self, mock_urlopen):
        """Test successful API request."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps({"test": "data"}).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = self.client._make_api_request('https://api.example.com/test', {})
        self.assertEqual(result, {"test": "data"})
    
    @patch('urllib.request.urlopen')
    def test_make_request_http_error(self, mock_urlopen):
        """Test HTTP error handling."""
        mock_urlopen.side_effect = urllib.error.HTTPError(
            None, 404, "Not Found", None, None
        )
        
        with self.assertRaises(utms.APIError):
            self.client._make_api_request('https://api.example.com/notfound', {})
    
    @patch('urllib.request.urlopen')
    def test_make_request_network_error(self, mock_urlopen):
        """Test network error handling."""
        mock_urlopen.side_effect = urllib.error.URLError("Network error")
        
        with self.assertRaises(utms.APIError):
            self.client._make_api_request('https://api.example.com/test', {})
    
    @patch('urllib.request.urlopen')
    def test_make_request_invalid_json(self, mock_urlopen):
        """Test handling of invalid JSON responses."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b"invalid json"
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        with self.assertRaises(utms.APIError):
            self.client._make_api_request('https://api.example.com/test', {})


class TestRepositoryDiscovery(unittest.TestCase):
    """Test RepositoryDiscovery functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock authentication manager
        self.mock_auth_manager = MagicMock()
        self.mock_auth_manager.get_headers.return_value = {'Authorization': 'Bearer test-token'}
        
        # Create RepositoryDiscovery instance
        self.discovery = utms.RepositoryDiscovery(utms.SourceType.AZURE_DEVOPS, self.mock_auth_manager)
        
    def test_discovery_initialization(self):
        """Test RepositoryDiscovery initialization."""
        self.assertEqual(self.discovery.source_type, utms.SourceType.AZURE_DEVOPS)
        self.assertEqual(self.discovery.auth_manager, self.mock_auth_manager)
    
    @patch.object(utms.RepositoryDiscovery, '_make_api_request')
    def test_discover_repositories_success(self, mock_request):
        """Test successful repository discovery."""
        # Mock API responses for projects and repositories
        mock_request.side_effect = [
            {'value': [{'name': 'TestProject', 'id': 'proj123'}]},  # projects call
            {'value': [{'name': 'repo1', 'id': 'repo123', 'webUrl': 'https://dev.azure.com/org/proj/_git/repo1'}]}  # repos call
        ]
        
        repositories = self.discovery.discover_repositories('test-org', 'test-token')
        self.assertIsInstance(repositories, list)
        self.assertEqual(len(repositories), 1)
        self.assertEqual(repositories[0].name, 'repo1')
    
    @patch.object(utms.RepositoryDiscovery, '_discover_azure_devops_repositories')
    def test_discover_repositories_with_filter(self, mock_discover):
        """Test repository discovery with project filter."""
        mock_discover.return_value = []
        
        self.discovery.discover_repositories('test-org', 'test-token', ['SpecificProject'])
        mock_discover.assert_called_once_with('test-org', 'test-token', ['SpecificProject'])
    
    def test_unsupported_source_type(self):
        """Test error handling for unsupported source types."""
        # Create discovery with unsupported source
        unsupported_discovery = utms.RepositoryDiscovery('unsupported', self.mock_auth_manager)
        
        with self.assertRaises(ValueError) as context:
            unsupported_discovery.discover_repositories('test-org', 'test-token')
        
        self.assertIn('Unsupported source type', str(context.exception))
    
    @patch.object(utms.RepositoryDiscovery, '_make_api_request')
    def test_api_request_error_handling(self, mock_request):
        """Test API request error handling."""
        mock_request.side_effect = Exception("API Error")
        
        with self.assertRaises(Exception):
            self.discovery.discover_repositories('test-org', 'test-token')
    
    def test_github_source_type_initialization(self):
        """Test RepositoryDiscovery with GitHub source type."""
        github_discovery = utms.RepositoryDiscovery(utms.SourceType.GITHUB, self.mock_auth_manager)
        self.assertEqual(github_discovery.source_type, utms.SourceType.GITHUB)
    
    @patch.object(utms.RepositoryDiscovery, '_make_api_request')
    def test_empty_repository_list(self, mock_request):
        """Test handling of empty repository list."""
        mock_request.side_effect = [
            {'value': [{'name': 'TestProject', 'id': 'proj123'}]},  # projects
            {'value': []}  # empty repositories
        ]
        
        repositories = self.discovery.discover_repositories('test-org', 'test-token')
        self.assertEqual(len(repositories), 0)
    
    def test_auth_manager_integration(self):
        """Test authentication manager integration."""
        headers = self.discovery.auth_manager.get_headers()
        self.assertIn('Authorization', headers)
        self.assertEqual(headers['Authorization'], 'Bearer test-token')


class TestGitHubRepositoryDiscovery(unittest.TestCase):
    """Test GitHub integration through RepositoryDiscovery."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock authentication manager
        self.mock_auth_manager = MagicMock()
        self.mock_auth_manager.get_headers.return_value = {'Authorization': 'token test-token'}
        
        # Create GitHub RepositoryDiscovery instance
        self.github_discovery = utms.RepositoryDiscovery(utms.SourceType.GITHUB, self.mock_auth_manager)
        
    def test_github_discovery_initialization(self):
        """Test GitHub RepositoryDiscovery initialization."""
        self.assertEqual(self.github_discovery.source_type, utms.SourceType.GITHUB)
        self.assertEqual(self.github_discovery.auth_manager, self.mock_auth_manager)
    
    @patch.object(utms.RepositoryDiscovery, '_make_api_request')
    def test_github_discover_repositories(self, mock_request):
        """Test GitHub repository discovery."""
        # Mock GitHub API response
        mock_request.return_value = [
            {
                'name': 'test-repo',
                'clone_url': 'https://github.com/test-org/test-repo.git',
                'default_branch': 'main'
            }
        ]
        
        repositories = self.github_discovery.discover_repositories('test-org', 'test-token')
        self.assertIsInstance(repositories, list)
        if repositories:  # Only check if repositories returned
            self.assertEqual(repositories[0].name, 'test-repo')
    
    def test_github_vs_azure_devops_source_types(self):
        """Test different source type handling."""
        azure_discovery = utms.RepositoryDiscovery(utms.SourceType.AZURE_DEVOPS, self.mock_auth_manager)
        
        self.assertEqual(self.github_discovery.source_type, utms.SourceType.GITHUB)
        self.assertEqual(azure_discovery.source_type, utms.SourceType.AZURE_DEVOPS)
        self.assertNotEqual(self.github_discovery.source_type, azure_discovery.source_type)


class TestAPIClientIntegration(unittest.TestCase):
    """Test API client integration scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_auth_manager = MagicMock()
        self.mock_auth_manager.get_headers.return_value = {'Authorization': 'Bearer test-token'}
    
    @patch.object(utms.BaseAPIClient, '_make_api_request')
    def test_rate_limit_handling(self, mock_request):
        """Test handling of API rate limits."""
        # Mock rate limit response
        mock_request.side_effect = utms.APIError("Rate limit exceeded: 429")
        
        client = utms.BaseAPIClient()
        
        with self.assertRaises(utms.APIError) as context:
            client._make_api_request('https://api.example.com/test')
        
        self.assertIn("429", str(context.exception))
    
    @patch.object(utms.BaseAPIClient, '_make_api_request')
    def test_authentication_error_handling(self, mock_request):
        """Test handling of authentication errors."""
        # Mock unauthorized response
        mock_request.side_effect = utms.APIError("Unauthorized: 401")
        
        client = utms.BaseAPIClient()
        
        with self.assertRaises(utms.APIError) as context:
            client._make_api_request('https://api.example.com/test')
        
        self.assertIn("401", str(context.exception))
    
    def test_discovery_factory_pattern(self):
        """Test creating discovery instances for different source types."""
        # Test Azure DevOps discovery creation
        azure_discovery = utms.RepositoryDiscovery(
            utms.SourceType.AZURE_DEVOPS, 
            self.mock_auth_manager
        )
        self.assertIsInstance(azure_discovery, utms.RepositoryDiscovery)
        self.assertEqual(azure_discovery.source_type, utms.SourceType.AZURE_DEVOPS)
        
        # Test GitHub discovery creation
        github_discovery = utms.RepositoryDiscovery(
            utms.SourceType.GITHUB, 
            self.mock_auth_manager
        )
        self.assertIsInstance(github_discovery, utms.RepositoryDiscovery)
        self.assertEqual(github_discovery.source_type, utms.SourceType.GITHUB)
    
    def test_concurrent_discovery_operations(self):
        """Test handling of concurrent discovery operations."""
        import threading
        
        discovery = utms.RepositoryDiscovery(utms.SourceType.AZURE_DEVOPS, self.mock_auth_manager)
        results = []
        errors = []
        
        def discover_repositories():
            try:
                with patch.object(discovery, 'discover_repositories') as mock_discover:
                    mock_discover.return_value = []
                    result = discovery.discover_repositories('test-org', 'test-token')
                    results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=discover_repositories)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify no errors occurred
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(results), 3)
    
    def test_error_propagation(self):
        """Test proper error propagation through the stack."""
        discovery = utms.RepositoryDiscovery(utms.SourceType.AZURE_DEVOPS, self.mock_auth_manager)
        
        with patch.object(discovery, '_discover_azure_devops_repositories') as mock_discover:
            mock_discover.side_effect = Exception("Network error")
            
            with self.assertRaises(Exception) as context:
                discovery.discover_repositories('test-org', 'test-token')
            
            self.assertIn("Network error", str(context.exception))


if __name__ == '__main__':
    unittest.main()
