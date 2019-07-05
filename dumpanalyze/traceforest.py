# -*- coding: utf-8 -*-
#
# A forest of trace bushes.
# This module is a part of the toolkit for processing LuaJIT plain text dumps.
#
# Copyright 2017-2019 IPONWEB Ltd.
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

from dumpanalyze.tracebush import TraceBush


class TraceForest:

    def __init__(self, traces):
        forest = {}
        roots = {}

        for trace in traces:
            root_id = None
            if trace.is_root:
                root_id = trace.id
                forest[root_id] = TraceBush(trace)
            else:
                root_id = roots[trace.parent_id]
                forest[root_id].append(trace)
            roots[trace.id] = root_id

        self._bushes = forest

    @property
    def bushes(self):
        return self._bushes
