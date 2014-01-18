# The purpose of thie rrdtool-cli facade library is to make
# the configuration of rrd creation, update and graph easier and faster,
# by enabling the user to create definitions of rrdatabases, datasouces
# and graphs that are reusable for creating, updating and graphing
# a wide variety of graphs,  easily and with peace of mind.

# Below are classes for create(), that I will probably use to compose these
# complex DS:speed:COUNTER:600:U:U and RRA:AVERAGE:0.5:1:24 patterns
class DataSource():
    "Represents a DataSource used by create()"
    DS = []
    RRA = []

class DataSourceType():
    "Represents a DataSourceType used by DataSource"
    #FIXME: Necessary? No: rrdtool error messages are good enough
    NAMES = ['GAUGE', 'COUNTER', 'DERIVE', 'ABSOLUTE']
    name = 'COUNTER'
    args = [600, 'U', 'U'] # this is tricky

class RoundRobinArchive():
    "Represents a RoundRobinArchive (RRA)  used by create()"
    CF = ['AVERAGE', 'MIN', 'MAX', 'LAST']
    consolidation = 'AVERAGE'
    args = [0.5, 1, 24] # this is tricky

# Below are classes for graph()
# There are many more to implement (thus understand): LINE, AREA, PRINT, ...
# http://oss.oetiker.ch/rrdtool/doc/rrdgraph_graph.en.html
# Remember: the goal is to reuse DataSource and RRD configs
#           try to create a ~ORM for rrd? :)
class GraphData():
    "Common denominator of graph data and variables classes"
    pass

class DEF(GraphData):
    filename = None
    #FIXME: The is something to do with /reuse/ of DataSources config here
    DS = None
    consolidation = None
    step = None
    start = None
    end = None

class CDEF(GraphData):
    expression = None 

class VDEF(GraphData):
    expression = None 


# Shorthands
DS = DataSource
DST = DataSourceType
RRA = RoundRobinArchive

# Below are low level helper function for calling rrdtool cli with arguments

# http://oss.oetiker.ch/rrdtool/doc/rrdcreate.en.html
# rrdtool create filename [--start|-b start time] [--step|-s step] [--no-overwrite] [DS:ds-name:DST:dst arguments] [RRA:CF:cf arguments]
# rrdtool create test.rrd        \
#    --start 920804400          \
#    DS:speed:COUNTER:600:U:U   \
#    RRA:AVERAGE:0.5:1:24       \
#    RRA:AVERAGE:0.5:6:10
def create(filename, start=None, step=None, overwrite=True, ds=[], rra=[]):
    pass

# http://oss.oetiker.ch/rrdtool/doc/rrdupdate.en.html
# rrdtool {update | updatev} filename [--template|-t ds-name[:ds-name]...] [--daemon address] [--] N|timestamp:value[:value...] at-timestamp@value[:value...] [timestamp:value[:value...] ...]
# rrdtool update test.rrd 920804700:12345 920805000:12357 920805300:12363
def update(filename, value, time='N', verbose=False):
    # rrdtool update filename time:value
    # use updatev if verbose=True
    pass

# http://oss.oetiker.ch/rrdtool/doc/rrdfetch.en.html
# rrdtool fetch filename CF [--resolution|-r resolution] [--start|-s start] [--end|-e end] [--daemon address]
# rrdtool fetch test.rrd AVERAGE --start 920804400 --end 920809200
def fetch(filename, consolidation='AVERAGE', start=None, end=None, resolution=None, daemon=None):
    pass

# http://oss.oetiker.ch/rrdtool/doc/rrdgraph.en.html
# rdtool graph|graphv filename [option ...] [data definition ...] [data calculation ...] [variable definition ...] [graph element ...] [print element ...]
# rrdtool graph speed3.png                            \
#    --start 920804400 --end 920808000               \
#    --vertical-label km/h                           \
#    DEF:myspeed=test.rrd:speed:AVERAGE              \
#    "CDEF:kmh=myspeed,3600,*"                       \
#    CDEF:fast=kmh,100,GT,kmh,0,IF                   \
#    CDEF:good=kmh,100,GT,0,kmh,IF                   \
#    HRULE:100#0000FF:"Maximum allowed"              \
#    AREA:good#00FF00:"Good speed"                   \
#    AREA:fast#FF0000:"Too fast"
def graph(indicators=[], outfile='-', options=[], data=[]):
    #FIXME: Shall we enumerate all (20+) cli options in the fn signature
    #       or use a options list ? (with default best options)
    pass
    # !! don't use graphing from cli ! it will reload fonts cache every time !
    #    Tobi says the way out is to run 'rrdtool -'
    # Use it from a shared library (does pythonrrd lib do that ??)
    # Also see: Use rrdtool through pipe mode (australia guy)

def _call():
    "rrdtool cli call helper"
    pass
