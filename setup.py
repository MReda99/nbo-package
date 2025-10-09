"""
Setup configuration for the NBO (Next Best Offer) package.
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "NBO (Next Best Offer) Package - A machine learning pipeline for personalized offer optimization"

setup(
    name="nbo-package",
    version="1.0.0",
    author="Finetooth",
    author_email="mohamed.reda@finetooth.ai",
    description="A machine learning pipeline for Next Best Offer (NBO) optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/nbo-package", # to be updated
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Data Scientists",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "scikit-learn>=1.1.0",
        "pyarrow>=10.0.0",  # For parquet support
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    package_data={
        "nbo": [
            "config/*.json",
            "data/*.csv",
        ],
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "nbo-run=nbo.cli:main",
            "nbo-pipeline=nbo.pipeline:run_pipeline",
        ],
    },
    zip_safe=False,
)
