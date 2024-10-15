#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import pathlib
import sys

NBS_DIR = pathlib.Path(__file__).resolve().parent
REPO_DIR = NBS_DIR.parent
PROJECT_DIR = REPO_DIR / "src"

def init_django(project_name='cfehome'):
    """Run administrative tasks."""
    os.chdir(PROJECT_DIR)
    sys.path.insert(0, str(PROJECT_DIR))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{project_name}.settings")
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

    import django
    django.setup()


if __name__ == "__main__":
    init_django()
