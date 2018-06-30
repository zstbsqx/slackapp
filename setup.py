# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os
import sys
import io
import re

with io.open('slackapp/__init__.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

setup(
    name="slackapp",
    version=version,
    packages=find_packages(exclude=["tests.*", "tests"]),
    description="slack app integration module",
    long_description="slack app integration module",
    url='http://github.com/zeaphoo/slackapp/',
    author="wei.zhuo",
    author_email="zeaphoo@gmail.com",
    include_package_data=True,
    zip_safe=False,
    license="MIT",
    keywords=("slack", "egg"),
    platforms="any",
    install_requires=['slackclient'],
    entry_points={}
)
