# -*- coding: utf-8 -*-
#
# Trace list view.
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

import csv


class ViewTraces:

    CSV_HEADER = [
        "ID", "PARENT", "LINK_TYPE", "NUM_BC", "NUM_IR", "NUM_SN", "SIZE_MC",
    ]

    def __init__(self, fmt):
        self._fmt = fmt

    def render(self, fname, traces):
        if self._fmt == "csv":
            self._render_csv(fname, traces)
        else:
            raise Exception("Unknown format")

    def _render_csv(self, fname, traces):
        with open(fname, "w", newline="") as out:
            writer = csv.writer(
                out, delimiter=",", quoting=csv.QUOTE_MINIMAL
            )
            writer.writerow(self.CSV_HEADER)
            for trace in traces:
                writer.writerow([
                    trace.id,
                    trace.parent_id,
                    trace.link_type,
                    trace.num_bc,
                    trace.num_ir,
                    trace.num_sn,
                    trace.size_mcode,
                ])
