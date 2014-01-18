pyrrdtool
=========

**A python rrdtool facade**

The purpose of thie rrdtool-cli facade library is to make
the configuration of rrd creation, update and graph easier and faster.

By enabling the user to *create definitions* of rrdatabases, datasouces
and graphs that are *modular* and *reusable* for creating, updating and graphing
a wide variety of graphs,  easily and with peace of mind.

Along with a python API to call rrdtool features such as create, update, fetch
and graph that is easier and faster to use, with default and automatic cli options
generation.

It should be easy to provide the graphing feature as a REST API that return
graph images binaries.

--

Because writing this library is also an in-depth learning of rrdtool,
the code should be commented nicely to *promote the understanding of what's happening*
