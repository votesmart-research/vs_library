#!/usr/bin/env python3
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setuptools

EGG = '#egg='
install_requires = []

with open('requirements.txt') as f:
    for line in f.read().splitlines():
        if line.startswith('git+'):
            if EGG not in line:
                raise Exception('egg specification is required.')
            package_name = line[line.find(EGG) + len(EGG):]
            dependency_link = line[:line.find(EGG)]
            install_requires.append(f"{package_name} @ {dependency_link}")
        else:
            install_requires.append(line)

config = {
    'description': "Research Tools for Vote Smart",
    'author': "Johanan Tai",
    'author_email': "jtai.dvlp@gmail.com",
    'version': '0.0.3',
    'install_requires': install_requires,
    'url': 'https://github.com/votesmart-projects/vs_library',
    'packages': ['vs_library', 'vs_library.cli', 'vs_library.database', 'vs_library.tools', 'vs_library.vsdb'],
    'name': 'vs_library'
}

setup(**config)
