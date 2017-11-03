# -*- coding: utf-8 -*-
#
# This file is a part of the testing suite for dumpanalyze.
#
# Copyright 2017 IPONWEB Ltd.
#

import sys
import os
import subprocess
import shutil
import tempfile

CLI_NAME = "dumpanalyze"
DATA_DIR = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "dump-files"
)
DUMP_FNAME = "test_cli.txt"
DUMP_FPATH = os.path.join(DATA_DIR, DUMP_FNAME)


def _prepare_cli_run(params):
    params.insert(0, sys.executable)
    command = " ".join(params)
    return subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )


def test_help():
    process = _prepare_cli_run([CLI_NAME, "-h"])
    out, err = process.communicate()
    assert process.returncode == 0
    assert " --help " in out
    assert " --dump " in out
    assert " --out-dir " in out


def test_bad_dump_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        assert not os.path.isfile(tmpdir)
        process = _prepare_cli_run([CLI_NAME, "--dump", tmpdir])
        out, err = process.communicate()
        assert process.returncode != 0
        assert "Bad dump file name " in err


def _assert_view_traces_csv(fname):
    assert os.path.isfile(fname)
    data = open(fname).read()
    assert "1,0,loop,5,15,7,113" in data
    assert "2,1,1,5,8,5,127" in data
    assert "3,2,interpreter,0,2,2,79" in data


def _assert_view_abort_reasons_csv(fname):
    assert os.path.isfile(fname)
    data = open(fname).read()
    assert "NYI: FastFunc print,4" in data


def _assert_view_abort_reasons_txt(fname):
    assert os.path.isfile(fname)
    data = open(fname).read()
    assert "NYI: FastFunc print: 4" in data


# A single trace bush is rendered in the same txt format as the original dump.
def _assert_view_tracebush_txt(fname):
    from dumpanalyze.dumpparser import DumpParser
    from dumpanalyze.trace import Trace

    assert os.path.isfile(fname)

    parser = DumpParser(fname)
    assert isinstance(parser, DumpParser)

    assert parser.parse() == DumpParser.PARSED_DUMP

    assert isinstance(parser.traces, list)
    assert isinstance(parser.abort_reasons, list)

    assert len(parser.traces) == 3
    assert len(parser.abort_reasons) == 0

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


def test_normal_run():
    with tempfile.TemporaryDirectory() as tmpdir:
        dump_fname = os.path.join(tmpdir, DUMP_FNAME)
        out_dir = dump_fname + "-parsed"

        shutil.copy(DUMP_FPATH, tmpdir)
        process = _prepare_cli_run([CLI_NAME, "--dump", dump_fname])
        __, __ = process.communicate()
        assert process.returncode == 0
        assert os.path.isdir(out_dir)

        fname_traces = os.path.join(out_dir, "gen-1-traces.csv")
        fname_reasons_csv = os.path.join(out_dir, "gen-1-abort-reasons.csv")
        fname_reasons_txt = os.path.join(out_dir, "gen-1-abort-reasons.txt")
        fname_tracebush = os.path.join(out_dir, "gen-1-bush-1.txt")

        _assert_view_traces_csv(fname_traces)
        _assert_view_abort_reasons_csv(fname_reasons_csv)
        _assert_view_abort_reasons_txt(fname_reasons_txt)
        _assert_view_tracebush_txt(fname_tracebush)

        assert os.path.isfile(os.path.join(out_dir, "gen-1-bush-1.png"))
