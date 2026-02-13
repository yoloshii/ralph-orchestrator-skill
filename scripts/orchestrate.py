#!/usr/bin/env python3
"""
Ralph Orchestrator - Bridge between Claude Code and ralph-orchestrator CLI.

Usage:
    python orchestrate.py --check
    python orchestrate.py --plan "Add authentication" --run
    python orchestrate.py --generate --title "Feature" --tasks "task1" "task2" --run
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def validate_environment() -> tuple[bool, list[str]]:
    """Validate that ralph and git are available."""
    errors = []

    # Check ralph CLI
    if not shutil.which("ralph"):
        errors.append("ralph CLI not found. Install: npm install -g @ralph-orchestrator/ralph-cli")

    # Check git repository
    git_dir = Path(".git")
    if not git_dir.exists():
        errors.append("Not a git repository. Run: git init && git add . && git commit -m 'init'")
    else:
        # Check for commits
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            errors.append("No git commits. Run: git add . && git commit -m 'Initial commit'")

    return len(errors) == 0, errors


def check_existing_files() -> dict:
    """Check for existing ralph files."""
    return {
        "prompt_exists": Path("PROMPT.md").exists(),
        "config_exists": Path("ralph.yml").exists() or Path(".ralph/config.yml").exists(),
        "specs_exists": Path("specs").exists() or Path(".ralph/specs").exists(),
    }


def generate_prompt(
    title: str,
    tasks: List[str],
    context: Optional[str] = None,
    dry_run: bool = False
) -> str:
    """Generate PROMPT.md content."""

    task_list = "\n".join(f"- [ ] {task}" for task in tasks)

    content = f"""# {title}

## Objective
Implement the following feature/changes as specified.

## Tasks
{task_list}

"""

    if context:
        content += f"""## Context
{context}

"""

    content += """## Constraints
- Follow existing code patterns in the codebase
- Run tests after changes
- Commit after each completed task
- Use meaningful commit messages

## Acceptance Criteria
- All tasks completed
- Tests passing
- No linting errors
- Code follows project conventions
"""

    if dry_run:
        print("=== DRY RUN: PROMPT.md content ===")
        print(content)
        print("=== END DRY RUN ===")
        return content

    # Write PROMPT.md
    prompt_path = Path("PROMPT.md")
    if prompt_path.exists():
        print(f"Warning: PROMPT.md already exists, overwriting...")

    prompt_path.write_text(content)
    print(f"Generated: {prompt_path.absolute()}")

    return content


def run_plan(description: str, dry_run: bool = False) -> int:
    """Run ralph plan for interactive PDD session."""

    if dry_run:
        print(f"=== DRY RUN: Would run ===")
        print(f"ralph plan \"{description}\"")
        return 0

    print(f"Starting PDD planning session...")
    print(f"Description: {description}")
    print("-" * 50)

    result = subprocess.run(
        ["ralph", "plan", description],
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr
    )

    return result.returncode


def run_ralph(
    max_iterations: int = 50,
    backend: str = "claude",
    dry_run: bool = False
) -> int:
    """Execute ralph run."""

    cmd = [
        "ralph", "run",
        "-a",  # autonomous mode (headless, no TUI)
        "--max-iterations", str(max_iterations),
        "-b", backend
    ]

    if dry_run:
        print(f"=== DRY RUN: Would run ===")
        print(" ".join(cmd))
        return 0

    # Check PROMPT.md exists
    if not Path("PROMPT.md").exists():
        print("Error: PROMPT.md not found. Run --plan or --generate first.")
        return 1

    print(f"Starting ralph orchestration loop...")
    print(f"Max iterations: {max_iterations}")
    print(f"Backend: {backend}")
    print("-" * 50)

    result = subprocess.run(
        cmd,
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr
    )

    return result.returncode


def report_results(exit_code: int) -> None:
    """Report execution results based on exit code."""

    print("\n" + "=" * 50)

    if exit_code == 0:
        print("SUCCESS: LOOP_COMPLETE - All tasks finished")
        print("Check git log for commits made during execution.")
    elif exit_code == 1:
        print("FAILURE: Execution failed")
        print("Check .ralph/ directory for logs and diagnostics.")
        print("You may resume with: ralph run --continue")
    elif exit_code == 2:
        print("LIMIT: Iteration or time limit exceeded")
        print("Partial progress may have been made.")
        print("Resume with: ralph run --continue")
    elif exit_code == 130:
        print("INTERRUPTED: User cancelled execution")
        print("Resume with: ralph run --continue")
    else:
        print(f"UNKNOWN: Exit code {exit_code}")

    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(
        description="Ralph Orchestrator - Bridge Claude Code to ralph-orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --check
  %(prog)s --plan "Add authentication" --run
  %(prog)s --generate --title "Feature" --tasks "task1" "task2" --run
  %(prog)s --run --max-iterations 100
        """
    )

    # Validation
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate environment (ralph, git, etc.)"
    )

    # Planning
    parser.add_argument(
        "--plan",
        metavar="DESCRIPTION",
        help="Run PDD planning session with this description"
    )

    # Generation
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate PROMPT.md from --title and --tasks"
    )
    parser.add_argument(
        "--title",
        help="Title for generated PROMPT.md"
    )
    parser.add_argument(
        "--tasks",
        nargs="+",
        help="Task list for generated PROMPT.md"
    )
    parser.add_argument(
        "--context",
        help="Additional context for PROMPT.md"
    )

    # Execution
    parser.add_argument(
        "--run",
        action="store_true",
        help="Execute ralph run after plan/generate"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=50,
        help="Iteration limit (default: 50)"
    )
    parser.add_argument(
        "--backend",
        default="claude",
        help="Backend to use (default: claude)"
    )

    # Options
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without executing"
    )

    args = parser.parse_args()

    # Handle --check
    if args.check:
        print("Validating environment...")
        valid, errors = validate_environment()

        if valid:
            print("Environment OK")
            files = check_existing_files()
            print(f"  PROMPT.md exists: {files['prompt_exists']}")
            print(f"  Config exists: {files['config_exists']}")
            print(f"  Specs exist: {files['specs_exists']}")
            return 0
        else:
            print("Environment validation failed:")
            for error in errors:
                print(f"  - {error}")
            return 1

    # Handle --generate
    if args.generate:
        if not args.title:
            print("Error: --generate requires --title")
            return 1
        if not args.tasks:
            print("Error: --generate requires --tasks")
            return 1

        generate_prompt(
            title=args.title,
            tasks=args.tasks,
            context=args.context,
            dry_run=args.dry_run
        )

    # Handle --plan
    if args.plan:
        exit_code = run_plan(args.plan, dry_run=args.dry_run)
        if exit_code != 0 and not args.dry_run:
            print(f"Planning failed with exit code {exit_code}")
            return exit_code

    # Handle --run
    if args.run:
        # Validate before running
        valid, errors = validate_environment()
        if not valid:
            print("Cannot run - environment validation failed:")
            for error in errors:
                print(f"  - {error}")
            return 1

        exit_code = run_ralph(
            max_iterations=args.max_iterations,
            backend=args.backend,
            dry_run=args.dry_run
        )

        if not args.dry_run:
            report_results(exit_code)

        return exit_code

    # No action specified
    if not any([args.check, args.generate, args.plan, args.run]):
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
