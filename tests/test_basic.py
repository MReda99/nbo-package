"""
Basic tests for the NBO package.
"""

import pytest
import tempfile
import pandas as pd
from pathlib import Path

from nbo import NBOConfig, DataLoader, setup_user_data, validate_user_data, NBOPipeline


def test_package_imports():
    """Test that all main components can be imported."""
    from nbo import (
        NBOConfig, DataLoader, NBOPipeline,
        setup_user_data, validate_user_data,
        __version__
    )
    
    assert __version__ is not None
    assert NBOConfig is not None
    assert DataLoader is not None
    assert NBOPipeline is not None


def test_config_initialization():
    """Test configuration initialization."""
    config = NBOConfig()
    assert config is not None
    
    # Test settings access
    test_value = config.get_setting('nonexistent.key', 'default')
    assert test_value == 'default'
    
    # Test setting values
    config.set_setting('test.key', 'test_value')
    assert config.get_setting('test.key') == 'test_value'


def test_data_template_creation():
    """Test data template creation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        templates = setup_user_data(temp_dir)
        
        assert len(templates) > 0
        assert 'offer_master' in templates
        assert 'feature_mart' in templates
        
        # Check that files were created
        for table_name, file_path in templates.items():
            assert Path(file_path).exists()
            
            # Check that CSV has headers
            df = pd.read_csv(file_path)
            assert len(df.columns) > 0
            assert len(df) >= 1  # Should have sample row


def test_data_validation():
    """Test data validation functionality."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a simple test CSV
        test_data = pd.DataFrame({
            'guest_id': ['guest_1', 'guest_2'],
            'promotion_id': [1, 2],
            'base_price': [10.0, 15.0]
        })
        
        test_file = temp_path / 'offer_master.csv'
        test_data.to_csv(test_file, index=False)
        
        # Test validation
        report = validate_user_data(str(temp_path), strict=False)
        
        assert report['total_files'] >= 1
        assert 'offer_master' in report['validation_results']


def test_pipeline_initialization():
    """Test pipeline initialization."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create minimal data directory
        data_path = Path(temp_dir) / 'data'
        data_path.mkdir()
        
        # Create a dummy CSV file
        test_data = pd.DataFrame({'test_col': [1, 2, 3]})
        test_data.to_csv(data_path / 'test_table.csv', index=False)
        
        # Initialize pipeline
        pipeline = NBOPipeline(data_path=data_path)
        
        assert pipeline is not None
        assert len(pipeline.steps) > 0
        
        # Test execution order
        execution_order = pipeline.get_execution_order()
        assert len(execution_order) > 0
        assert 'catalog_guardrails' in execution_order


if __name__ == '__main__':
    # Run tests manually if pytest not available
    test_package_imports()
    test_config_initialization()
    test_data_template_creation()
    test_data_validation()
    test_pipeline_initialization()
    print("All tests passed!")
