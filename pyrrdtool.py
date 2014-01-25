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
# 1. Get rid of the complicated __init__ signatures and use a {dict}
#    for rrd options set, for all classes.
#    This will ease a lot the factory implementation
# 2. Keep the eg. DEF class to be constructed with plain arguments
#    and create a, say, fDEF class (a facade) that handles a Variable and
#    creates a DEF object, able to output the cli args.
#    This will be better for clarity, understanding, testing and debugging.
#    (done for DEF, ongoing for all others)
# - Reuse the cli doc option definitions in classes variables doc
#   (with useful links to rrdtool apidoc?)
# - Check definition classes variables default values,
#   some might not be None but float('nan') (cf. rrdtool info and RRD.apply()) 
# - Turn the test.py into a UnitTest
#
# Global TODOs:
# - Create the concept of GraphTemplate():
#   takes a DataSource as argument and applies a predefined template
#   to this datasource. Returning a set of graph data and style
#   to be fed directly to the Graph(Component).
#   But maybe in a super-module
# - Apply GraphTemplate to make it easy to eg. 'flamestyle' a graph
#   flamestyle http://old.ed.zehome.com/?page=rrdtool2
# - Separate lib into pyrrdtool.data and . graph ?
#   for better readability ?
# - OK Every class must have its .create(config),
#   so that everybody know how to parse its related config object.
#   just like databse.


# Below are classes that are reused across pyrrdtool components
class Component():
    "Base class for all pyrrdtool classes"
    pass

#NOTE: Variable class meant to abstract the DataSource and RRA concepts,
#       and the reuse of Datasources within update, fetch and graph commands
#       by linking the datasource dans databases together, and making a
#       reusable datasources directory.
#       Moreover, il will 
#       is it a good idea?
class Variable(Component): #or Indicator ?
    "Links a DataSource and a Database, and abstracts rrdtool internals"
    #FIXME: weakref module could be used to keep refs
    #       noooo, no need, simply say s.datasource = ds
    vname = None
    "Virtual name of the datasouce, used by graph components"
    "(defaults to ds.name)"
    ds = None
    rrd = None
    rra = []
    def __init__(s, rrd, ds_name, vname=None):
        "Creates a Variable from a Database and a datasource name"
        "The Variable class is meta to rrdtool; it allows to reuse"
        "datasources definitions within the graphs objects,"
        "thus saving your typing of rrd, CF and other names"
        for ds in rrd.datasources:
            #uglycode, shall we use a dict for Database.datasources ?
            if ds.name == ds_name: break
        s.ds = ds
        s.rrd = rrd
        s.rra = rrd.rrarchives
        s.vname = vname if vname else ds.name
        

#FIXME: Keep this for the pyrrd super-module, that provides more complex features.
#class StyleTemplate(Component):
#    "Base class for defining arbitrary style templates to be applied to the given datasource"
#    style = []
#    def __init__(s, ds):
#        pass


class Database(Component):
    "Represents a rrd database file with its DSes and RRAs"
    "and reflects the rrd create command options."
    name = None
    "Name of the database (ie. {name}.rrd file)"
    _datasources = [] #FIXME: shall it be the object or the object.name string, or both ?
    "DataSource definitions (objects)"
    #FIXME: getter/setter not working properly
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
    noOverwrite = None
    "Overwrite any existing database file. Values: True or False"
    def __init__(s, name, ds, rra, step=None, start=None):
        #FIXME: would be good to set overwrite to False by default,
        #       unlike the default of rrdtool create (which is to overwrite),
        #       this forces to delete de db explicitely to avoid loosing data
        s.name = name
        s.datasources = ds
        s.rrarchives = rra
        s.step = step
        s.start = start
    def __str__(s):
        "FIXME: returns the rrdtool create command arguments"
        args = {arg:getattr(s,arg)
                for arg in ['start', 'step']
                if getattr(s, arg)}
        return "create %s %s %s %s" % (
            s.filename(),
            ' '.join(['--%s %s'%(k,v) for k,v in args.items()]),
            ' '.join([str(ds) for ds in s.datasources]),
            ' '.join([str(ds) for ds in s.rrarchives]))
    def filename(s):
        "Returns the database filename"
        return s.name + '.rrd' #FIXME: use os.path
    @staticmethod
    def create(config):
        "Returns an instance from the given config dictionary"
        "(as returned by info())"
        import os
        return Database(
            name = os.path.splitext(os.path.basename(config.get('filename')))[0],
            ds = [DS.create(name, c) for name,c in config.get('ds').items()],
            rra = [RRA.create(c) for c in config.get('rra')],
            start = config.get('start'),
            step = config.get('step'))

