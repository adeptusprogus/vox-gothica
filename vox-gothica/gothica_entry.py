#!/usr/bin/env python3
"""PyInstaller / release entry point (absolute imports only)."""
import sys

from gothica.cli import main

if __name__ == "__main__":
    sys.exit(main())
