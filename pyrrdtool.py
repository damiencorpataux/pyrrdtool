# The purpose of thie rrdtool-cli facade library is to make
# the configuration of rrd creation, update and graph easier and faster.
#
# By enabling the user to create definitions of rrdatabases, datasouces
# and graphs that are reusable for creating, updating and graphing
# a wide variety of graphs,  easily and with peace of mind.
#
# Also, it eases the definition of DS, RRA and graph configurations,
# and makes them reusable - that is the point of that library.
# E.g. the user can graphe multiple graphs of multiple sources
# with multiple style by reusing Database, DataSource and GraphData.
#
# Global FIXMEs:
# - Reuse the cli doc option definitions in classes variables doc
#   (with useful links to rrdtool apidoc?)


# Below are classes that are reused across pyrrdtool components
class Component():
    "Base class for all pyrrdtool classes"
    pass

class Database(Component):
    "Represents a rrd database file with its DSes and RRAs"
    "and reflects the rrd create command options."
    "This class is used by the create() command and is reused"
    "for fetch() and graph()"
    #FIXME: we could do it ORM-style where the db filename is {name}.rrd
    name = None
    "Filename of the database (.rrd file)"
    _datasources = [] #FIXME: shall it be the object or the object.name string, or both ?
    "DataSource definitions (objects)"
    @property
    def datasources(s):
        return s._datasources
    @datasources.setter
    def datasources(s, value):
        #FIXME: here, a reference to this database
        #       should be made within the given datasource
        s._datasources = value
    rrarchives = [] #FIXME: same as datasources
    "RoundRobinArchive definitions (objects)"
    start = None
    "Archive start time"
    step = None
    "Archive step interval"
    overwrite = True
    "Overwrite any existing database file"
    def __init__(s, name, ds, rra, step=None, start=None, overwrite=True):
        #FIXME: would be good to set overwrite to False by default,
        #       unlike the default of rrdtool create (which is to overwrite),
        #       this forces to delete de db explicitely to avoid loosing data
        s.name = name
        s.datasources = ds or []
        s.rrarchives = rra or []
        s.step = step
        s.start = start
        s.overwrite = overwrite
    def filename(s):
        "Returns the database filename"
        return s.name + '.rrd' #FIXME: use os.path
    def load(s, filename):
        "Creates a database object from the given filename (eg. test.rrd)"
        "along with the DataSource and RoundRobinArchive objects"
        #FIXME: should this be a module function, eg: pyrrdtool.load(filename) ?
        #       depends whether it sets this database properties or it returns a
        #       list of objects.
        # TODO: use rrdtool info to extract db, ds and rra information
        #       and create the object instances accordingly
        return []
    def __str__(s):
        "FIXME: returns the rrdtool create command arguments"
        args = {arg:getattr(s,arg)
                for arg in ['start', 'step', 'overwrite']
                if getattr(s, arg)}
        return "create %s %s %s %s" % (
            s.filename(),
            ' '.join(['--%s %s'%(k,v) for k,v in args.items()]),
            ' '.join([str(ds) for ds in s.datasources]),
            ' '.join([str(ds) for ds in s.rrarchives]))

#FIXME: Variable class meant to abstract the DataSource and RRA concepts,
#       and the reuse of Datasources within update, fetch and graph commands
#       by linking the datasource dans databases together, and making a
#       reusable datasources directory.
#       Moreover, il will 
#       is it a good idea?
#class Variable(Component):
#    "Links a DataSource and a Database, and abstracts rrdtool internals"
#    datasource = None
#    database = None


# Below are classes for create(), that I will probably use to compose these
# complex DS:speed:COUNTER:600:U:U and RRA:AVERAGE:0.5:1:24 patterns
# FIXME: It would be great to be able to use DataSources seamlessly,
#        for graphing without thinking of their database.
#        For that, the datasource needs to know to which Database(s) it belongs to.
class DataSource(Component):
    "Represents a DataSource definition"
    name = None
    "Name of the datasource (for referencing)"
    # FIXME: Implement constraint:
    # must be 1 to 19 characters long in the characters [a-zA-Z0-9_]
    # http://oss.oetiker.ch/rrdtool/doc/rrdcreate.en.html
    type = None #FIXME: object instance or object.name ?
    "DataType to use for this source"
    database = None #FIXME: database object reference should be set by constructor
    "Database name"
    def __init__(s, name, type):
        s.name = name
        s.type = type
    def __str__(s):
        return "DS:%s:%s" % (s.name, s.type)

