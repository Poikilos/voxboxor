#!/usr/bin/env python3
import os
import sys

REPO_DIR = os.path.dirname(__file__)

if __name__ == "__main__":
    sys.path.insert(0, REPO_DIR)

from bakedin.mainmenu.tab_online import main

if __name__ == "__main__":
    sys.exit(main())
