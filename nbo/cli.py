"""
Command-line interface for the NBO package.

Provides command-line tools for running the NBO pipeline and individual components.
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Optional

from .pipeline import NBOPipeline, run_nbo_pipeline
from .configuration import NBOConfig
from .data_loader import DataLoader
from .user_setup import UserDataSetup, setup_user_data, validate_user_data
from ._version import __version__


def setup_logging(level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def cmd_run_pipeline(args):
    """Run the complete NBO pipeline."""
    setup_logging(args.log_level)
    
    try:
        result = run_nbo_pipeline(
            data_path=args.data_path,
            output_path=args.output_path,
            config_path=args.config_path,
            steps=args.steps
        )
        
        print(f"\nPipeline run completed: {result.run_id}")
        print(f"Status: {result.status}")
        print(f"Steps completed: {len(result.steps_completed)}")
        print(f"Steps failed: {len(result.steps_failed)}")
        
        if result.steps_completed:
            print(f"Completed steps: {', '.join(result.steps_completed)}")
        
        if result.steps_failed:
            print(f"Failed steps: {', '.join(result.steps_failed)}")
            for error in result.error_messages:
                print(f"Error: {error}")
        
        if result.outputs_generated:
            print(f"\nOutputs generated:")
            for filename, path in result.outputs_generated.items():
                print(f"  {filename} -> {path}")
        
        # Exit with error code if pipeline failed
        if result.status == "failed":
            sys.exit(1)
        elif result.status == "completed_with_errors":
            sys.exit(2)
        else:
            sys.exit(0)
            
    except Exception as e:
        print(f"Error running pipeline: {e}")
        sys.exit(1)


def cmd_run_step(args):
    """Run a single pipeline step."""
    setup_logging(args.log_level)
    
    try:
        config = NBOConfig(args.config_path) if args.config_path else None
        pipeline = NBOPipeline(
            data_path=args.data_path,
            output_path=args.output_path,
            config=config
        )
        
        success = pipeline.run_step(args.step_name)
        
        if success:
            print(f"Step '{args.step_name}' completed successfully")
            sys.exit(0)
        else:
            print(f"Step '{args.step_name}' failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error running step: {e}")
        sys.exit(1)


def cmd_list_steps(args):
    """List all available pipeline steps."""
    try:
        config = NBOConfig(args.config_path) if args.config_path else None
        pipeline = NBOPipeline(
            data_path=args.data_path,
            output_path=args.output_path,
            config=config
        )
        
        print("Available pipeline steps:")
        print("=" * 50)
        
        execution_order = pipeline.get_execution_order()
        
        for i, step_name in enumerate(execution_order, 1):
            step_info = pipeline.get_step_info(step_name)
            print(f"{i}. {step_name}")
            print(f"   Description: {step_info['description']}")
            print(f"   Script: {step_info['script_path']}")
            print(f"   Inputs: {', '.join(step_info['inputs'])}")
            print(f"   Outputs: {', '.join(step_info['outputs'])}")
            if step_info['dependencies']:
                print(f"   Dependencies: {', '.join(step_info['dependencies'])}")
            print(f"   Script exists: {'✓' if step_info['script_exists'] else '✗'}")
            print()
            
    except Exception as e:
        print(f"Error listing steps: {e}")
        sys.exit(1)


def cmd_validate_data(args):
    """Validate input data files."""
    setup_logging(args.log_level)
    
    try:
        config = NBOConfig(args.config_path) if args.config_path else None
        loader = DataLoader(args.data_path, config)
        
        available_tables = loader.get_available_tables()
        print(f"Found {len(available_tables)} data files:")
        
        for table_name in available_tables:
            try:
                info = loader.get_table_info(table_name)
                print(f"  ✓ {table_name}: {info.get('column_count', '?')} columns, ~{info.get('estimated_rows', '?')} rows")
            except Exception as e:
                print(f"  ✗ {table_name}: Error - {e}")
        
        # Try to load and validate a few tables
        if args.validate_schema:
            print("\nValidating schemas...")
            for table_name in available_tables[:5]:  # Validate first 5 tables
                try:
                    df = loader.load_table(table_name, validate_schema=True)
                    print(f"  ✓ {table_name}: Schema validation passed")
                except Exception as e:
                    print(f"  ✗ {table_name}: Schema validation failed - {e}")
        
    except Exception as e:
        print(f"Error validating data: {e}")
        sys.exit(1)


def cmd_setup_data_templates(args):
    """Create data templates for users."""
    try:
        templates = setup_user_data(args.output_dir)
        
        print(f"Data templates created in: {args.output_dir}")
        print(f"Created {len(templates)} template files:")
        
        for table_name, file_path in templates.items():
            print(f"  ✓ {table_name}.csv")
        
        print(f"\nNext steps:")
        print(f"1. Replace sample data in {args.output_dir}/ with your actual data")
        print(f"2. Run: nbo-run validate-user-data --data-path {args.output_dir}")
        print(f"3. Run: nbo-run pipeline --data-path {args.output_dir}")
        
    except Exception as e:
        print(f"Error creating data templates: {e}")
        sys.exit(1)


def cmd_validate_user_data(args):
    """Validate user-provided data."""
    setup_logging(args.log_level)
    
    try:
        config = NBOConfig(args.config_path) if args.config_path else None
        setup = UserDataSetup(config)
        
        print(f"Validating user data in: {args.data_path}")
        print("=" * 50)
        
        validation_report = setup.validate_user_data(
            Path(args.data_path), 
            strict=not args.ignore_errors
        )
        
        # Print summary
        print(f"Validation Results:")
        print(f"  Files validated: {validation_report['files_validated']}")
        print(f"  Files passed: {validation_report['files_passed']}")
        print(f"  Files failed: {validation_report['files_failed']}")
        print(f"  Overall status: {validation_report['overall_status']}")
        
        # Print detailed results
        if validation_report['validation_results']:
            print(f"\nDetailed Results:")
            for table_name, result in validation_report['validation_results'].items():
                status_icon = "✓" if result['status'] == 'passed' else "✗"
                print(f"  {status_icon} {table_name}: {result['rows']} rows, "
                      f"{result['columns']} columns, "
                      f"quality score: {result['quality_score']:.1f}")
        
        # Print errors
        if validation_report['errors']:
            print(f"\nErrors:")
            for error in validation_report['errors']:
                print(f"  ✗ {error}")
        
        # Print warnings
        if validation_report['warnings']:
            print(f"\nWarnings:")
            for warning in validation_report['warnings']:
                print(f"  ⚠ {warning}")
        
        # Save report if requested
        if args.save_report:
            import json
            report_file = Path(args.data_path) / "validation_report.json"
            with open(report_file, 'w') as f:
                json.dump(validation_report, f, indent=2)
            print(f"\nValidation report saved to: {report_file}")
        
        # Exit with appropriate code
        if validation_report['overall_status'] == 'failed':
            sys.exit(1)
        elif validation_report['overall_status'] == 'partial':
            sys.exit(2)
        else:
            print(f"\n✓ All data validation passed! You can now run the pipeline.")
            sys.exit(0)
            
    except Exception as e:
        print(f"Error validating user data: {e}")
        sys.exit(1)


def cmd_check_pipeline(args):
    """Check pipeline configuration and dependencies."""
    try:
        config = NBOConfig(args.config_path) if args.config_path else None
        pipeline = NBOPipeline(
            data_path=args.data_path,
            output_path=args.output_path,
            config=config
        )
        
        status = pipeline.get_pipeline_status()
        print("Pipeline Configuration:")
        print("=" * 50)
        print(f"Data path: {status['data_path']}")
        print(f"Output path: {status['output_path']}")
        print(f"Scripts path: {status['scripts_path']}")
        print(f"Total steps: {status['total_steps']}")
        print(f"Execution order: {' -> '.join(status['execution_order'])}")
        
        print("\nStep Validation:")
        print("=" * 20)
        
        all_valid = True
        for step_name in status['execution_order']:
            step_info = pipeline.get_step_info(step_name)
            script_status = "✓" if step_info['script_exists'] else "✗"
            print(f"{script_status} {step_name}: {step_info['script_path']}")
            
            if not step_info['script_exists']:
                all_valid = False
        
        if all_valid:
            print("\n✓ All pipeline scripts found and configuration is valid")
        else:
            print("\n✗ Some pipeline scripts are missing")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error checking pipeline: {e}")
        sys.exit(1)


def create_parser():
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="NBO Package Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Set up data templates for users
  nbo-run setup-data-templates --output-dir ./my_data
  
  # Validate user data
  nbo-run validate-user-data --data-path ./my_data --save-report
  
  # Run complete pipeline
  nbo-run pipeline --data-path ./data --output-path ./output
  
  # Run specific steps
  nbo-run pipeline --steps catalog_guardrails fatigue_candidates
  
  # Run single step
  nbo-run step model_training --data-path ./data
  
  # List available steps
  nbo-run list-steps
  
  # Validate data files
  nbo-run validate-data --data-path ./data --validate-schema
  
  # Check pipeline configuration
  nbo-run check-pipeline --data-path ./data
        """
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version=f'nbo-package {__version__}'
    )
    
    # Global arguments
    parser.add_argument(
        '--data-path',
        default='data',
        help='Path to input data directory (default: data)'
    )
    
    parser.add_argument(
        '--output-path', 
        default='output',
        help='Path to output directory (default: output)'
    )
    
    parser.add_argument(
        '--config-path',
        help='Path to configuration file or directory'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Pipeline command
    pipeline_parser = subparsers.add_parser(
        'pipeline',
        help='Run the complete NBO pipeline'
    )
    pipeline_parser.add_argument(
        '--steps',
        nargs='*',
        help='Specific steps to run (default: all steps)'
    )
    pipeline_parser.set_defaults(func=cmd_run_pipeline)
    
    # Step command
    step_parser = subparsers.add_parser(
        'step',
        help='Run a single pipeline step'
    )
    step_parser.add_argument(
        'step_name',
        help='Name of the step to run'
    )
    step_parser.set_defaults(func=cmd_run_step)
    
    # List steps command
    list_parser = subparsers.add_parser(
        'list-steps',
        help='List all available pipeline steps'
    )
    list_parser.set_defaults(func=cmd_list_steps)
    
    # Validate data command
    validate_parser = subparsers.add_parser(
        'validate-data',
        help='Validate input data files'
    )
    validate_parser.add_argument(
        '--validate-schema',
        action='store_true',
        help='Also validate data against schema configuration'
    )
    validate_parser.set_defaults(func=cmd_validate_data)
    
    # Setup data templates command
    setup_templates_parser = subparsers.add_parser(
        'setup-data-templates',
        help='Create CSV templates for user data'
    )
    setup_templates_parser.add_argument(
        '--output-dir',
        default='data_template',
        help='Directory to create templates in (default: data_template)'
    )
    setup_templates_parser.set_defaults(func=cmd_setup_data_templates)
    
    # Validate user data command
    validate_user_parser = subparsers.add_parser(
        'validate-user-data',
        help='Validate user-provided data files'
    )
    validate_user_parser.add_argument(
        '--ignore-errors',
        action='store_true',
        help='Continue validation even if errors are found'
    )
    validate_user_parser.add_argument(
        '--save-report',
        action='store_true',
        help='Save validation report as JSON file'
    )
    validate_user_parser.set_defaults(func=cmd_validate_user_data)
    
    # Check pipeline command
    check_parser = subparsers.add_parser(
        'check-pipeline',
        help='Check pipeline configuration and dependencies'
    )
    check_parser.set_defaults(func=cmd_check_pipeline)
    
    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Call the appropriate command function
    args.func(args)


if __name__ == '__main__':
    main()
