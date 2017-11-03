# -*- coding: utf-8 -*-
#
# A compiled trace.
# This module is a part of the toolkit for processing LuaJIT plain text dumps.
#
# Copyright 2017 IPONWEB Ltd.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

import collections
import re


class Trace:
    # Regular expressions to extract data from trace header lines:
    re_header_start = re.compile(" start (?:((\d+)/(\d+)) )?([^:]+):(\d+)$")
    re_header_mcode = re.compile(" mcode (\d+)$")
    re_header_stop = re.compile(" stop -> (.+)$")

    # Regular expressions to extract data from trace data lines:
    re_data_mcode = re.compile("->(\d+)")

    def __init__(self, trace_id):
        self._id = trace_id
        self._parent_id = 0
        self._parent_side = 0
        self._parent = ""
        self._file = ""
        self._line = 0
        self._link_type = ""
        self._side_exits = collections.defaultdict(lambda: 0)
        self._num_ir = 0
        self._num_sn = 0
        self._size_mcode = 0
        self._bc = []          # List of bytecode dump
        self._ir = []          # List of IR dump
        self._mc = []          # List of machine code dump

    @property
    def id(self):
        return self._id

    @property
    def parent_id(self):
        return self._parent_id

    @property
    def parent_side(self):
        return self._parent_side

    @property
    def parent(self):
        return self._parent

    @property
    def is_root(self):
        return self._parent_id == 0

    @property
    def file(self):
        return self._file

    @property
    def line(self):
        return self._line

    @property
    def link_type(self):
        return self._link_type

    @property
    def side_exits(self):
        return self._side_exits

    @property
    def num_bc(self):
        return len(self._bc)

    @property
    def num_ir(self):
        return self._num_ir

    @property
    def num_sn(self):
        return self._num_sn

    @property
    def size_mcode(self):
        return self._size_mcode

    @property
    def bc(self):
        return self._bc

    @property
    def ir(self):
        return self._ir

    @property
    def mc(self):
        return self._mc

    # Process `line` which is logically a header signalling about entering
    # a new `state` while reading the stream of data.
    def process_header(self, state, line):
        action = "_process_header_" + state
        return getattr(self, action)(line)

    # Process a `line` of data while the parser is in the given `state`.
    def process_data(self, state, line):
        action = "_process_data_" + state
        return getattr(self, action)(line)

    #
    # Per-state terminal handlers for header lines
    #

    def _process_header_start(self, line):
        match = self.re_header_start.search(line)

        if match.group(1) is not None:
            self._parent = match.group(1)

        if match.group(2) is not None:
            self._parent_id = int(match.group(2))

        if match.group(3) is not None:
            self._parent_side = int(match.group(3))

        self._file = match.group(4)
        self._line = int(match.group(5))

    def _process_header_IR(self, line):
        pass

    def _process_header_mcode(self, line):
        match = self.re_header_mcode.search(line)
        self._size_mcode = int(match.group(1))

    def _process_header_stop(self, line):
        match = self.re_header_stop.search(line)
        self._link_type = match.group(1)

    def _process_header_exit(self, line):
        pass

    def _process_header_abort(self, line):
        pass

    def _process_header_flush(self, line):
        pass

    #
    # Per-state terminal handlers for data lines
    #

    def _process_data_start(self, line):
        self._bc.append(line)

    def _process_data_IR(self, line):
        self._ir.append(line)
        if "SNAP" in line:
            self._num_sn += 1
        else:
            self._num_ir += 1

    def _process_data_mcode(self, line):
        self._mc.append(line)
        match = self.re_data_mcode.search(line)

        if not match or match.group(1) is None:
            return

        # We record only side exits actually preserved in mcode
        self._side_exits[int(match.group(1))] += 1

    def _process_data_stop(self, line):
        pass

    def _process_data_exit(self, line):
        pass

    def _process_data_abort(self, line):
        pass

    def _process_data_flush(self, line):
        pass
