#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
from setuptools import setup, find_packages
 
import simple_photo_backup
 
setup(
 
    name='simple_photo_backup',
    version=simple_photo_backup.__version__,
 
    packages=find_packages(),
 
    author="Asteroide",
 
    author_email="asteroide__AT__domtombox.net",
 
    description="A very simple photo backup manager.",
 
    long_description=open('README.rst').read(),
 
    install_requires=[
        "exifread",
    ],
 
    include_package_data=True,
 
    url='http://github.com/asteroide/simple_photo_backup',
 
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.4",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: System :: Archiving :: Backup",

    ],
 
    entry_points={
        'console_scripts': [
            'spb = simple_photo_backup.core:run',
        ],
    },
)
