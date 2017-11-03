# -*- coding: utf-8 -*-
#
# This file is a part of the testing suite for dumpanalyze.
#
# Copyright 2017 IPONWEB Ltd.
#

import os

from dumpanalyze.dumpparser import DumpParser
from dumpanalyze.trace import Trace
from dumpanalyze.tracebush import TraceBush
from dumpanalyze.traceforest import TraceForest
from dumpanalyze.abortreason import AbortReason

DATA_DIR = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "dump-files"
)
DUMP_FNAME = os.path.join(DATA_DIR, "test_objects.txt")


def test_parser():
    parser = DumpParser(DUMP_FNAME)
    assert isinstance(parser, DumpParser)

    assert parser.parse() == DumpParser.PARSED_DUMP

    assert isinstance(parser.traces, list)
    assert isinstance(parser.abort_reasons, list)

    assert len(parser.traces) == 3
    assert len(parser.abort_reasons) == 4


def test_traces():
    parser = DumpParser(DUMP_FNAME)
    parser.parse()

    root_trace = parser.traces[0]
    assert isinstance(root_trace, Trace)
    assert root_trace.id == 1
    assert root_trace.parent_id == 0
    assert root_trace.parent_side == 0
    assert root_trace.parent == ""
    assert root_trace.is_root
    assert root_trace.file == "=(command line)"
    assert root_trace.line == 1
    assert root_trace.link_type == "loop"
    assert root_trace.num_bc == 5
    assert root_trace.num_ir == 15
    assert root_trace.num_sn == 7
    assert root_trace.size_mcode == 113

    side_trace = parser.traces[1]
    assert isinstance(side_trace, Trace)
    assert side_trace.id == 2
    assert side_trace.parent_id == 1
    assert side_trace.parent_side == 1
    assert side_trace.parent == "1/1"
    assert not side_trace.is_root
    assert side_trace.file == "=(command line)"
    assert side_trace.line == 1
    assert side_trace.link_type == str(root_trace.id)
    assert side_trace.num_bc == 5
    assert side_trace.num_ir == 8
    assert side_trace.num_sn == 5
    assert side_trace.size_mcode == 127

    stub_trace = parser.traces[2]
    assert isinstance(stub_trace, Trace)
    assert stub_trace.id == 3
    assert stub_trace.parent_id == 2
    assert stub_trace.parent_side == 1
    assert stub_trace.parent == "2/1"
    assert not stub_trace.is_root
    assert stub_trace.file == "=(command line)"
    assert stub_trace.line == 1
    assert stub_trace.link_type == "interpreter"
    assert stub_trace.num_bc == 0
    assert stub_trace.num_ir == 2
    assert stub_trace.num_sn == 2
    assert stub_trace.size_mcode == 79


# Testing bushes and forests withing a single test
def test_trace_grouping():
    parser = DumpParser(DUMP_FNAME)
    parser.parse()

    forest = TraceForest(parser.traces)
    assert isinstance(forest, TraceForest)
    assert isinstance(forest.bushes, dict)
    assert len(forest.bushes) == 1

    bush = forest.bushes[1]
    assert isinstance(bush, TraceBush)
    assert bush.root_id == 1
    assert bush.size == 3
    assert isinstance(bush.traces, list)


def test_abort_reason():
    parser = DumpParser(DUMP_FNAME)
    parser.parse()

    abort_reason = parser.abort_reasons[0]
    assert isinstance(abort_reason, AbortReason)
    assert abort_reason.file == "=(command line)"
    assert abort_reason.line == 1
    assert abort_reason.reason == "NYI: FastFunc print"
