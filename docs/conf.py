# -*- coding: utf-8 -*-
#
# celery-haystack documentation build configuration file

# -- General configuration -----------------------------------------------------

# Add any Sphinx extension module names here, as strings.
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'celery-haystack'
copyright = '2011-2024, Jannis Leidel and contributors'

# The version info for the project you're documenting, used in various locations
try:
    from celery_haystack import __version__
    version = '.'.join(__version__.split('.')[:2])  # Short version
    release = __version__  # Full version
except ImportError:
    version = release = 'dev'

# List of patterns, relative to source directory, to ignore when looking for files
exclude_patterns = ['_build']

# The Pygments (syntax highlighting) style to use
pygments_style = 'sphinx'

# -- Options for HTML output ---------------------------------------------------

html_theme = 'default'

# Output file base name for HTML help builder
htmlhelp_basename = 'celery-haystackdoc'

# -- Options for LaTeX output --------------------------------------------------

latex_documents = [
  ('index', 'celery-haystack.tex', 'celery-haystack Documentation',
   'Jannis Leidel', 'manual'),
]

# -- Options for manual page output --------------------------------------------

man_pages = [
    ('index', 'celery-haystack', 'celery-haystack Documentation',
     ['Jannis Leidel'], 1)
]

# -- Intersphinx configuration -------------------------------------------------

# Updated intersphinx mappings
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
    'django': ('https://docs.djangoproject.com/en/stable/', None),
}
