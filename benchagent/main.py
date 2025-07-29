#!/usr/bin/env python3
"""
BenchmarkAgent - Blockchain Benchmark Testing Agent

Usage:
    python main.py --config config/config.json --tasks config/tasks.json
    python main.py --env  # Use environment variable configuration
"""

import argparse
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

from core.config import BenchmarkConfig
from core.benchmark_agent import BenchmarkAgent


def setup_logging(output_dir: str, log_level: str = "INFO"):
    """Setup logging system"""
    # Output directory includes timestamp for organization
    log_dir = Path(output_dir) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure log format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers = []
    
    # Create file handler
    file_handler = logging.FileHandler(
        log_dir / "benchmark.log", 
        mode='w', 
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(log_format))
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format))
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def main():
    parser = argparse.ArgumentParser(description="BenchmarkAgent - Blockchain Benchmark Testing Agent")
    
    # Configuration options
    config_group = parser.add_mutually_exclusive_group(required=True)
    config_group.add_argument(
        "--config", 
        type=str, 
        help="Configuration file path"
    )
    config_group.add_argument(
        "--env", 
        action="store_true", 
        help="Use environment variable configuration"
    )
    
    # Task file
    parser.add_argument(
        "--tasks", 
        type=str, 
        default="config/tasks.json",
        help="Task configuration file path (default: config/tasks.json)"
    )
    
    # Other options
    parser.add_argument(
        "--skip-env-check",
        action="store_true",
        help="Skip environment check (for debugging)"
    )
    parser.add_argument(
        "--log-level", 
        type=str, 
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Log level (default: INFO)"
    )
    
    parser.add_argument(
        "--dry-run", 
        action="store_true",
        help="Dry run mode - only load and validate configuration, do not execute tasks"
    )
    
    args = parser.parse_args()
    
    try:
        # Load environment variables (if .env file exists)
        if Path(".env").exists():
            load_dotenv()
        
        # Load configuration
        if args.env:
            print("Loading configuration from environment variables...")
            config = BenchmarkConfig.from_env()
        else:
            print(f"Loading configuration from: {args.config}")
            config = BenchmarkConfig.from_file(args.config)
        
        # Create benchmark agent (this creates timestamped output directory)
        agent = BenchmarkAgent(config)
        
        # Setup logging (use actual output directory created by agent)
        logger = setup_logging(str(agent.task_manager.output_dir), args.log_level)
        logger.info("BenchmarkAgent starting...")
        
        # Validate configuration
        config.validate()
        logger.info("Configuration validated successfully")
        
        # Validate task file
        if not Path(args.tasks).exists():
            raise FileNotFoundError(f"Tasks file not found: {args.tasks}")
        
        if args.dry_run:
            logger.info("Dry run mode - configuration and tasks file validated successfully")
            return 0
        
        # Run benchmark
        logger.info(f"Starting benchmark execution with tasks from: {args.tasks}")
        summary = agent.run_benchmark(args.tasks, skip_env_check=args.skip_env_check)
        
        # Output result summary
        logger.info("="*50)
        logger.info("BENCHMARK RESULTS SUMMARY")
        logger.info("="*50)
        logger.info(f"Total tasks: {summary['total_tasks']}")
        logger.info(f"Successful tasks: {summary['successful_tasks']}")
        logger.info(f"Failed tasks: {summary['failed_tasks']}")
        logger.info(f"Success rate: {summary['success_rate']:.2f}%")
        logger.info(f"Results saved in: {agent.task_manager.output_dir}")
        
        # If there are failed tasks, show details
        if summary['failed_tasks'] > 0:
            logger.info("\nFailed tasks:")
            for task_id, details in summary['task_details'].items():
                if not details['success']:
                    logger.info(f"  - {task_id}: {details['error']}")
        
        # Return exit code
        return 0 if summary['failed_tasks'] == 0 else 1
        
    except KeyboardInterrupt:
        print("\nBenchmark interrupted by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        if "--log-level" in sys.argv and sys.argv[sys.argv.index("--log-level") + 1] == "DEBUG":
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())