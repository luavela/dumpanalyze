#!/bin/bash
#
# Test suite runner for dumpanalyze
# Copyright 2017 IPONWEB Ltd. See License Notice in LICENSE
#

# Exit on error
set -e

echo "[$(date +%Y%m%dT%H%M%S)] ${USER}@$(hostname) :: $(2>&1 /usr/bin/env python3 --version)"
echo

find . -name '*.pyc' -exec rm {} \;

/usr/bin/env python3 -m flake8 dumpanalyze tests

PYTHONPATH=${PWD} /usr/bin/env python3 -m pytest -v $@ tests
