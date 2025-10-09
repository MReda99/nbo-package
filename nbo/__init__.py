"""
NBO (Next Best Offer) Package

A machine learning pipeline for personalized offer optimization that includes:
- Data loading and validation
- Feature engineering
- Model training and scoring
- Guardrails and business rules
- Decision optimization

Main components:
- DataLoader: Handle CSV data loading and validation
- ModelTrainer: Train uplift models for offer optimization  
- Pipeline: Orchestrate the full NBO workflow
- Config: Configuration management
"""

# Import version information
from ._version import __version__, get_version, get_version_info, check_python_version

__author__ = "Finetooth"
__email__ = "mohamed.reda@finetooth.ai"

# Check Python version compatibility on import
check_python_version()

# Import main classes for easy access
from .configuration import NBOConfig, get_config, set_config
from .data_loader import DataLoader, load_data, quick_load
from .validation import assess_data_quality, validate_business_rules, check_data_consistency
from .pipeline import NBOPipeline, run_nbo_pipeline
from .user_setup import UserDataSetup, setup_user_data, validate_user_data

# CLI is available but not imported by default to avoid heavy imports

# Define what gets imported with "from nbo import *"
__all__ = [
    "NBOConfig",
    "get_config", 
    "set_config",
    "DataLoader",
    "load_data",
    "quick_load",
    "assess_data_quality",
    "validate_business_rules",
    "check_data_consistency",
    "NBOPipeline",
    "run_nbo_pipeline",
    "UserDataSetup",
    "setup_user_data",
    "validate_user_data",
    # "ModelTrainer",  # Will be created later if needed
    "__version__",
    "get_version",
    "get_version_info",
]

# Package-level configuration
import logging

# Set up default logging configuration
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Expose version info
def get_version():
    """Return the current package version."""
    return __version__

def get_package_info():
    """Return package information."""
    return {
        "name": "nbo-package",
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "description": "A machine learning pipeline for Next Best Offer (NBO) optimization"
    }