class DataSourceType(Component):
    "Represents a datasource type and options used by DataSource"
    "Command line equivalent is DST:arg1:arg2:..."
    TYPES = ['GAUGE', 'COUNTER', 'DERIVE', 'ABSOLUTE', 'COMPUTE']
    "Available types"

class DataSourceTypeBase(DataSourceType):
    heartbeat = None
    "the maximum number of seconds that may pass between two updates of this"
    "data source before the value of the data source is assumed to be *UNKNOWN*"
    min = 'U'
    "Minimum expected values for supplied data"
    max = 'U'
    "Maximum expected values for supplied data"
    "Any value outside the defined range will be regarded as *UNKNOWN*"
    "Always set If information on min/max expected values is available;"
    "this will help RRDtool in doing a simple sanity check on the data"
    "supplied when running update"
    def __init__(s, heartbeat, min=None, max=None):
        s.heartbeat = heartbeat
        if min: s.min = min
        if max: s.max = max
    def __str__(s):
        return '%s:%s' % (
            s.__class__.__name__,
            ':'.join([str(getattr(s,arg)) for arg in ['heartbeat','min','max']]))
class GAUGE(DataSourceTypeBase): pass
class COUNTER(DataSourceTypeBase): pass
class DERIVE(DataSourceTypeBase): pass
class ABSOLUTE(DataSourceTypeBase): pass
class COMPUTE(DataSourceType):
#FIXME: RPN is used by the COMPUTE DataType and the CDEF and VDEF graph variables type.
#        Shall we make an RPN class whose purpose is to
#        handle RPN (reverse polish notation) expressions comprehensively ?
#        And makes them reusable ?
#        http://oss.oetiker.ch/rrdtool/doc/rrdgraph_rpn.en.html
#        RPN reuse is not todays topic so let's keep it simple
#        for now and refactor if needed in the future
    rpn = []
    "Reverse polish notation arguments"

class RoundRobinArchive(Component):
    "Represents a RoundRobinArchive (RRA)  used by create()"
    #FIXME: Necessary? Are the cli/lib error messages good enough ?
    CONSOLIDATION_FUNCTIONS = ['AVERAGE', 'MIN', 'MAX', 'LAST']
    "Available consolidation functions"
    #FIXME: shall we create class AVERAGE|MIN|MAX|LAST() ?
    #       in order to have named arguments as class properties ?
    #       as well as HWPREDICT|MHWPREDICT|... classes ? 
    consolidation = None
    "The consolidation function to use with the archive"
    "This affects how data is resampled to lower resolutions"
    "and should be chosen according to what you want to track"
    "eg. MIN is you want to track, say, a minimal service level"
    xff = None
    steps = None
    rows = None
    #FIXME: Update doc: "A list of consolidation function options"
    "These options configure the behaviour of the consolidation function"
    "The options structure and contents depends on the function used"
    "http://oss.oetiker.ch/rrdtool/doc/rrdcreate.en.html"
    def __init__(s, consolidation, xff, steps, rows):
        s.consolidation = consolidation
        s.xff = xff
        s.steps = steps
        s.rows = rows
    def __str__(s):
        return 'RRA:%s:%s' % (
            s.consolidation,
            ':'.join([str(getattr(s, arg)) for arg in ['xff','steps','rows']]))


# Below are classes for graph()
# There are many more to implement (thus understand): LINE, AREA, PRINT, ...
# http://oss.oetiker.ch/rrdtool/doc/rrdgraph_graph.en.html
# Remember: the goal is to reuse DataSource and RRD configs
#           try to create a ~ORM for rrd? :)
class Graph(Component):
    "Represents a rrdtool graph and contains all the possible options"
    "for the rrdtool graph function"
    "http://oss.oetiker.ch/rrdtool/doc/rrdgraph.en.html"
    name = '-'
    #FIXME: Reuse cli options names and doc (--* options)
    #       Implement as 1 attribute per option, or options = [] ?
    option1 = None
    option2 = None
    data = []
    "Variables and calculation definitions (GraphData objects)"
    "reflects rrdtool graph [data definition ...] [data calculation ...]"
    "[variable definition ...] options"
    "http://oss.oetiker.ch/rrdtool/doc/rrdgraph_data.en.html"
    style = []
    "Graph and print elements definitions (GraphStyle objects)"
    "reflects rrdtool graph [graph elelement ...] [print element ...] options"
    "http://oss.oetiker.ch/rrdtool/doc/rrdgraph_graph.en.html"
    def __init__(s, data, style, name=None):
        #FIXME: how to add options in constructor arguments, one by one or a list ?
        s.data = data
        s.style = style
        if name: s.name = name
    def __str__(s):
        #FIXME: the DataSource reuse must apply here on data list
        return 'graph %s %s %s %s' % (
            s.name,
            '', #FIXME: options will go here
            ' '.join([str(data) for data in s.data]),
            ' '.join([str(style) for style in s.style]))

