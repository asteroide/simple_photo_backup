#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
from setuptools import setup, find_packages
import distutils.cmd
import distutils.log
import os
import stat

from simple_photo_backup import __version__


class UniqueFile(distutils.cmd.Command):
    """A custom command to create a unique python file."""

    description = 'create a unique python file'
    main_file = os.path.join("simple_photo_backup", "core.py")
    user_options = [
        ("destination=", "d", "destination directory"),
        ("output-name=", "o", "output name"),
    ]

    def initialize_options(self):
        """Set default values for options."""
        self.destination = "dists"
        self.output_name = "spb.py"

    def finalize_options(self):
        """Post-process options."""
        try:
            os.mkdir(self.destination)
        except OSError:
            pass

    def run(self):
        """Run command."""
        try:
            os.chmod(os.path.join(self.destination, self.output_name), stat.S_IEXEC | stat.S_IREAD | stat.S_IWRITE)
            os.remove(os.path.join(self.destination, self.output_name))
        except OSError:
            pass
        ofile = open(os.path.join(self.destination, self.output_name), "w")

        for line in open(os.path.join(os.getcwd(), self.main_file)).readlines():
            if "DEFAULT_OUT_DIR = " in line:
                line = "DEFAULT_OUT_DIR = '.'\n"
            ofile.write(line)
        ofile.close()
        os.chmod(os.path.join(self.destination, self.output_name), stat.S_IEXEC | stat.S_IREAD)


setup(
 
    name='simple_photo_backup',
    version=__version__,
 
    packages=find_packages(),
 
    author="Asteroide",
 
    author_email="asteroide__AT__domtombox.net",
 
    description="A very simple photo backup manager.",
 
    long_description=open('README.rst').read(),
 
    install_requires=[
        "Image",
        "exifread"
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
    cmdclass={
        'unique_file': UniqueFile,
    },
)
