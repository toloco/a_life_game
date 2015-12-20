from setuptools import setup, find_packages
from codecs import open
from os import path
import game

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()


requirements = [
    "python-Levenshtein",
    "ipdb",
    "redis"
]

setup(
    name='Life',
    version=game.__version__,

    description=long_description,
    long_description=long_description,
    url='https://github.com/toloco/life',
    author='Tolo Palmer',
    author_email='tolopalmer@gmail.com',
    license='MIT',
    keywords='life',
    classifiers=[
        '3 - Alpha',
        # '4 - Beta',
        # '5 - Production/Stable',
        # 'Development Status :: 3 - Alpha',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=requirements,
    tests_require=['nose', 'coveralls'],
    test_suite='nose.collector',

    entry_points={
        'console_scripts': [
            'feedhub-unittest = feedhub.tests:main',
        ],
    },

)
