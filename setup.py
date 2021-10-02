
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setuptools


config = {
    'description': "Research Tools for Vote Smart",
    'author': "Johanan Tai",
    'author_email': "jtai.dvlp@gmail.com",
    'version': '0.0.1',
    'install_requires': ['pandas', 'odfpy', 'pg8000','fuzzywuzzy', 'python-Levenshtein', 'tabulate'],
    'packages': ['vs_libary'],
    'name': 'vs_library'
}

setup(**config)
