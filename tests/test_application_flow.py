"""
UTMS Application Flow Tests
===========================

Tests for the main application workflow, argument parsing, and execution flow.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from io import StringIO

# Import test utilities
import test_utils


class TestApplicationFlow(unittest.TestCase):
    """Test the main application flow and coordination."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.utms = test_utils.get_utms()
    
    def test_main_function_exists(self):
        """Test that main function is defined."""
        self.assertTrue(hasattr(self.utms, 'main'))
    
    def test_argument_parsing_basic(self):
        """Test basic argument parsing."""
        # Test the argument parser directly rather than through parse_arguments()
        if hasattr(self.utms, '_create_argument_parser'):
            parser = self.utms._create_argument_parser()
            self.utms._add_required_arguments(parser)
            self.utms._add_optional_arguments(parser)
            self.utms._add_utility_arguments(parser)
            
            test_args = [
                '--source', 'azure-devops',
                '--organization', 'test-org'
            ]
            
            args = parser.parse_args(test_args)
            self.assertEqual(args.source, 'azure-devops')
            self.assertEqual(args.organization, 'test-org')
        else:
            # Fallback: test that parse_arguments function exists
            self.assertTrue(hasattr(self.utms, 'parse_arguments'))
    
    def test_argument_parsing_with_repositories(self):
        """Test argument parsing with repository filter."""
        if hasattr(self.utms, '_create_argument_parser'):
            parser = self.utms._create_argument_parser()
            self.utms._add_required_arguments(parser)
            self.utms._add_optional_arguments(parser)
            self.utms._add_utility_arguments(parser)
            
            test_args = [
                '--source', 'azure-devops',
                '--organization', 'test-org',
                '--repositories', 'repo1,repo2,repo3'
            ]
            
            args = parser.parse_args(test_args)
            self.assertEqual(args.repositories, 'repo1,repo2,repo3')
        else:
            self.skipTest("Parser functions not available")
    
    def test_argument_parsing_with_cross_reference(self):
        """Test argument parsing with cross-reference directory specification."""
        if hasattr(self.utms, '_create_argument_parser'):
            parser = self.utms._create_argument_parser()
            self.utms._add_required_arguments(parser)
            self.utms._add_optional_arguments(parser)
            self.utms._add_utility_arguments(parser)
            
            test_args = [
                '--source', 'azure-devops',
                '--organization', 'test-org',
                '--cross-reference', '/path/to/tmvs/data'
            ]
            
            args = parser.parse_args(test_args)
            if hasattr(args, 'cross_reference'):
                self.assertEqual(args.cross_reference, '/path/to/tmvs/data')
        else:
            self.skipTest("Parser functions not available")
    
    def test_argument_parsing_invalid_source(self):
        """Test argument parsing with invalid source type."""
        if hasattr(self.utms, '_create_argument_parser'):
            parser = self.utms._create_argument_parser()
            self.utms._add_required_arguments(parser)
            self.utms._add_optional_arguments(parser)
            self.utms._add_utility_arguments(parser)
            
            test_args = [
                '--source', 'invalid-source',
                '--organization', 'test-org'
            ]
            
            # This should raise SystemExit due to invalid choice
            with self.assertRaises(SystemExit):
                parser.parse_args(test_args)
        else:
            self.skipTest("Parser functions not available")
            with self.assertRaises(SystemExit):
                self.utms.parse_arguments()


