# -*- coding: utf-8 -*-
#
# Line-by-line parser of a LuaJIT plain text dump.
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

import sys
import re

from dumpanalyze.trace import Trace
from dumpanalyze.abortreason import AbortReason


class DumpParser:
    # Internal parser states while parsing multiple states
    # within a single trace generation:
    PARSER_INIT = ""
    PARSER_START = "start"
    PARSER_IR = "IR"
    PARSER_MCODE = "mcode"
    PARSER_STOP = "stop"
    PARSER_EXIT = "exit"
    PARSER_ABORT = "abort"
    PARSER_FLUSH = "flush"

    # External parser states:
    PARSED_GENERATION = 1  # Parsed generation, but there are more in the dump
    PARSED_DUMP = 2        # Parsed generation and reached the end of the dump

    ASSERTABLE_STATES = [
        PARSER_IR, PARSER_MCODE, PARSER_STOP, PARSER_ABORT
    ]

    # Regular expression to detect a new logical portion of
    # trace-related data or a global trace flush:
    re_trace_header = re.compile(r"^---- TRACE (?:(\d+ )?(\S+))")

    def __init__(self, dump):
        # Errors are ignored because non-UTF-8 string values
        # may appear in the dumps.
        self._dump_f = open(dump, "r", errors="ignore")

        self._init_parser()

    def __del__(self):
        self._dump_f.close()

    @property
    def traces(self):
        return self._traces

    @property
    def abort_reasons(self):
        return self._abort_reasons

    def parse(self):
        self._init_parser()

        for line in self._dump_f:
            self._line += 1
            self._parse_line(line)
            if self._state == self.PARSER_FLUSH:
                return self.PARSED_GENERATION

        return self.PARSED_DUMP

    def _init_parser(self):
        self._line = 0
        self._state = self.PARSER_INIT
        self._trace = None
        self._traces = []
        self._abort_reasons = []

    def _parse_line(self, line):
        if line == "\n":
            return

        match = self.re_trace_header.match(line)
        if match:
            trace_id = int(match.group(1) or 0)
            self._parse_header_line(line, match.group(2), trace_id)
        else:
            self._trace.process_data(self._state, line)

    def _parse_header_line(self, line, state, trace_id):
        self._state = state

        if state in self.ASSERTABLE_STATES and trace_id != self._trace.id:
            sys.exit(
                "Line {}, in state={}: Expected trace ID {}, got {}"
                .format(self._line, self._state, self._trace.id, trace_id)
            )

        if state == self.PARSER_ABORT:
            self._abort_reasons.append(AbortReason(line))
            return

        if state == self.PARSER_START:
            self._trace = Trace(trace_id)

        self._trace.process_header(state, line)

        if state == self.PARSER_STOP:
            self._traces.append(self._trace)