# Below are classes for create(), that I will probably use to compose these
# complex DS:speed:COUNTER:600:U:U and RRA:AVERAGE:0.5:1:24 patterns
# FIXME: It would be great to be able to use DataSources seamlessly,
#        for graphing without thinking of their database.
#        For that, the datasource needs to know to which Database(s) it belongs to.
class DataSource(Component):
    "Represents a DataSource definition"
    name = None
    "Name of the datasource (for referencing)"
    # FIXME: Implement constraint ?
    # must be 1 to 19 characters long in the characters [a-zA-Z0-9_]
    # http://oss.oetiker.ch/rrdtool/doc/rrdcreate.en.html
    type = None
    "DataType to use for this source"
    database = None #FIXME: database object reference should be set by constructor
    "Database name"
    def __init__(s, name, type):
        s.name = name
        s.type = type
    def __str__(s):
        return "DS:%s:%s" % (s.name, s.type)
    @staticmethod
    def create(name, config):
        #NOTE: there is an inconsistency in create() signature here.
        #       for the sake of using rrdtool info dict pristinely
        return DataSource(
            name = name,
            type = DataSourceType.create(config))

class DataSourceType(Component):
    "Represents a datasource type and options used by DataSource"
    "Command line equivalent is DST:arg1:arg2:..."
    #FIXME: Unncesseary, remove TYPES
    TYPES = ['GAUGE', 'COUNTER', 'DERIVE', 'ABSOLUTE', 'COMPUTE']
    "Available types"
    @staticmethod
    def create(config):
        return globals()[config.get('type')].create(config)
class DataSourceType_Common(DataSourceType):
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
    @staticmethod
    def create(config):
        return globals()[config.get('type')](
            heartbeat = config.get('minimal_heartbeat'),
            #FIXME: a parser function should take care of value format conversion
            min = config.get('min').replace('NaN','U'),
            max = config.get('max').replace('NaN','U'))
class GAUGE(DataSourceType_Common): pass
class COUNTER(DataSourceType_Common): pass
class DERIVE(DataSourceType_Common): pass
class ABSOLUTE(DataSourceType_Common): pass
class COMPUTE(DataSourceType):
#FIXME: RPN is used by the COMPUTE DataType and the CDEF and VDEF graph variables type.
#        Shall we make an RPN class whose purpose is to
#        handle RPN (reverse polish notation) expressions comprehensively ?
#        And makes them reusable ?
#        http://oss.oetiker.ch/rrdtool/doc/rrdgraph_rpn.en.html
#        RPN reuse is not todays topic so let's keep it simple
#        for now and refactor if needed in the future
    rpn = ''
    "Reverse polish notation arguments"
    def __init__(s, rpn):
        s.rpn = rpn
    def __str__(s):
        return 'COMPUTE:%s' % s.rpn
    @staticmethod
    def create(config):
        return COMPUTE(
            rpn = config.get('cdef'))