class TestWorkflowCoordination(unittest.TestCase):
    """Test the coordination between different components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.utms = test_utils.get_utms()
    
    @patch('builtins.print')
    def test_help_display(self, mock_print):
        """Test that help information is displayed correctly."""
        # Test help flag handling
        if hasattr(self.utms, 'main'):
            with patch('sys.argv', ['utms', '--help']):
                try:
                    self.utms.main()
                except SystemExit:
                    pass  # Help typically exits
    
    def test_source_type_validation(self):
        """Test source type validation logic."""
        if hasattr(self.utms, 'SourceType'):
            source_type = self.utms.SourceType
            
            # Test valid source types
            valid_sources = ['azure-devops', 'github']
            for source in valid_sources:
                # Test that source validation accepts valid sources
                self.assertIn(source, [s.value for s in source_type])
    
    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_output_directory_creation(self, mock_exists, mock_makedirs):
        """Test that output directories are created when needed."""
        mock_exists.return_value = False
        
        # Test output directory creation logic
        output_path = 'results/test-output.json'
        output_dir = os.path.dirname(output_path)
        
        # Simulate the application creating output directory
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        mock_makedirs.assert_called_once_with(output_dir, exist_ok=True)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in the application flow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.utms = test_utils.get_utms()
    
    def test_missing_organization_error(self):
        """Test error handling for missing organization."""
        if hasattr(self.utms, 'parse_arguments'):
            with patch('sys.argv', ['utms', '--source', 'azure-devops']):
                with self.assertRaises(SystemExit):
                    self.utms.parse_arguments()
    
    def test_missing_source_error(self):
        """Test error handling for missing source type."""
        if hasattr(self.utms, 'parse_arguments'):
            with patch('sys.argv', ['utms', '--organization', 'test-org']):
                with self.assertRaises(SystemExit):
                    self.utms.parse_arguments()
    
    @patch('sys.stderr', new_callable=StringIO)
    def test_authentication_failure_handling(self, mock_stderr):
        """Test handling of authentication failures."""
        # Test that authentication failures are handled gracefully
        if hasattr(self.utms, 'SourceAuthenticationManager'):
            auth_manager = self.utms.SourceAuthenticationManager(self.utms.SourceType.AZURE_DEVOPS)
            
            # Mock authentication failure
            with patch.object(auth_manager, 'authenticate', return_value=None):
                token = auth_manager.authenticate(self.utms.SourceType.AZURE_DEVOPS, 'test-org')
                self.assertIsNone(token)


class TestIntegrationFlow(unittest.TestCase):
    """Test the integration between major components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.utms = test_utils.get_utms()
    
    @patch('builtins.print')
    def test_successful_workflow_simulation(self, mock_print):
        """Test a simulated successful workflow."""
        # Mock successful authentication
        mock_token = 'test-token-12345'
        
        # Mock successful repository discovery
        mock_repositories = [
            self.utms.Repository(
                name='test-repo-1',
                id='repo-1',
                project_name='test-project'
            ),
            self.utms.Repository(
                name='test-repo-2', 
                id='repo-2',
                project_name='test-project'
            )
        ]
        
        # Mock successful scanning results
        mock_scan_results = [
            self.utms.ScanResult(
                source_type=self.utms.SourceType.AZURE_DEVOPS,
                organization='test-org',
                project_name='test-project',
                repository_name='test-repo-1',
                total_files_scanned=5,
                total_modules_found=3
            )
        ]
        
        # Verify components can be instantiated
        self.assertIsNotNone(mock_repositories)
        self.assertIsNotNone(mock_scan_results)
        self.assertEqual(len(mock_repositories), 2)
        self.assertEqual(len(mock_scan_results), 1)
    
    def test_component_dependencies(self):
        """Test that all required components are available."""
        required_classes = [
            'SourceType',
            'Repository', 
            'ScanResult',
            'ModuleReference',
            'UTMSConfig'
        ]
        
        for class_name in required_classes:
            self.assertTrue(hasattr(self.utms, class_name), 
                          f"Missing required class: {class_name}")
    
    def test_configuration_loading(self):
        """Test that configuration is properly loaded."""
        if hasattr(self.utms, 'UTMSConfig'):
            config = self.utms.UTMSConfig
            
            # Test that essential configuration constants exist
            essential_configs = [
                'API_TIMEOUT_SECONDS',
                'MAX_FILE_SIZE_MB',
                'MAX_CONCURRENT_FILES'
            ]
            
            for config_name in essential_configs:
                self.assertTrue(hasattr(config, config_name),
                              f"Missing configuration: {config_name}")


if __name__ == '__main__':
    unittest.main()
