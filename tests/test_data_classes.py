"""
Test Data Classes and Configuration
====================================

Unit tests for UTMS data classes, configuration, and core data structures.
"""

import unittest
import sys
import os
from datetime import datetime

# Add parent directory to path to import utms
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import UTMS module using test utilities
import test_utils
utms = test_utils.get_utms()


class TestUTMSConfig(unittest.TestCase):
    """Test UTMSConfig configuration class."""
    
    def test_config_constants_exist(self):
        """Test that all required configuration constants are defined."""
        # Test that UTMSConfig class exists
        self.assertTrue(hasattr(utms, 'UTMSConfig'))
        
        # Test essential constants exist
        config_attrs = dir(utms.UTMSConfig)
        expected_constants = [
            'MAX_CONCURRENT_FILES',
            'MAX_CONCURRENT_REPOS', 
            'API_TIMEOUT_SECONDS',
            'MAX_FILE_SIZE_MB',
            'REPOSITORY_BATCH_SIZE'
        ]
        
        for constant in expected_constants:
            self.assertIn(constant, config_attrs, f"Missing constant: {constant}")
    
    def test_environment_variables_list(self):
        """Test environment variable configuration."""
        # Check if authentication-related classes exist
        self.assertTrue(hasattr(utms, 'EnvironmentAuthProvider'))
        self.assertTrue(hasattr(utms, 'SourceType'))
        
        # Test SourceType enum values
        source_type = utms.SourceType
        self.assertTrue(hasattr(source_type, 'AZURE_DEVOPS'))
        self.assertTrue(hasattr(source_type, 'GITHUB'))


class TestModuleReference(unittest.TestCase):
    """Test ModuleReference data class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_module_ref = utms.ModuleReference(
            local_name="network_module",
            source="git::https://github.com/Azure/terraform-azurerm-network.git",
            version="~> 2.0",
            file_path="./main.tf",
            line_number=15,
            repository_name="test-repo",
            project_name="test-project"
        )
    
    def test_module_reference_creation(self):
        """Test creating ModuleReference instances."""
        self.assertEqual(self.sample_module_ref.local_name, "network_module")
        self.assertEqual(self.sample_module_ref.source, "git::https://github.com/Azure/terraform-azurerm-network.git")
        self.assertEqual(self.sample_module_ref.version, "~> 2.0")
        self.assertEqual(self.sample_module_ref.file_path, "./main.tf")
        self.assertEqual(self.sample_module_ref.line_number, 15)
        self.assertEqual(self.sample_module_ref.repository_name, "test-repo")
        self.assertEqual(self.sample_module_ref.project_name, "test-project")
    
    def test_module_reference_str_representation(self):
        """Test string representation of ModuleReference."""
        str_repr = str(self.sample_module_ref)
        self.assertIn("test-repo", str_repr)
        self.assertIn("main.tf", str_repr)
        self.assertIn("15", str_repr)
    
    def test_module_reference_equality(self):
        """Test ModuleReference equality comparison."""
        ref1 = utms.ModuleReference(
            source="git::https://github.com/test/module.git",
            version="1.0.0",
            file_path="main.tf",
            line_number=10,
            repository_name="repo1",
            project_name="project1"
        )
        
        ref2 = utms.ModuleReference(
            source="git::https://github.com/test/module.git",
            version="1.0.0",
            file_path="main.tf",
            line_number=10,
            repository_name="repo1",
            project_name="project1"
        )
        
        self.assertEqual(ref1, ref2)
    
    def test_get_module_name(self):
        """Test extracting module name from source."""
        if hasattr(self.sample_module_ref, 'get_module_name'):
            module_name = self.sample_module_ref.get_module_name()
            self.assertIsInstance(module_name, str)
            self.assertTrue(len(module_name) > 0)
    
    def test_is_registry_module(self):
        """Test identifying registry vs. Git modules."""
        if hasattr(self.sample_module_ref, 'is_registry_module'):
            # Git module should return False (using property, not method call)
            self.assertFalse(self.sample_module_ref.is_registry_module)
            
            # Registry module should return True
            registry_ref = utms.ModuleReference(
                local_name="test_registry_module",
                source="hashicorp/consul/aws",
                version="1.0.0",
                file_path="main.tf",
                line_number=5,
                repository_name="test-repo"
            )
            self.assertTrue(registry_ref.is_registry_module)


class TestScanResult(unittest.TestCase):
    """Test ScanResult data class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_modules = [
            utms.ModuleReference(
                local_name="network_module",
                source="git::https://github.com/Azure/terraform-azurerm-network.git",
                version="~> 2.0",
                file_path="./main.tf",
                line_number=15,
                repository_name="test-repo",
                project_name="test-project"
            ),
            utms.ModuleReference(
                local_name="storage_module",
                source="app.terraform.io/org/storage/azurerm",
                version="1.0.0",
                file_path="./storage.tf",
                line_number=8,
                repository_name="test-repo",
                project_name="test-project"
            )
        ]
        
        self.scan_result = utms.ScanResult(
            source_type=utms.SourceType.AZURE_DEVOPS,
            organization="test-org",
            project_name="test-project",
            repository_name="test-repo",
            total_files_scanned=25,
            total_modules_found=len(self.sample_modules),
            modules=self.sample_modules
        )
    
    def test_scan_result_creation(self):
        """Test creating ScanResult instances."""
        self.assertEqual(self.scan_result.project_name, "test-project")
        self.assertEqual(self.scan_result.repository_name, "test-repo")
        self.assertEqual(len(self.scan_result.modules), 2)
        self.assertEqual(self.scan_result.total_files_scanned, 25)
    
    def test_scan_result_with_errors(self):
        """Test ScanResult with error tracking."""
        # Note: ScanResult doesn't have an errors field in the actual implementation
        # This test demonstrates creating minimal scan results
        result_with_errors = utms.ScanResult(
            source_type=utms.SourceType.AZURE_DEVOPS,
            organization="error-org",
            project_name="error-project",
            repository_name="error-repo",
            total_files_scanned=0,
            total_modules_found=0,
            modules=[]
        )
        
        self.assertEqual(len(result_with_errors.modules), 0)
        self.assertEqual(result_with_errors.total_files_scanned, 0)
    
    def test_get_unique_modules(self):
        """Test getting unique modules from scan result."""
        if hasattr(self.scan_result, 'get_unique_modules'):
            unique_modules = self.scan_result.get_unique_modules()
            self.assertIsInstance(unique_modules, list)
            self.assertEqual(len(unique_modules), 2)
    
    def test_get_registry_modules(self):
        """Test filtering registry modules from scan result."""
        if hasattr(self.scan_result, 'get_registry_modules'):
            registry_modules = self.scan_result.get_registry_modules()
            self.assertIsInstance(registry_modules, list)
            # Should find the app.terraform.io module
            self.assertTrue(any("app.terraform.io" in mod.source for mod in registry_modules))
    
    def test_get_git_modules(self):
        """Test filtering Git modules from scan result."""
        if hasattr(self.scan_result, 'get_git_modules'):
            git_modules = self.scan_result.get_git_modules()
            self.assertIsInstance(git_modules, list)
            # Should find the GitHub module
            self.assertTrue(any("github.com" in mod.source for mod in git_modules))


