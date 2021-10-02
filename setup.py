
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setuptools


config = {
    'description': "Research Tools for Vote Smart",
    'author': "Johanan Tai",
    'author_email': "jtai.dvlp@gmail.com",
    'version': '0.0.2',
    'install_requires': ['pandas', 'odfpy', 'pg8000','fuzzywuzzy', 'python-Levenshtein', 'tabulate'],
    'url': 'https://github.com/votesmart-projects/vs_library',
    'packages': ['vs_library'],
    'name': 'vs_library'
}

setup(**config)
