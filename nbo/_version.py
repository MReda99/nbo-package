"""Version information for the NBO package."""

__version__ = "1.0.0"
__version_info__ = (1, 0, 0)

# Version history and compatibility
MIN_PYTHON_VERSION = (3, 8)
SUPPORTED_PYTHON_VERSIONS = [(3, 8), (3, 9), (3, 10), (3, 11)]

def get_version():
    """Return the current version string."""
    return __version__

def get_version_info():
    """Return version as a tuple of integers."""
    return __version_info__

def check_python_version():
    """Check if current Python version is supported."""
    import sys
    current_version = sys.version_info[:2]
    
    if current_version < MIN_PYTHON_VERSION:
        raise RuntimeError(
            f"Python {current_version[0]}.{current_version[1]} is not supported. "
            f"Minimum required version is {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}"
        )
    
    return True
