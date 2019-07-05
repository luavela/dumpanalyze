# -*- coding: utf-8 -*-
#
# Test suite runner for dumpanalyze
# Copyright 2017-2019 IPONWEB Ltd. See License Notice in LICENSE
#

from setuptools import sandbox
sandbox.run_setup('setup.py', ['flake8', 'pytest'])