class RoundRobinArchive(Component):
    "Represents a RoundRobinArchive (RRA)  used by create()"
    #FIXME: Necessary? Are the cli/lib error messages good enough ?
    CONSOLIDATION_FUNCTIONS = ['AVERAGE', 'MIN', 'MAX', 'LAST']
    "Available consolidation functions"
    #FIXME: shall we create class AVERAGE|MIN|MAX|LAST() ?
    #       in order to have named arguments as class properties ?
    #       as well as HWPREDICT|MHWPREDICT|... classes ? 
    consolidation = None
    "Consolidation function (cf). Values: AVERAGE|MIN|MAX|LAST"
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
    @staticmethod
    def create(config):
        return RoundRobinArchive(
            consolidation = config.get('cf'),
            #FIXME: a parser function should take care of value format conversion
            #       eg. format(value) - note that it formatting has two directions
            xff = float(config.get('xff').replace(',','.')),
            steps = int(config.get('pdp_per_row')),
            rows = int(config.get('rows')))


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
    options = {
        'imgformat': None,
        "Values': PNG|SVG|EPS|PDF"
        'no-rrdtool-tag': True,
        "Hides Tobis credits"
        'option2': None,
        'option3': None,
    }
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

# Below are graph data classes
class GraphData(GraphElement):
    "Base class for graph data definition classes"
    "http://oss.oetiker.ch/rrdtool/doc/rrdgraph_data.en.html"
    INSTRUCTIONS_TYPES = ['DEF', 'VDEF', 'CDEF']
#FIXME: this is not used anymore, remove it
    instruction = None
    args = []
    def __init__(s, instruction, args):
        s.instruction = instruction
        s.args = args
    def __str__(s):
        return '%s:%s' % (
            s.instruction,
            ':'.join([str(arg) for arg in s.args]))
class DEF(GraphElement):
    vname = None
    rrdfile = None
    ds_name = None
    cf = None
    "Consolidation function name. Values: AVERAGE|MIN|MAX|LAST"
    step = None
    start = None
    end = None
    reduce = None
    def __init__(s, vname, rrdfile, ds_name, cf, step=None, start=None, end=None, reduce=None):
        s.vname = vname
        s.rrdfile = rrdfile
        s.ds_name = ds_name
        s.cf = cf
        if step: s.step = step
        if start: s.start = start
        if end: s.end = end
        if reduce: s.reduce = reduce
    def __str__(s):
        #FIXME: add remaining args: s.step, s.start, s.end, s.reduce
        return '%s:%s=%s:%s:%s' % (
            'DEF', #s.__class__.__name__,
            s.vname, s.rrdfile, s.ds_name, s.cf)
class eDEF(GraphElement):
    #FIXME: DEF is DEF_Base, eDEF is DEF and contains an instance of DEF_Base
    #FIXME: there is something to do with /reuse/ of DataSources config here
    #       -> yes, the concept of Variable (or Indicator?)
    variable = None
    "Variable definition object, contains vname definition"
    element = None
    "DEF object instance"
    def __init__(s, variable):
       s.variable = variable
       s.element = DEF(s.variable.vname,
                       s.variable.rrd.filename(),
                       s.variable.ds.name,
                       #FIXME: arbitratily uses the first available RRA
                       s.variable.rra[0].consolidation)
       #FIXME: add remaining constructor args (as in DEF)
    def __str__(s):
        return str(s.element)
class GraphElement_Common():
    vname = None
    rpn = None
    def __init__(s, vname, rpn):
        s.vname = vname
        "Variable name to use for calculated value (virtual name)"
        s.rpn = rpn
        "Operation in RPN format (reverse polish notation)"
        "http://oss.oetiker.ch/rrdtool/doc/rrdgraph_rpn.en.html"
    def __str__(s):
        return '%s=%s,%s,' % (
            s.__class__.__name__,
            s.vname, rpn)
class CDEF(GraphElement_Common):
    pass
class VDEF(GraphElement_Common):
    pass

