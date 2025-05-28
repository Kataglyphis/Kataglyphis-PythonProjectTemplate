# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath("../../"))

version: str = Path("../../VERSION.txt").read_text().strip()
project = "kataglyphispythonpackage"
copyright = "2025, Jonas Heinle"
author = "Jonas Heinle"
release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",  # For Google and NumPy style docstrings
    "sphinx.ext.viewcode",  # To include links to the source code
    "myst_parser",  # adding .md files
]

templates_path = ["_templates"]
exclude_patterns = []

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "private-members": True,
    "special-members": True,
    # 'inherited-members': True,
    # 'show-inheritance': True,
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# Enable the processing of Markdown files
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
