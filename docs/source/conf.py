import toml

with open("../../pyproject.toml") as in_file:
    pyproject = toml.load(in_file)

project = pyproject['project']['name']
author = pyproject['project']['authors'][0]['name']
copyright = "2023, " + author
version = pyproject['project']['version']


extensions = [
    'autoapi.extension',
]

templates_path = ['_templates']
exclude_patterns = []


html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']


autoapi_options = [
    'members',
    'undoc-members',
    'show-inheritance',
    'show-module-summary',
    'special-members',
    'imported-members',
]
autoapi_dirs = ['../../src/']
