#!/usr/bin/env python3
"""
MgmtSays Startup Script

This script builds the frontend and starts the backend server.
Usage: uv run start.py [options]

Options:
    --skip-build    Skip frontend build (use existing build)
    --dev           Run in development mode with hot reload
    --port PORT     Backend port (default: 8000)
    --host HOST     Backend host (default: 0.0.0.0)
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.resolve()
FRONTEND_DIR = PROJECT_ROOT / "frontend"
BACKEND_DIR = PROJECT_ROOT / "backend"


def run_command(cmd: list[str], cwd: Path, description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}")
    print(f"  Running: {' '.join(cmd)}")
    print(f"  Directory: {cwd}")
    print()

    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            shell=(os.name == "nt"),  # Use shell on Windows
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Error: Command failed with exit code {e.returncode}")
        return False
    except FileNotFoundError as e:
        print(f"  ❌ Error: Command not found - {e}")
        return False


def check_uv_installed() -> bool:
    """Check if uv is installed."""
    if shutil.which("uv"):
        try:
            result = subprocess.run(
                ["uv", "--version"],
                capture_output=True,
                text=True,
                shell=(os.name == "nt"),
            )
            if result.returncode == 0:
                print(f"  ✓ uv version: {result.stdout.strip()}")
                return True
        except FileNotFoundError:
            pass
    print("  ❌ uv is not installed.")
    print("  Install with: curl -LsSf https://astral.sh/uv/install.sh | sh")
    print("  Or on Windows: powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\"")
    return False


def check_node_installed() -> bool:
    """Check if Node.js is installed."""
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            shell=(os.name == "nt"),
        )
        if result.returncode == 0:
            print(f"  ✓ Node.js version: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    print("  ❌ Node.js is not installed. Please install Node.js first.")
    return False


def sync_python_deps() -> bool:
    """Sync Python dependencies using uv."""
    return run_command(
        ["uv", "sync"],
        PROJECT_ROOT,
        "Syncing Python dependencies with uv",
    )


def install_frontend_deps() -> bool:
    """Install frontend dependencies."""
    package_lock = FRONTEND_DIR / "package-lock.json"
    node_modules = FRONTEND_DIR / "node_modules"

    # Use npm ci if lock file exists and node_modules doesn't
    if package_lock.exists() and not node_modules.exists():
        cmd = ["npm", "ci"]
    else:
        cmd = ["npm", "install"]

    return run_command(cmd, FRONTEND_DIR, "Installing frontend dependencies")


def build_frontend() -> bool:
    """Build the frontend for production."""
    return run_command(
        ["npm", "run", "build"],
        FRONTEND_DIR,
        "Building frontend for production",
    )


def start_backend(host: str, port: int, dev_mode: bool) -> None:
    """Start the backend server."""
    print(f"\n{'='*60}")
    print("  Starting Backend Server")
    print(f"{'='*60}")

    if dev_mode:
        print("  Mode: Development (with hot reload)")
        print(f"  URL: http://{host}:{port}")
        print(f"  Docs: http://{host}:{port}/docs")
        print()

        # Use uv run for dev mode with reload
        cmd = [
            "uv", "run", "uvicorn",
            "backend.src.main:app",
            "--host", host,
            "--port", str(port),
            "--reload",
            "--reload-dir", "backend/src",
        ]
        subprocess.run(cmd, cwd=PROJECT_ROOT, shell=(os.name == "nt"))
    else:
        print("  Mode: Production")
        print(f"  URL: http://{host}:{port}")
        print()

        # Use uv run for production
        cmd = [
            "uv", "run", "uvicorn",
            "backend.src.main:app",
            "--host", host,
            "--port", str(port),
            "--log-level", "info",
        ]
        subprocess.run(cmd, cwd=PROJECT_ROOT, shell=(os.name == "nt"))


def main():
    parser = argparse.ArgumentParser(
        description="Build frontend and start MgmtSays backend server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run start.py                    # Build frontend and start backend
  uv run start.py --dev              # Development mode with hot reload
  uv run start.py --skip-build       # Skip frontend build
  uv run start.py --port 3000        # Use custom port
        """,
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip frontend build step",
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Run in development mode with hot reload",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Backend server port (default: 8000)",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Backend server host (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--skip-deps",
        action="store_true",
        help="Skip dependency sync",
    )

    args = parser.parse_args()

    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║            MgmtSays - Startup Script                     ║")
    print("║     Management Disclosure Intelligence Platform          ║")
    print("╚══════════════════════════════════════════════════════════╝")

    # Check prerequisites
    print("\n  Checking prerequisites...")

    if not check_uv_installed():
        sys.exit(1)

    if not args.skip_build:
        if not check_node_installed():
            sys.exit(1)

    # Sync Python dependencies with uv
    if not args.skip_deps:
        if not sync_python_deps():
            print("\n  ❌ Failed to sync Python dependencies")
            sys.exit(1)
        print("  ✓ Python dependencies synced")

    # Frontend build
    if not args.skip_build:
        # Install dependencies
        if not args.skip_deps:
            if not install_frontend_deps():
                print("\n  ❌ Failed to install frontend dependencies")
                sys.exit(1)

        # Build frontend
        if not build_frontend():
            print("\n  ❌ Failed to build frontend")
            sys.exit(1)

        print("\n  ✓ Frontend built successfully!")
    else:
        print("\n  ⏭ Skipping frontend build")

    # Start backend
    try:
        start_backend(args.host, args.port, args.dev)
    except KeyboardInterrupt:
        print("\n\n  👋 Server stopped. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