# Below are graph style classes
class GraphStyle(GraphElement):
    "Base class for graph print elements classes"
    "http://oss.oetiker.ch/rrdtool/doc/rrdgraph_graph.en.html"
    INSTRUCTIONS_TYPES = ['PRINT','GPRINT','COMMENT','VRULE','HRULE','LINE','AREA','TICK','SHIFT','TEXTALIGN']
    def __init__(s, args):
        s.args = dict(s.args.items() + args.items())
    #FIXME: this will be unused when all graph style instructions are implemented
    #instruction = None
    #args = []
    #def __init__(s, instruction, args):
    #    s.instruction = instruction
    #    s.args = args
    #def __str__(s):
    #    return '%s:%s' % (
    #        s.instruction,
    #        ':'.join([str(arg) for arg in s.args]))
#FIXME: shall we create 1 class per GraphStyle element ?
#NOTE: some common factors:
# a. legend, color
# b. dashes, dashes-offset
class LINE(GraphStyle):
    args = {
        'width': None,
        'value': None,
        'color': None,
        'legend': None,
        'STACK': None,
        'skipscale': None,
        'dashes': None,
        'dashOffset': None
    }
    def __str__(s):
        # LINE[width]:value[#color][:[legend][:STACK][:skipscale][:dashes[=on_s[,off_s[,on_s,off_s]...]][:dash-offset=offset]]
        f = lambda arg, value: {
                'width': '%s' % value,
                'value': ':%s' % value, # mandatory
                'color': '#%s' % value,
                'legend': ':%s' % value,
                'STACK': 'STACK', #FIXME: use lowercase for key ?
                'skipscale': 'skipscale',
                'dashes': ':dashes=%s' % value,
                'dashOffset': ':dashes-offset=%s' % value,
            }[arg]# if value else '' #FIXME: attention, falsy values
        order = ['width', 'value', 'color', 'legend', 'STACK', 'skipscale', 'dashes', 'dashOffset']
        #return reduce(lambda string, arg: string + f(arg, s.args.get(arg)), order, '')
        return s.__class__.__name__+reduce(
            lambda x, y: x + y,
            [f(arg, s.args.get(arg)) for arg in order if s.args.get(arg)])
class eLINE(GraphElement):
    variable = None
    line = None
    def __init__(s, variable, args={}):
        s.variable = variable
        s.line = LINE(dict({
            'value': s.variable.vname
        }.items() + args.items()))
    def __str__(s):
        return str(s.line)
    
class AREA(GraphStyle):
    args = {
        'value':  None,
        'color':  None,
        'legend': None,
        'STACK': None,
        'skipscale': None
    }
    def __str__(s):
        # AREA:value[#color][:[legend][:STACK][:skipscale]]
        f = lambda arg, value: {
            'value': ':%s' % value,
            'color': '#%s' % value,
            'legend': ':%s' % value,
            'STACK' : 'STACK',
            'skipscale': 'skipscale'
        }[arg]
        order = ['value', 'color', 'legend', 'STACK', 'skipscale']
        return s.__class__.__name__+reduce(
            lambda x, y: x + y,
            [f(arg, s.args.get(arg)) for arg in order if s.args.get(arg)])
#class PRINT(GraphStyle):
#    vname = None
#    format = None
#class GPRINT(PRINT): pass #or
#class GPRINT(GraphStyle):
#    vname = None
#    format = None
#class COMMENT(GraphStyle):
#    text = None
#class VHRULE(GraphStyle):
#    color = None
#    legend = None
#    dashes = None
#    dashOffset = None
#    def __init__(s, p, color):
#        setattr(s, s.p) = val
#        s.color = color
#class VRULE(VHRULE):
#    p = 'time'
#    time = None
#class HRULE(VHRULE):
#    p = 'value'
#    value = None
#class TICK(GraphStyle):
#    vname = None
#    color = None
#    alpha = None
#    fraction = None
#    legend = None
#class SHIFT(GraphStyle):
#    vname = None
#    offset = None
#class TEXTALIGN(GraphStyle):
#    value = None
#    "Values: left|right|justified|center"


# Shorthands
RRD = Database
DS = DataSource
DST = DataSourceType
RRA = RoundRobinArchive


