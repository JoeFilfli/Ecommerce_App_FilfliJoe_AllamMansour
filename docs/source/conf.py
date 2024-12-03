# conf.py

import os
import sys
sys.path.insert(0, os.path.abspath('../../'))  # Adjust the path based on your project structure

# -- Project information -----------------------------------------------------

project = 'Ecommerce_FilfliJoe_AllamMansour'
author = 'Your Name'
release = '1.0'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',                  # Core Sphinx extension for automatic documentation
    'sphinx_autodoc_typehints',            # Integrates type hints into documentation
    'sphinx.ext.napoleon',                 # Supports Google and NumPy docstring styles
    'sphinx.ext.viewcode',                 # Adds links to the source code
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

html_theme = 'alabaster'  # You can choose other themes like 'sphinx_rtd_theme'
html_static_path = ['_static']

# Enable automatic generation of documentation from docstrings
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'private-members': False,
    'special-members': '__init__',
    'inherited-members': True,
    'show-inheritance': True,
}


