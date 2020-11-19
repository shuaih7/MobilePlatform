#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on 04.20.2020
Updated on 04.20.2020

Author: 212780558
"""

from setuptools import setup, find_packages
import os


with open("README.md") as f:
    readme = f.read()

with open("requirements.txt") as f:
    requirements = f.read().split("\n")
    
    
setup(
    name="MobilePlatform",
    version="1.0",
    description="HMI for the Cleanliness Sensor Project",
    long_description=readme,
    author="212780558",
    author_email="Shuai1.Hao@ge.com",
    url="https://github.build.ge.com/RDC",
    license="RDC License",
    entry_points={'console_scripts': ['MobilePlatform = MobilePlatform.main:main', ]},
    classifiers=["Programming Language :: Python :: 3.7", ],
    packages=find_packages(),
    package_dir={'MobilePlatform': ''},
    python_requires=">=3.6",
    install_requires=requirements,
    zip_safe=False,
)