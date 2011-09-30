#!/usr/bin/env python
from setuptools import setup, find_packages

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules'
]

KEYWORDS = 'mailchimp api wrapper'


setup(name = 'cheeta',
    version = '1.0.0',
    description = """MailChimp API wrapper for Python.""",
    author = 'starenka',
    url = "https://github.com/starenka/cheeta",
    packages = find_packages(),
    download_url = "https://github.com/starenka/cheeta",
    classifiers = CLASSIFIERS,
    keywords = KEYWORDS,
    zip_safe = True,
    install_requires = ['distribute','simplejson','mailsnake>=1.3.0',],
    dependency_links = ['git+git://github.com/leftium/mailsnake#egg=mailsnake-1.3.0',]
)

