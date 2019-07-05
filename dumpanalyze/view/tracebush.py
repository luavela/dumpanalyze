# -*- coding: utf-8 -*-
#
# Trace bush view.
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

import graphviz


class ViewTraceBush:

    MARKED_TRACE_COLOR = "crimson"

    def __init__(self, fmt):
        self._fmt = fmt

    def render(self, fname, bush):
        if self._fmt == "txt":
            self._render_txt(fname, bush)
        elif self._fmt == "png":
            self._render_png(fname, bush)
        else:
            raise Exception("Unknown format")

    def _render_txt(self, fname, bush):
        with open(fname, "w") as out:
            for trace in bush.traces:
                self._print_trace(out, trace)

    def _render_png(self, fname, bush):
        graph = graphviz.Digraph(format="png")
        for trace in bush.traces:
            self._add_to_graph(graph, bush, trace)
        graph.render(filename=fname, cleanup=True)

    def _print_trace(self, out, trace):
        padding = " " if trace.parent else ""
        out.write("---- TRACE {} start {}{}{}:{}\n".format(
            trace.id,
            trace.parent,
            padding,
            trace.file,
            trace.line
        ))
        out.write("".join(trace.bc))
        out.write("---- TRACE {} IR\n".format(trace.id))
        out.write("".join(trace.ir))
        out.write("---- TRACE {} mcode {}\n".format(
            trace.id,
            trace.size_mcode
        ))
        out.write("".join(trace.mc))
        out.write("---- TRACE {} stop -> {}\n".format(
            trace.id,
            trace.link_type
        ))
        out.write("\n")

    # Add a trace (either a root one or a side-trace) to the graph.
    def _add_to_graph(self, graph, bush, trace):

        #
        # Add the "trace entry node" (along with a link to the parent for
        # side traces)
        #

        node_start = "START " + str(trace.id)
        self._add_boundary_node(graph, node_start, trace.is_root)

        # In case of side traces, highlight parent's compiled side-exit:
        if not trace.is_root:
            graph.edge(trace.parent, node_start, style="bold")

        node_last = self._add_trace_body(graph, trace, node_start)

        #
        # Add the "trace exit node" with link information
        #

        link_type = trace.link_type
        node_end = "END " + str(trace.id) + " "
        if link_type == "interpreter":
            # A stub trace: The only thing it does
            # is an immediate switch to interpreter
            node_end += "enforce VM"
        elif link_type == "return":
            # Normal return to interpreter
            node_end += "return to VM"
        elif link_type == "loop":
            # Looping trace
            node_end += "loop"
        elif link_type.isnumeric():
            # Link to another root trace
            node_end += "goto " + link_type
        else:
            # Don't know how to render the rest properly
            # will be fixed on demand
            node_end += link_type

        self._add_boundary_node(graph, node_end, trace.is_root)
        self._add_implicit_cf_edge(graph, node_last, node_end, trace.is_root)

        node_loop = None
        if link_type == "loop":
            node_loop = node_start
        elif link_type.isnumeric() and int(link_type) == bush.root_id:
            # If current trace links to current *root* trace, add a
            # corresponding
            # edge. Otherwise the link will point to some other bush
            # outside the graph.
            node_loop = "START " + str(bush.root_id)

        if node_loop is not None:
            graph.edge(node_end, node_loop, style="bold")

    # Add the body of the trace (exit 0 --> exit 1 --> ... --> exit N).
    def _add_trace_body(self, graph, trace, node_start):
        side_exits = sorted(trace.side_exits.keys())
        node_prev = node_start

        for side_exit in side_exits:
            node_side = str(trace.id) + "/" + str(side_exit)
            self._add_implicit_cf_edge(
                graph, node_prev, node_side, trace.is_root
            )
            if trace.is_root:
                graph.node(
                    node_side,
                    style="bold",
                    color=self.MARKED_TRACE_COLOR
                )
            node_prev = node_side

        return node_prev

    # Add initial/final node for a trace
    def _add_boundary_node(self, graph, node, is_root):
        graph.node(node, style="bold", shape="box")
        if is_root:
            graph.node(node, color=self.MARKED_TRACE_COLOR)

    # Add an edge denoting an implicit control flow within the trace
    def _add_implicit_cf_edge(self, graph, node1, node2, is_root):
        if is_root:
            graph.edge(
                node1, node2,
                color=self.MARKED_TRACE_COLOR,
                penwidth="1.5"
            )
        else:
            graph.edge(node1, node2, style="dashed")
