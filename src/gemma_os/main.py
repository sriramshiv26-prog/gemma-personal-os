#!/usr/bin/env python3
"""
Gemma 4 Personal OS - Main CLI Entry Point

Usage:
    python3 -m gemma_os.main --task "describe your task" [options]
"""

import argparse
import sys
import json
from pathlib import Path

from .core import Config, ModelRouter, Database


def setup_parser():
    """Setup command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="Gemma 4 Personal OS - Local AI Workstation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Health check
  python3 -m gemma_os.main --health

  # Test model inference
  python3 -m gemma_os.main --test-inference

  # Run a task (simple)
  python3 -m gemma_os.main --task "What is machine learning?"

  # Run a task (with SKILL)
  python3 -m gemma_os.main --task "Audit this code for security" --skill security-auditing

  # Show configuration
  python3 -m gemma_os.main --config

  # Database statistics
  python3 -m gemma_os.main --stats
        """,
    )

    # Task execution
    parser.add_argument(
        "--task",
        type=str,
        help="Task description to execute",
    )

    parser.add_argument(
        "--skill",
        type=str,
        help="SKILL.md to load for context",
    )

    parser.add_argument(
        "--input-file",
        type=str,
        help="Input file (code, document, etc.)",
    )

    parser.add_argument(
        "--output-file",
        type=str,
        help="Output file for results",
    )

    # System checks
    parser.add_argument(
        "--health",
        action="store_true",
        help="Check system health (models, connectivity)",
    )

    parser.add_argument(
        "--test-inference",
        action="store_true",
        help="Test model inference",
    )

    parser.add_argument(
        "--config",
        action="store_true",
        help="Show current configuration",
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show database statistics",
    )

    # Options
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Debug mode",
    )

    parser.add_argument(
        "--offline",
        action="store_true",
        help="Offline mode (no external APIs)",
    )

    return parser


def print_health(config: Config):
    """Print system health check"""
    print("\n" + "=" * 60)
    print("SYSTEM HEALTH CHECK")
    print("=" * 60)

    router = ModelRouter(config=config)
    health = router.health_check()

    print(f"\nStatus: {health['status'].upper()}")
    print(f"\nModels:")
    print(f"  Expert ({config.ollama.model_expert}): {'✓' if health['expert_model']['available'] else '✗'}")
    print(f"  Fast ({config.ollama.model_fast}): {'✓' if health['fast_model']['available'] else '✗'}")

    if health['status'] == 'healthy':
        print("\n✓ System is healthy")
    else:
        print(f"\n✗ System issues detected: {health.get('error', 'Unknown')}")

    print("=" * 60 + "\n")


def print_config(config: Config):
    """Print current configuration"""
    print("\n" + "=" * 60)
    print("CONFIGURATION")
    print("=" * 60)

    summary = config.summary()
    print(json.dumps(summary, indent=2))

    print("=" * 60 + "\n")


def print_stats():
    """Print database statistics"""
    print("\n" + "=" * 60)
    print("DATABASE STATISTICS")
    print("=" * 60)

    config = Config()
    db = Database(config=config)
    db.init()

    stats = db.stats()
    db.close()

    print(f"\nTotal tasks: {stats['total_tasks']}")
    print(f"Completed: {stats['completed_tasks']}")
    print(f"Success rate: {stats['success_rate']:.1f}%")
    print(f"Total execution time: {stats['total_execution_time_ms']}ms")
    print(f"Total tokens used: {stats['total_tokens_used']}")

    print("=" * 60 + "\n")


def test_inference(config: Config):
    """Test model inference"""
    print("\n" + "=" * 60)
    print("INFERENCE TEST")
    print("=" * 60)

    router = ModelRouter(config=config)

    print(f"\nTesting {config.ollama.model_fast}...")
    result = router.test_inference(model=config.ollama.model_fast)

    if result['status'] == 'success':
        print(f"✓ Success")
        print(f"  Inference time: {result['inference_time_ms']}ms")
        print(f"  Tokens/sec: {result['tokens_per_second']:.1f}")
    else:
        print(f"✗ Failed: {result.get('error', 'Unknown error')}")

    print("=" * 60 + "\n")


def main():
    """Main entry point"""
    parser = setup_parser()
    args = parser.parse_args()

    # Initialize configuration
    config = Config()

    if not config.validate():
        sys.exit(1)

    # Handle system checks
    if args.health:
        print_health(config)
        return

    if args.test_inference:
        test_inference(config)
        return

    if args.config:
        print_config(config)
        return

    if args.stats:
        print_stats()
        return

    # Handle task execution
    if args.task:
        print(f"\n{'=' * 60}")
        print(f"EXECUTING TASK")
        print(f"{'=' * 60}")
        print(f"\nTask: {args.task}")

        if args.skill:
            print(f"Skill: {args.skill}")

        if args.offline:
            print("Mode: OFFLINE (no external APIs)")

        # Route task
        router = ModelRouter(config=config)
        model, analysis = router.select_model(args.task)

        print(f"\nModel selected: {model}")
        print(f"Reasoning: {analysis.reasoning}")
        print(f"Complexity: {analysis.reasoning_depth}")

        print(f"\nEstimated output tokens: {analysis.estimated_output_tokens}")
        print(f"\n{'=' * 60}\n")

        print("✓ Task setup complete")
        print("Note: Full execution requires CrewAI orchestration")
        return

    # No action specified
    if len(sys.argv) == 1:
        parser.print_help()
        return

    parser.print_help()


if __name__ == "__main__":
    main()