# Module-level functions
def info_raw(filename):
    "Returns a dict from the rrd file raw meta-information"
    import re
    from collections import defaultdict
    rawdata = _call('info %s' % filename)
    # Creates dict from 'rrd' data
    m = re.findall(r'^(\w*?) = (.*)$', rawdata, re.MULTILINE)
    data = dict(m)
    # Creates a structured dict out of 'ds' data
    m = re.findall(r'^ds\[(.*?)\]\.(.*?) = (.*)$', rawdata, re.MULTILINE)
    ds = data['ds'] = defaultdict(dict)
    for name, key, value in m:
        ds[name][key] = value
    # Creates a structured dict out of 'rra' data
    m = re.findall(r'^rra\[(.*?)\]\.(.*?) = (.*)$', rawdata, re.MULTILINE)
    rra = data['rra'] = defaultdict(dict)
    for name, key, value in m:
        rra[name][key] = value
    # Typecast: ds: defaultdict -> dict, rra: defaultdict -> list
    data['ds'] = dict(ds)
    data['rra'] = [rra[str(i)] for i in range(len(rra))] # assumes rra key
                     # are contiguous, will raise an error if not the case
    return data

def info(filename):
    "Returns a dict from the rrd file meta-information"
    "containing a subset of content that is useful to pyrrdtool"
    #FIXME: in fact, the info dict should be returned as is:
    #       toby thought about its info spec, reuse it: simpler, thiner,  better
    def clean(info):
        "Recursively strips quotes (\") from values"
        # Strips quotes (") from values
        for k in info:
            if type(info[k]) == list:
                info[k] = [clean(i) for i in info[k]]
            elif type(info[k]) == dict:
                clean(info[k])
            else:
                info[k] = info[k].strip('"')
                #FIXME: Clean 'cdp_prep[0]' keys in rra list items
                #FIXME: Convert 0,0000000000e+00 values to float ?
                #FIXME: Convert NaN values to float('nan') ? or 'U' ? which is most meaningful
        return info
    return clean(info_raw(filename))

def _call(argline):
    "Helper for rrdtool command calls"
    import subprocess
    cmd = ['rrdtool'] + argline.split()
    return subprocess.check_output(cmd, shell=False)
    # !! don't use graphing from cli without pipe mode (rrdtool -) !
    #    It will reload fonts cache every time !
    #    Tobi says the way out is to run 'rrdtool -' (pipe mode)
    # Use it from a shared library to avoid reloading fonts cache
    # on every call (does pythonrrd lib do that, is it a shared lib ??)


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


def factory(classname, *args, **kwargs):
    "Static factory method"
    #FIXME: superseded by Component.create
    #FIXME: get the classname.__init__() arguments using
    #       import inspect; print(inspect.getargspec(the_function)), and remove
    #       kwargs keys that are not expected by classname.__init__()
    cls = globals()[classname]
    import inspect
    print inspect.getargspec(cls.__init__)
    print 
    print args, kwargs
    return globals()[classname](*args, **kwargs)


#FIXME: superseded by class Variable, remove this
def datasources():
    "Test implementation to collect existing Datasources objects"
    #FIXME: return a list of Variable objects ?
    #FIXME: the DataSource should really be added its rrd & rra references list
    #       it would make it so easy to use (eg. add a whole RRD.datasources to a graph!)
    #       but it is a short round towards that goal
    import gc
    datasources = {}
    for rrd in gc.get_objects():
        if isinstance(rrd, Database):
            for ds in rrd.datasources:
                ds._rrd = rrd
                ds._rra = rrd.rrarchives
                datasources[ds.name] = ds
    return datasources

# Below are definition import/export functions
# This might be another piece of software (standalone or with webview)
def json_load(filename):
    "Returns a list of objects instances defined in the given json filename"
    pass

def json_import(string):
    pass

def json_export(obj):
    "Serializes the given object into a json string"
    #FIXME: not working properly
    #FIXME: implement a recursive function to develop variables containing dict objects
    #FIXME: how to manage both objects serialization and referencing (for composition) ?
    import json
    return json.dumps(obj.__dict__.items())
