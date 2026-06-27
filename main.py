#!/usr/bin/env python
"""
Main Entry Point for the AI Career Coach Agent.
Runs the interactive Command Line Interface.
"""

import sys
from ui.cli import CareerCoachCLI

def main():
    try:
        cli = CareerCoachCLI()
        cli.start()
    except KeyboardInterrupt:
        print("\n\nSession terminated by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn error occurred while launching the Career Coach: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
