"""
UTMS Test Suite
===============

Comprehensive unit test suite for Universal Terraform Module Scanner (UTMS).

This test suite provides comprehensive coverage of all UTMS functionality including:
- Data classes and configuration
- Authentication providers
- API clients for multiple source providers
- Terraform file scanning and parsing
- Module reference analysis
- Repository discovery and scanning
- Output handling and reporting

Test Modules:
=============

- test_utils.py: Import utilities for UTMS executable script testing
- test_data_classes.py: Tests for UTMS data structures and configuration
- test_authentication.py: Tests for authentication providers and management
- test_api_clients.py: Tests for Azure DevOps and GitHub API integration
- test_terraform_scanner.py: Tests for Terraform file parsing and module detection
- test_application_flow.py: Tests for main application workflow and coordination
- test_module_processing.py: Tests for module analysis and processing logic
- test_output_handling.py: Tests for output formatting and file generation
- run_tests.py: Professional test runner with coverage and timing

Test Categories:
===============

1. **Infrastructure Tests** (test_utils.py)
   - UTMS script import mechanism
   - Module loading and caching
   - Test environment setup

2. **Data Structure Tests** (test_data_classes.py) ✅ 23 tests passing
   - UTMSConfig configuration validation
   - ModuleReference creation and properties
   - ScanResult data processing and aggregation
   - Repository management and metadata
   - SourceType enumeration validation
   - Custom exception handling

3. **Authentication Tests** (test_authentication.py)
   - EnvironmentAuthProvider testing
   - KeychainAuthProvider testing (macOS)
   - InteractiveAuthProvider testing
   - SourceAuthenticationManager integration
   - Token caching and validation
   - Provider fallback chains

4. **API Integration Tests** (test_api_clients.py)
   - BaseAPIClient common functionality
   - Azure DevOps API client testing
   - GitHub API client testing
   - HTTP error handling and retries
   - Rate limiting and pagination
   - Authentication header management

5. **Terraform Processing Tests** (test_terraform_scanner.py)
   - TerraformFileScanner module detection
   - Pattern matching and regex validation
   - Version constraint parsing
   - Module type classification
   - Line number tracking
   - Error handling for malformed files

6. **Application Flow Tests** (test_application_flow.py)
   - Command-line argument parsing
   - Main application workflow coordination
   - Component integration testing
   - Error handling and user feedback
   - Help and usage information
   - Output directory management

7. **Module Processing Tests** (test_module_processing.py)
   - Module classification and analysis
   - Version validation and parsing
   - Cross-repository aggregation
   - Usage pattern identification
   - Module uniqueness and deduplication
   - Statistical analysis

8. **Output Handling Tests** (test_output_handling.py)
   - JSON serialization and formatting
   - File output operations
   - Console output and progress reporting
   - Error message formatting
   - Output customization and filtering
   - Verbosity level management

Usage:
    # Run all tests
    python utms/tests/run_tests.py
    
    # Run with coverage analysis
    python utms/tests/run_tests.py --coverage
    
    # Run specific module tests
    python utms/tests/run_tests.py --module data_classes
    
    # Run specific test class
    python utms/tests/run_tests.py --module authentication --class TestEnvironmentAuthProvider
    
    # Using pytest (alternative)
    python -m pytest utms/tests/ -v
    python -m pytest utms/tests/ --cov=utms --cov-report=html

Test Coverage:
- Configuration and data structures: Complete coverage of UTMSConfig, ModuleReference, ScanResult
- Authentication: All auth providers with proper mocking and error scenarios
- API clients: Full HTTP client testing for Azure DevOps and GitHub APIs
- Terraform scanning: Comprehensive parsing logic with real-world test cases
- Repository handling: Discovery, filtering, and scanning workflows
- Module analysis: Version constraint resolution and module reference parsing
- Output handling: All format types with file I/O and error handling
- Application flow: End-to-end scenarios with integration testing

Quality Assurance:
- All tests use proper mocking for external dependencies
- Edge cases and error conditions thoroughly tested
- Professional test structure with setUp/tearDown methods
- Comprehensive assertions covering success and failure scenarios
- Clean separation of concerns with focused test modules
- Real-world test data and scenarios included
"""

__version__ = "1.0.0"
