#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This package allows users to get photos from a directory (eg. from a camera) and send them to a backup directory.
"""

__version__ = "0.1.2"


try:
    from simple_photo_backup.core import run
except ImportError:
    pass
