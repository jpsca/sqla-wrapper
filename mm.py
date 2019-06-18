#!/usr/bin/env python
"""
COPY THIS FILE TO YOUR PROJECT.
---------
This file generates all the necessary files for packaging for the project.
Read more about it at https://github.com/jpscaletti/mastermold/
"""
from pathlib import Path


data = {
    "title": "SQLA-wrapper",
    "name": "sqla_wrapper",
    "pypi_name": "sqla-wrapper",
    "version": "2.0.2",
    "author": "Juan-Pablo Scaletti",
    "author_email": "juanpablo@jpscaletti.com",
    "description": "A framework-independent wrapper for SQLAlchemy that makes it really easy to use.",
    "copyright": "2013",
    "repo_name": "jpscaletti/sqla-wrapper",
    "home_url": "https://jpscaletti.com/sqla-wrapper",
    "project_urls": {
        "Documentation": "http://sqlawrapper.lucuma.co",
    },
    "development_status": "5 - Production/Stable",
    "minimal_python": 3.6,
    "install_requires": [
        "inflection",
        "sqlalchemy ~= 1.0",
    ],
    "testing_requires": [
        "pytest",
        "mock",
    ],
    "development_requires": [
        "pytest-cov",
        "tox",
        "sphinx",
    ],
    "entry_points": "",

    "coverage_omit": [
    ],

    "has_docs": False,
    "google_analytics": "UA-XXXXXXXX-X",
    "docs_nav": [],
}

exclude = [
    "copier.yml",
    "README.md",
    ".git",
    ".git/*",
    ".venv",
    ".venv/*",

    "LICENSE.txt",
    "CONTRIBUTING.md",
    "docs",
    "docs/*",
]


def do_the_thing():
    import copier
    from ruamel.yaml import YAML

    def save_current_nav():
        yaml = YAML()
        mkdocs_path = Path("docs") / "mkdocs.yml"
        if not mkdocs_path.exists():
            return
        mkdocs = yaml.load(mkdocs_path)
        data["docs_nav"] = mkdocs.get("nav")

    if data["has_docs"]:
        save_current_nav()

    copier.copy(
        # "gh:jpscaletti/mastermold.git",
        "../mastermold",  # Path to the local copy of Master Mold
        ".",
        data=data,
        exclude=exclude,
        force=True,
        cleanup_on_error=False
    )


if __name__ == "__main__":
    do_the_thing()
