dumpanalyze
===========

Introduction
------------

`dumpanalyze` is a mini-framework equipped with a CLI for processing LuaJIT's
plain text JIT compiler dumps. `dumpanalyze` can be used with any other software
as well, as long the dump format remains the same.

To get a grasp of what a *dump* is, run following command in your terminal
(assuming you already have LuaJIT installed):

```
luajit -jdump=T -e 'local s = 0; for i = 1, 100 do s = s + i end; print(s)'
```

You will see some plain text output which is generated in run-time as long as
the JIT compiler records a trace, assembles its machine code, etc. This info
can now be used for analysing/improving/troubleshooting the compiler.

However, if you try to run the dump with a large application under heavy load,
you may face certain difficulties trying to interpret the output. First,
it may be really **huge**. Second, it may contain various artefacts (compiled
traces, aborted traces, exit state records) melted into a single data stream.
Third, if your application is large enough, the dump will contain information
about thousands of traces connected with non-trivial parent/child relations.

`dumpanalyze` was created to (at least partly) address these challenges.

Architecture
------------

The core of the `dumpanalyze` is a *parser of dumps* which reads its input
line by line converting it into a simple object model (compiled traces,
trace bushes, abort reasons, etc.).

After parsing is done, resulting objects can be grouped and rendered
with a help of various *views*.

Everything is glued together with a CLI although can be used a Python module.

Available Views
---------------

* Aggregated list of compiled traces (`csv`)
* List of trace bushes (`txt`, `png`)
* Aggregated list of abort reasons (`csv`)
* List of abort reasons grouped by file:line (`txt`)

Installation
------------

For local installation, simply clone this repository.

If you need a system-wide installation, please run following command from
the repository root after cloning it:

```
sudo pip install .
```

This will install all modules and create a CLI wrapper named `dumpanalyze`.

Usage
-----

In case of local installation:

```
python3 -m dumpanalyze --dump /path/to/dump.txt --out-dir /tmp/dump-parsed
```

...or...

```
PYTHONPATH=. python3 dumpanalyze --dump /path/to/dump.txt --out-dir /tmp/dump-parsed
```

In case of system-wide installation:

```
dumpanalyze --dump /path/to/dump.txt --out-dir /tmp/dump-parsed
```

Benchmarks
----------

* Data: a dump obtained from a production system (~800Mb of plain text data)
* Machine: Intel(R) Core(TM) i5-4570 CPU @ 3.20GHz with 8Gb RAM
* Time (in user mode): 122 seconds
* Peak RAM usage: 900Mb

Links
-----

* [LuaJIT dump module](https://github.com/LuaJIT/LuaJIT/blob/master/src/jit/dump.lua)
* [Loom: replacement / enhancement of the -jdump option](https://github.com/cloudflare/loom)
* [luajit-web-inspector](https://github.com/mejedi/luajit-web-inspector)
* [Studio: Yet another debugging environment from RaptorJIT developers](https://github.com/studio/studio)

Caveats
-------

* This software was tested with Python 3.5 and 3.6.
* The parser supports **only plain text dumps** at the moment.

Copyright and License
---------------------

Copyright 2017 IPONWEB Ltd.

This software is licensed under the terms of the MIT license.