class GraphElement(Component):
    #FIXME: if we choose to use 1 class per graph element,
    #       we might use the following common string serializer
    #def __str__(s):
    #    return '%s:%s' % (
    #        s.__class__.__name__,
    #        '123')
    pass

class GraphData(GraphElement):
    "Base class for graph data definitions classes"
    "http://oss.oetiker.ch/rrdtool/doc/rrdgraph_data.en.html"
    INSTRUCTIONS_TYPES = ['DEF', 'VDEF', 'CDEF']
    instruction = None
    args = []
    def __init__(s, instruction, args):
        s.instruction = instruction
        s.args = args
    def __str__(s):
        return '%s:%s' % (
            s.instruction,
            ':'.join([str(arg) for arg in s.args]))
#FIXME: Shall we create 1 class per GraphData element (DEF,CDEF,VDEF) ?
#       Note that CDEF and VDEF use the RPN
#class DEF(GraphElement):
#    name = None
#    #FIXME: there is something to do with /reuse/ of DataSources config here
#    DS = None
#    consolidation = None # Can RRA.consolidation be reused here (through DS.rrd reference, for automatic setting of this variable) ? Or is it autoset by the cli if option is not specified ?
#    step = None # Same as consolidation, with RRD.step through DS.rrd reference too
#    start = None
#    end = None
#class CDEF(GraphElement):
#    name = None
#    rpn = []
#class VDEF(GraphElement):
#    name = None
#    rpn = []

class GraphStyle(GraphElement):
    "Base class for graph print elements classes"
    "http://oss.oetiker.ch/rrdtool/doc/rrdgraph_graph.en.html"
    INSTRUCTIONS_TYPES = ['PRINT','GPRINT','COMMENT','VRULE','HRULE','LINE','AREA','TICK','SHIFT','TEXTALIGN']
    instruction = None
    args = []
    def __init__(s, instruction, args):
        s.instruction = instruction
        s.args = args
    def __str__(s):
        return '%s:%s' % (
            s.instruction,
            ':'.join([str(arg) for arg in s.args]))
#FIXME: shall we create 1 class per GraphStyle element ?
#class PRINT(GraphStyle): pass
#class GPRINT(GraphStyle): pass
#class COMMENT(GraphStyle): pass
#class VRULE(GraphStyle): pass
#class HRULE(GraphStyle): pass
#class LINE(GraphStyle): pass
#class AREA(GraphStyle): pass
#class TICK(GraphStyle): pass
#class SHIFT(GraphStyle): pass
#class TEXTALIGN(GraphStyle): pass


# Shorthands
RRD = Database
DS = DataSource
DST = DataType = DataSourceType
RRA = RoundRobinArchive


# Below are low level helper function for calling rrdtool cli with arguments

# http://oss.oetiker.ch/rrdtool/doc/rrdcreate.en.html
# rrdtool create filename [--start|-b start time] [--step|-s step] [--no-overwrite] [DS:ds-name:DST:dst arguments] [RRA:CF:cf arguments]
# rrdtool create test.rrd        \
#    --start 920804400          \
#    DS:speed:COUNTER:600:U:U   \
#    RRA:AVERAGE:0.5:1:24       \
#    RRA:AVERAGE:0.5:6:10
#
#FIXME: for now str(Database) outputs the create command args
#       it is better to use this create() function below to do that job
#       but shall we use that long func signature, or just create(Database) ?
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

def _call():
    "Helper for rrdtool command calls"
    pass
    # !! don't use graphing from cli without pipe mode (rrdtool -) !
    #    It will reload fonts cache every time !
    #    Tobi says the way out is to run 'rrdtool -' (pipe mode)
    # Use it from a shared library to avoid reloading fonts cache
    # on every call (does pythonrrd lib do that, is it a shared lib ??)


# Below are definition import/export functions
# This might be another piece of software (standalone or with webview)
def json_load(filename):
    "Returns a list of objects instances defined in the given json filename"
    pass

def json_import(string):
    pass

def json_export():
    "Serializes the given object into a json string"
    pass
