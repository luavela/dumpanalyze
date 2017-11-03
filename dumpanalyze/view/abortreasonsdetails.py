# -*- coding: utf-8 -*-
#
# Abort reasons detailed view.
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


class ViewAbortReasonsDetails:

    def __init__(self, fmt):
        self._fmt = fmt

    def render(self, fname, abort_reasons):
        if self._fmt == "txt":
            self._render_txt(fname, abort_reasons)
        else:
            raise Exception("Unknown format")

    def _render_txt(self, fname, abort_reasons):
        files = collections.defaultdict(
            lambda: collections.defaultdict(
                lambda: collections.defaultdict(
                    lambda: 0
                )
            )
        )

        for ar in abort_reasons:
            files[ar.file][ar.line][ar.reason] += 1

        with open(fname, 'w', newline='') as out:
            names = sorted(files.keys())
            for name in names:
                out.write("{}:\n".format(name))
                lines = sorted(files[name].keys())
                for line in lines:
                    out.write("\tline {}:\n".format(line))
                    reasons = sorted(files[name][line].keys())
                    for reason in reasons:
                        out.write("\t\t{}: {}\n".format(
                            reason, files[name][line][reason]
                        ))