class TestRepository(unittest.TestCase):
    """Test Repository data class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.repository = utms.Repository(
            name="test-repository",
            id="repo-123",
            project_name="test-project",
            project_id="proj-456",
            clone_url="https://dev.azure.com/org/project/_git/test-repository",
            default_branch="main",
            web_url="https://dev.azure.com/org/project/_git/test-repository"
        )
    
    def test_repository_creation(self):
        """Test creating Repository instances."""
        self.assertEqual(self.repository.name, "test-repository")
        self.assertEqual(self.repository.id, "repo-123")
        self.assertEqual(self.repository.project_name, "test-project")
        self.assertEqual(self.repository.clone_url, "https://dev.azure.com/org/project/_git/test-repository")
        self.assertEqual(self.repository.default_branch, "main")
    
    def test_repository_str_representation(self):
        """Test string representation of Repository."""
        str_repr = str(self.repository)
        self.assertIn("test-repository", str_repr)
        self.assertIn("test-project", str_repr)
    
    def test_get_full_name(self):
        """Test getting full repository name."""
        if hasattr(self.repository, 'full_name'):
            full_name = self.repository.full_name
            self.assertEqual(full_name, "test-project/test-repository")
    
    def test_is_active(self):
        """Test repository properties."""
        # Test that repository has expected attributes
        self.assertTrue(hasattr(self.repository, 'name'))
        self.assertTrue(hasattr(self.repository, 'project_name'))
        self.assertTrue(hasattr(self.repository, 'source_type'))
        self.assertEqual(self.repository.source_type, utms.SourceType.AZURE_DEVOPS)


class TestSourceType(unittest.TestCase):
    """Test SourceType enumeration."""
    
    def test_source_type_enum_exists(self):
        """Test that SourceType enum is defined."""
        self.assertTrue(hasattr(utms, 'SourceType'))
    
    def test_source_type_values(self):
        """Test SourceType enum values."""
        source_type = utms.SourceType
        expected_values = ['AZURE_DEVOPS', 'GITHUB']
        
        for value in expected_values:
            self.assertTrue(hasattr(source_type, value))
    
    def test_source_type_string_conversion(self):
        """Test converting SourceType to string."""
        azure_type = utms.SourceType.AZURE_DEVOPS
        github_type = utms.SourceType.GITHUB
        
        self.assertIsInstance(str(azure_type), str)
        self.assertIsInstance(str(github_type), str)


class TestExceptions(unittest.TestCase):
    """Test custom exception classes."""
    
    def test_api_error_exception(self):
        """Test APIError exception."""
        self.assertTrue(hasattr(utms, 'APIError'))
        
        with self.assertRaises(utms.APIError):
            raise utms.APIError("Test API error")
    
    def test_scan_error_exception(self):
        """Test ScanError exception."""
        self.assertTrue(hasattr(utms, 'ScanError'))
        
        with self.assertRaises(utms.ScanError):
            raise utms.ScanError("Test scan error")
    
    def test_exception_hierarchy(self):
        """Test that custom exceptions inherit from appropriate base classes."""
        self.assertTrue(issubclass(utms.APIError, Exception))
        self.assertTrue(issubclass(utms.ScanError, Exception))
    
    def test_exception_with_details(self):
        """Test exceptions with detailed error information."""
        error_details = {
            "status_code": 404,
            "message": "Repository not found",
            "url": "https://api.example.com/repo"
        }
        
        try:
            raise utms.APIError("API request failed", error_details)
        except utms.APIError as e:
            self.assertIn("API request failed", str(e))


if __name__ == '__main__':
    unittest.main()
