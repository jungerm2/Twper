from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt') as requirements:
    required = requirements.read().splitlines()

setup(
    name='Twper',
    version='0.1.0',
    description='An asynchronous twitter scraper',
    long_description=long_description,
    url='https://github.com/jungerm2/Twper',
    author='Sacha Jungerman',
    author_email='jungerm2@illinois.edu',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='twitter scraper async asynchronous fast non-blocking asyncio',
    packages=find_packages(),
    install_requires=required,
)


# pandoc --from=markdown --to=rst --output=README.rst README.md

