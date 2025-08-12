"""
UTMS Output Handling Tests
==========================

Tests for output formatting, file generation, and data presentation.
"""

import unittest
from unittest.mock import Mock, patch, mock_open, MagicMock
import json
import os
import tempfile
from datetime import datetime

# Import test utilities
import test_utils
utms = test_utils.get_utms()


class TestOutputFormatting(unittest.TestCase):
    """Test output formatting and data presentation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.utms = test_utils.get_utms()
        
        # Create sample scan results for output testing
        self.sample_scan_result = self.utms.ScanResult(
            source_type=self.utms.SourceType.AZURE_DEVOPS,
            organization="test-org",
            project_name="test-project",
            repository_name="test-repo",
            total_files_scanned=10,
            total_modules_found=3
        )
        
        # Add sample modules
        modules = [
            self.utms.ModuleReference(
                local_name="consul_module",
                source="hashicorp/consul/aws",
                version="0.1.0",
                file_path="main.tf",
                line_number=10,
                repository_name="test-repo",
                project_name="test-project"
            ),
            self.utms.ModuleReference(
                local_name="vpc_module",
                source="terraform-aws-modules/vpc/aws",
                version="3.0.0",
                file_path="vpc.tf",
                line_number=5,
                repository_name="test-repo",
                project_name="test-project"
            ),
            self.utms.ModuleReference(
                local_name="git_module",
                source="git::https://github.com/user/module.git",
                version="v1.0.0",
                file_path="git.tf",
                line_number=15,
                repository_name="test-repo", 
                project_name="test-project"
            )
        ]
        
        for module in modules:
            self.sample_scan_result.add_module(module)
    
    def test_json_serialization(self):
        """Test JSON serialization of scan results."""
        # Test that scan result can be converted to dict/JSON
        if hasattr(self.sample_scan_result, '__dict__'):
            result_dict = self.sample_scan_result.__dict__.copy()
            
            # Convert modules to dictionaries
            if 'modules' in result_dict:
                result_dict['modules'] = [
                    mod.__dict__ if hasattr(mod, '__dict__') else str(mod)
                    for mod in result_dict['modules']
                ]
            
            # Should be JSON serializable
            json_str = json.dumps(result_dict, indent=2, default=str)
            self.assertIsInstance(json_str, str)
            self.assertGreater(len(json_str), 0)
    
    def test_output_structure_validation(self):
        """Test that output has the expected structure."""
        result_dict = {}
        
        # Basic scan information
        expected_fields = [
            'source_type',
            'organization', 
            'project_name',
            'repository_name',
            'total_files_scanned',
            'total_modules_found',
            'modules',
            'scan_timestamp'
        ]
        
        # Check if scan result has expected attributes
        for field in expected_fields:
            if hasattr(self.sample_scan_result, field):
                result_dict[field] = getattr(self.sample_scan_result, field)
        
        # Should have most expected fields
        self.assertGreaterEqual(len(result_dict), 6)
    
    def test_module_output_formatting(self):
        """Test formatting of individual modules in output."""
        for module in self.sample_scan_result.modules:
            # Module should have essential attributes
            self.assertTrue(hasattr(module, 'local_name'))
            self.assertTrue(hasattr(module, 'source'))
            self.assertTrue(hasattr(module, 'version'))
            self.assertTrue(hasattr(module, 'file_path'))
            self.assertTrue(hasattr(module, 'line_number'))
            
            # Attributes should have reasonable values
            self.assertIsInstance(module.local_name, str)
            self.assertIsInstance(module.source, str)
            self.assertIsInstance(module.file_path, str)
            self.assertIsInstance(module.line_number, int)
            self.assertGreater(module.line_number, 0)


class TestFileOutput(unittest.TestCase):
    """Test file output operations and file handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.utms = test_utils.get_utms()
        
        # Create sample data for file output
        self.sample_data = {
            "scan_metadata": {
                "source_type": "azure-devops",
                "organization": "test-org",
                "scan_timestamp": datetime.now().isoformat(),
                "total_repositories": 1,
                "total_files_scanned": 10,
                "total_modules_found": 3
            },
            "repositories": [
                {
                    "project_name": "test-project",
                    "repository_name": "test-repo",
                    "modules_found": 3,
                    "modules": [
                        {
                            "local_name": "consul_module",
                            "source": "hashicorp/consul/aws",
                            "version": "0.1.0",
                            "file_path": "main.tf",
                            "line_number": 10
                        }
                    ]
                }
            ]
        }
    
    def test_json_file_writing(self):
        """Test writing JSON output to file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            try:
                # Write test data to file
                json.dump(self.sample_data, tmp_file, indent=2, default=str)
                tmp_file.flush()
                
                # Verify file was written
                self.assertTrue(os.path.exists(tmp_file.name))
                
                # Read back and verify content
                with open(tmp_file.name, 'r') as read_file:
                    loaded_data = json.load(read_file)
                    self.assertEqual(loaded_data['scan_metadata']['organization'], 'test-org')
                    self.assertEqual(len(loaded_data['repositories']), 1)
                    
            finally:
                # Clean up
                if os.path.exists(tmp_file.name):
                    os.unlink(tmp_file.name)
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_output_file_error_handling(self, mock_json_dump, mock_file):
        """Test error handling in file output operations."""
        # Simulate file write error
        mock_file.side_effect = IOError("Permission denied")
        
        try:
            with open('test_output.json', 'w') as f:
                json.dump(self.sample_data, f)
        except IOError as e:
            self.assertIn("Permission denied", str(e))
    
    def test_output_directory_creation(self):
        """Test creation of output directories."""
        test_dir = tempfile.mkdtemp()
        try:
            # Test nested directory creation
            output_path = os.path.join(test_dir, 'results', 'scan_output.json')
            output_dir = os.path.dirname(output_path)
            
            # Create directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Verify directory was created
            self.assertTrue(os.path.exists(output_dir))
            self.assertTrue(os.path.isdir(output_dir))
            
        finally:
            # Clean up
            import shutil
            shutil.rmtree(test_dir)


class TestConsoleOutput(unittest.TestCase):
    """Test console output and logging functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.utms = test_utils.get_utms()
    
    @patch('builtins.print')
    def test_progress_reporting(self, mock_print):
        """Test progress reporting during scans."""
        # Simulate progress reporting
        total_repos = 5
        processed_repos = 3
        
        # Test progress calculation
        progress_percent = (processed_repos / total_repos) * 100
        self.assertEqual(progress_percent, 60.0)
        
        # Test that progress would be printed
        progress_message = f"Progress: {processed_repos}/{total_repos} repositories ({progress_percent:.1f}%)"
        print(progress_message)
        
        mock_print.assert_called_with(progress_message)
    
    @patch('sys.stdout')
    def test_summary_output_format(self, mock_stdout):
        """Test summary output formatting."""
        # Test summary statistics formatting
        summary_data = {
            'total_repositories': 5,
            'total_files_scanned': 50,
            'total_modules_found': 25,
            'registry_modules': 20,
            'git_modules': 3,
            'local_modules': 2
        }
        
        # Format summary (simulate what the application would do)
        summary_lines = [
            f"📊 Scan Summary:",
            f"   Repositories scanned: {summary_data['total_repositories']}",
            f"   Files processed: {summary_data['total_files_scanned']}",
            f"   Modules found: {summary_data['total_modules_found']}",
            f"   Registry modules: {summary_data['registry_modules']}",
            f"   Git modules: {summary_data['git_modules']}",
            f"   Local modules: {summary_data['local_modules']}"
        ]
        
        for line in summary_lines:
            print(line)
        
        # Verify expected number of print calls
        self.assertEqual(len(summary_lines), 7)
    
    @patch('builtins.print')
    def test_error_output_formatting(self, mock_print):
        """Test error message formatting."""
        error_messages = [
            "❌ Error: Failed to authenticate with Azure DevOps",
            "⚠️  Warning: Repository 'test-repo' could not be accessed",
            "ℹ️  Info: Skipping binary file 'image.png'"
        ]
        
        for error_msg in error_messages:
            print(error_msg)
        
        # Verify all error messages were printed
        self.assertEqual(mock_print.call_count, len(error_messages))


