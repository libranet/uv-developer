"""Sphinx configuration."""

project = "uv-developer"
author = "Wouter Vanden Hove"
copyright = ", Wouter Vanden Hove"  # noqa: A001 # pylint: disable=redefined-builtin
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "sphinx_rtd_theme"
