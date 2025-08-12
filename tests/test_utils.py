"""
UTMS Test Import Utilities
==========================

Utilities for importing the UTMS module in tests.
"""

import sys
import os


def import_utms():
    """Import the UTMS module from the executable script."""
    # Get the path to the utms script
    utms_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "utms")
    
    # Verify the file exists
    if not os.path.exists(utms_path):
        raise ImportError(f"UTMS script not found at {utms_path}")
    
    # Read the script content
    with open(utms_path, 'r') as f:
        utms_code = f.read()
    
    # Create a module namespace
    utms_module = type(sys)('utms_module')
    utms_module.__file__ = utms_path
    
    # Add the module to sys.modules to handle imports within the module
    sys.modules["utms_module"] = utms_module
    
    # Execute the module code in the module namespace
    # We'll override __name__ to prevent the main() function from running
    utms_module.__name__ = 'utms_module'
    exec(utms_code, utms_module.__dict__)
    
    return utms_module


# Cache the imported module to avoid repeated imports
_utms_module = None


def get_utms():
    """Get the cached UTMS module or import it if not cached."""
    global _utms_module
    if _utms_module is None:
        _utms_module = import_utms()
    return _utms_module