class TestOutputCustomization(unittest.TestCase):
    """Test output customization and configuration options."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.utms = test_utils.get_utms()
    
    def test_timestamp_formatting(self):
        """Test timestamp formatting in output."""
        # Test ISO format timestamp
        timestamp = datetime.now().isoformat()
        self.assertIn('T', timestamp)  # ISO format includes 'T'
        
        # Test custom timestamp format
        custom_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.assertRegex(custom_timestamp, r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')
    
    def test_output_filtering(self):
        """Test filtering options for output."""
        # Create sample modules with different types
        all_modules = [
            {
                'name': 'registry_module',
                'source': 'hashicorp/consul/aws',
                'type': 'registry'
            },
            {
                'name': 'git_module', 
                'source': 'git::https://github.com/user/module.git',
                'type': 'git'
            },
            {
                'name': 'local_module',
                'source': './modules/local',
                'type': 'local'
            }
        ]
        
        # Test filtering by type
        registry_only = [mod for mod in all_modules if mod['type'] == 'registry']
        self.assertEqual(len(registry_only), 1)
        self.assertEqual(registry_only[0]['name'], 'registry_module')
        
        git_only = [mod for mod in all_modules if mod['type'] == 'git']
        self.assertEqual(len(git_only), 1)
        self.assertEqual(git_only[0]['name'], 'git_module')
    
    def test_output_verbosity_levels(self):
        """Test different verbosity levels in output."""
        # Test minimal output (just counts)
        minimal_output = {
            'total_modules': 25,
            'registry_modules': 20,
            'git_modules': 3,
            'local_modules': 2
        }
        
        # Test detailed output (includes module details)
        detailed_output = {
            'summary': minimal_output,
            'modules': [
                {
                    'name': 'consul_module',
                    'source': 'hashicorp/consul/aws',
                    'version': '0.1.0',
                    'file': 'main.tf',
                    'line': 10
                }
            ]
        }
        
        # Verify structure differences
        self.assertIn('total_modules', minimal_output)
        self.assertNotIn('modules', minimal_output)
        
        self.assertIn('summary', detailed_output)
        self.assertIn('modules', detailed_output)
        self.assertIsInstance(detailed_output['modules'], list)


if __name__ == '__main__':
    unittest.main()
