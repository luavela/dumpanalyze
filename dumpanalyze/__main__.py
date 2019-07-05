# -*- coding: utf-8 -*-
#
# Command-line interface for parsing dumps and producing views.
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
import os
import errno
import argparse

from dumpanalyze.dumpparser import DumpParser
from dumpanalyze.traceforest import TraceForest

from dumpanalyze.view.traces import ViewTraces
from dumpanalyze.view.tracebush import ViewTraceBush
from dumpanalyze.view.abortreasonslist import ViewAbortReasonsList
from dumpanalyze.view.abortreasonsdetails import ViewAbortReasonsDetails

if sys.version_info[0] < 3:
    sys.exit("This toolkit requires Python 3.0+")


def parse_command_line(argv):
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--dump",
        type=str,
        help="Path to the dump file",
    )
    argparser.add_argument(
        "--out-dir",
        type=str,
        help="Path to output directory",
    )
    args = argparser.parse_args(argv[1:])
    return args


def get_output_directory(args):
    out_dir = args.out_dir

    if out_dir is None:
        out_dir = os.path.join(
            os.path.dirname(args.dump),
            "{}-parsed".format(os.path.basename(args.dump)),
        )

    if os.path.isdir(out_dir):
        if not os.access(out_dir, os.W_OK):
            sys.exit("Bad output directory '{}'".format(out_dir))
        else:
            return out_dir

    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as e:
        if e.errno == errno.EACCES:
            sys.exit(
                "Permission denied to create output directory '{}'"
                .format(out_dir)
            )
        else:
            raise

    return out_dir


def main(argv=None):
    argv = argv or sys.argv
    args = parse_command_line(argv)

    if args.dump is None:
        sys.exit("Dump file name is not specified")
    elif not(os.path.isfile(args.dump) and os.access(args.dump, os.R_OK)):
        sys.exit("Bad dump file name '{}'".format(args.dump))

    out_dir = get_output_directory(args)

    print("Initializing")

    # Setup parser:
    parser = DumpParser(args.dump)

    # Setup all available views:
    v_traces = ViewTraces("csv")
    v_ar_list = ViewAbortReasonsList("csv")
    v_ar_details = ViewAbortReasonsDetails("txt")
    v_bush_txt = ViewTraceBush("txt")
    v_bush_png = ViewTraceBush("png")

    generation = 1
    while True:
        print("Generation {}: parsing dump".format(generation))

        status = parser.parse()
        traces = parser.traces
        abort_reasons = parser.abort_reasons

        print("Read {} compiled traces".format(len(traces)))

        forest = TraceForest(traces)
        bushes = forest.bushes

        print("Read {} trace bushes".format(len(bushes)))

        print("Rendering aggregated list of compiled traces")
        v_traces.render(os.path.join(
            out_dir, "gen-{}-traces.csv".format(generation)
        ), traces)

        print("Rendering aggregated list of abort reasons")
        v_ar_list.render(os.path.join(
            out_dir, "gen-{}-abort-reasons.csv".format(generation)
        ), abort_reasons)

        print("Rendering detailed list of abort reasons")
        v_ar_details.render(os.path.join(
            out_dir, "gen-{}-abort-reasons.txt".format(generation)
        ), abort_reasons)

        print("Rendering views of bushes")
        for root_id, bush in bushes.items():
            fname = "gen-{}-bush-{}".format(generation, str(root_id))
            v_bush_txt.render(os.path.join(out_dir, fname + ".txt"), bush)
            v_bush_png.render(os.path.join(out_dir, fname), bush)

        if status == parser.PARSED_DUMP:
            break

        generation += 1

    print("Done")


if __name__ == "__main__":
    main()
