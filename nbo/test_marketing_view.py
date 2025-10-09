"""
Test Marketing View Generator

This script combines validated offer catalog data with decision log outputs
to create a comprehensive test marketing view.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def main():
    """Generate test marketing view from contract checks and guardrails winners outputs."""
    
    print("Starting test marketing view generation...")
    
    try:
        # Input files (these should be available from previous steps)
        offer_catalog_file = "offer_catalog_v1.csv"  # From contract_checks
        decision_log_file = "decision_log_output.csv"  # From guardrails_winners
        
        # Try to load from output directory first, then data directory
        def load_file(filename):
            output_path = Path("../output") / filename
            data_path = Path("../data") / filename
            current_path = Path(filename)
            
            for path in [output_path, current_path, data_path]:
                if path.exists():
                    print(f"Loading {filename} from {path}")
                    return pd.read_csv(path)
            
            raise FileNotFoundError(f"Could not find {filename} in any expected location")
        
        # Load input data
        offer_catalog = load_file(offer_catalog_file)
        decision_log = load_file(decision_log_file)
        
        print(f"Loaded offer catalog: {len(offer_catalog)} records")
        print(f"Loaded decision log: {len(decision_log)} records")
        
        # Create test marketing view by joining the data
        # This combines the validated offer information with the final decisions
        
        # Ensure we have the key columns for joining
        if 'promotion_id' not in offer_catalog.columns:
            raise ValueError("offer_catalog missing promotion_id column")
        
        if 'promotion_id' not in decision_log.columns:
            raise ValueError("decision_log missing promotion_id column")
        
        # Merge decision log with offer catalog to get complete offer details
        test_marketing_view = decision_log.merge(
            offer_catalog[['promotion_id', 'promotion_name', 'product_category', 
                          'base_price', 'channel_eligibility', 'start_date', 'end_date',
                          'legal_flag']].drop_duplicates(),
            on='promotion_id',
            how='left',
            suffixes=('', '_catalog')
        )
        
        # Add marketing-specific fields
        test_marketing_view['campaign_type'] = 'NBO_ML_DRIVEN'
        test_marketing_view['test_cell'] = 'TREATMENT'
        test_marketing_view['selection_method'] = 'UPLIFT_MODEL'
        test_marketing_view['created_timestamp'] = pd.Timestamp.now().isoformat()
        
        # Add some derived marketing metrics
        if 'eim_final' in test_marketing_view.columns and 'expected_ticket' in test_marketing_view.columns:
            test_marketing_view['roi_estimate'] = (
                test_marketing_view['eim_final'] / test_marketing_view['expected_ticket']
            ).fillna(0)
        
        if 'discount_cost_banded' in test_marketing_view.columns and 'base_price' in test_marketing_view.columns:
            test_marketing_view['discount_percentage'] = (
                test_marketing_view['discount_cost_banded'] / test_marketing_view['base_price'] * 100
            ).fillna(0)
        
        # Select final columns for marketing view
        marketing_columns = [
            'guest_id', 'promotion_id', 'promotion_name', 'product_category',
            'campaign_type', 'test_cell', 'selection_method',
            'base_price', 'discount_cost_banded', 'discount_percentage',
            'expected_ticket', 'eim_final', 'roi_estimate',
            'channel_eligibility', 'start_date', 'end_date',
            'p_treat', 'p_ctrl', 'uplift',
            'created_timestamp', 'snapshot_id', 'build_version'
        ]
        
        # Only include columns that exist
        available_columns = [col for col in marketing_columns if col in test_marketing_view.columns]
        final_view = test_marketing_view[available_columns].copy()
        
        # Sort by guest_id for consistent output
        final_view = final_view.sort_values('guest_id')
        
        # Save output
        output_file = "test_marketing_view_output.csv"
        final_view.to_csv(output_file, index=False)
        
        print(f"Test marketing view generated successfully:")
        print(f"  Output file: {output_file}")
        print(f"  Records: {len(final_view)}")
        print(f"  Columns: {len(final_view.columns)}")
        print(f"  Unique guests: {final_view['guest_id'].nunique()}")
        print(f"  Unique promotions: {final_view['promotion_id'].nunique()}")
        
        # Display sample of the output
        print(f"\nSample output:")
        print(final_view.head(3).to_string())
        
    except Exception as e:
        print(f"Error generating test marketing view: {e}")
        raise

if __name__ == "__main__":
    main()
