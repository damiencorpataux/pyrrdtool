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
# 1. Get rid of the complicated __init__ signatures and use a {dict} ?
#    for rrd options set, for all classes.
#    but this make __doc__ the options impossible :(
#    This will ease a lot the factory implementation
#    -> so it is not an argument anymore :)
#    Options dict:
#    PROs: easier to iter (no getattr()), easier to get keys (no class prop clobber)
#    CONs: harder to document (no __doc__ for dicts)
#    Alternatives:
#    - options dict: there's a args dict the defines args names and default values,
#      it makes easy to iterate the dict to generate args
#      it makes easy to have dashes (-) in keys (eg no-overwrite, dash-offset)
#      it makes easy to merge default options dict with given options dict
#    - kwargs: there's a args_order list that defines
#      (1) arguments names (for finding rddtool args amongst class vars) and default values
#      (2) the order of args (already present, and needed by opt dicts too, see __str__)
#      and there's a get_args() function that returns args dict from class vars
#      this way we can still documents args using class vars __doc__
#      -> but can we merge easily the given args (as easy as dict) ?
#    Anyway it is: either all-kwargs, either options dict
# 2. DEF- & LINE.from_template show that the __init__ signature of their
#    respective class differs: the 1st is kwargs, the 2nd is {options_dict}
#    This is linked to 1. - so decide.
# 3. Component.from_variable factorization fails because it is
#    static and doesn't know __class__, therefore it is impossible
#    to factorize it into the super-class.
#    Why not make an .apply(s, config) method that is a @classmethod
#    and use it so: LINE.apply(LINE(config), variable)
#    or maybe even: Component.factory(LINE(config), variable)
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
# - See if __repr__ should be used over __str__
#   http://stackoverflow.com/questions/1436703/difference-between-str-and-repr-in-python
# - Add the ability to create a definition object from a given rrdtool command line
# - Manage the rrdcached daemon parameter (in Database class)


# Below are classes that are reused across pyrrdtool components
class Component():
    "Base class for all pyrrdtool classes"
    #FIXME: shall we implement options merging here,
    #       automatic or explicitely called by subclasses ?
    def sapply(s, string):
        "Applies the given string to instance args and returns the instance"
        raise NotImplementedError('This method must be implemented by subclasses')

#NOTE: Variable class meant to abstract the DataSource and RRA concepts,
#       and the reuse of Datasources within update, fetch and graph commands
#       by linking the datasource dans databases together, and making a
#       reusable datasources directory.
#       Moreover, il will 
#       is it a good idea?
class Variable(Component): #or Indicator ?
    "Links a DataSource and a Database, and abstracts rrdtool internals"
    vname = None
    "Virtual name of the datasouce, used by graph components"
    "(defaults to ds.name)"
    #FIXME: shall we specify consolidation here, or in DEF.from(v, cf) calls ?
    #cf = None
    #"Consolidation function to use with this variable"
    #"(must exist in related rra)"
    ds = None
    "Datasource object represented"
    rrd = None
    "Related Database object"
    rra = []
    "Related RoundRobinDatabase objects list"
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
#    #FIXME: implement quickly a system of color palette (a color:hex dict):
#    #       this will enable style to specify color names, and apply a palette !
#    #       over-the-top, usage of the palette must be optional for defining style.
#    style = []
#    def __init__(s, ds):
#        pass

# RRD tool abstraction classes
class Database(Component):
    "Represents a rrd database file with its DSes and RRAs"
    "and reflects the rrd create command options."
    name = None
    "Name of the database (ie. {name}.rrd file)"
    _datasources = [] #FIXME: shall it be the object or the object.name string, or both ?
    "DataSource definitions (objects)"
    #FIXME: getter/setter not working properly,
    #       but superseded by class Variable
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
        "Returns the rrdtool create command and arguments"
        args = {arg:getattr(s,arg)
                for arg in ['start', 'step'] if getattr(s, arg)}
        return "create %s %s %s %s" % (
            s.filename(),
            ' '.join(['--%s %s'%(k,v) for k,v in args.items()]),
            ' '.join([str(ds) for ds in s.datasources]),
            ' '.join([str(ds) for ds in s.rrarchives]))
    @staticmethod
    def create(config):
        "Returns an instance from the given config dictionary"
        "(as returned by info())"
        #FIXME: create is a bad name, it can be confused with update/fetch
        import os
        return Database(
            #name = os.path.splitext(os.path.basename(config.get('filename')))[0],
            #FIXME: keep filename path in 'path' variable for name to stay clean ?
            name = os.path.splitext(config.get('filename'))[0],
            ds = [DS.create(name, c) for name,c in config.get('ds').items()],
            rra = [RRA.create(c) for c in config.get('rra')],
            start = config.get('start'),
            step = config.get('step'))
    def filename(s):
        "Returns the database filename"
        return s.name + '.rrd' #FIXME: use os.path
    def update(s, data, timestamp='N'):
        "Updates database using the given dict (use 'U' for unknown values)"
        #FIXME: allow to pass an list of [{timestamp:'N',data:{}}]
        #       so that rrdtool update can be called once
        import collections
        data = collections.OrderedDict(data)
        cmd = 'updatev %s --template %s -- %s:%s' % (
            s.filename(),
            ':'.join([str(k) for k in data]),
            timestamp,
            ':'.join([str(v) for k,v in data.items()]))
        return _call(cmd)
    def fetch(s, cf=None, start=None, end=None, resolution=None):
        "Fetches and returns data from rrd"
        #FIXME: implement remaining command options
        #       iterate kwargs ?
        cf = cf or s.rrarchives[0].cf
        cmd = 'fetch %s %s' % (s.filename(), cf)
        #FIXME: return an array of better data (eg with readable time)
        return _call(cmd)

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
    "Represents a RoundRobinArchive (RRA)"
    #FIXME: Necessary? Are the cli/lib error messages good enough ?
    rows = None
    "Number of rows in the archive"
    "(a row is a slot containing a data; data type is: double)"
    step = None
    "Number of pdp represented by a row"
    xff = None
    "The ratio of allowed unknown pdp data per row (xfile factor)"
    cf = None
    "Consolidation function name. Values: AVERAGE|MIN|MAX|LAST"
    "Used for consolidating a set of PDPs into a rows"
    "The consolidation function to use with the archive"
    "This affects how data is resampled to lower resolutions"
    "and should be chosen according to what you want to track"
    "eg. MIN is you want to track, say, a minimal service level"
    def __init__(s, cf, xff, step, rows):
        s.cf = cf
        s.xff = xff
        s.step = step
        s.rows = rows
    def __str__(s):
        order = ['cf', 'xff','step','rows']
        return 'RRA:%s' % (
            ':'.join([str(getattr(s, arg)) for arg in order]))
    @staticmethod
    def create(config):
        return RoundRobinArchive(
            cf = config.get('cf'),
            #FIXME: a parser function should take care of value format conversion
            #       eg. format(value) - note that it formatting has two directions
            xff = float(config.get('xff').replace(',','.')),
            step = int(config.get('pdp_per_row')),
            rows = int(config.get('rows')))


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
    # All cli options:
    # https://github.com/oetiker/rrdtool-1.x/blob/master/src/rrd_graph.c#L4409
    #FIXME: most of these are style, move them into class GraphStyle
    #       and reference GraphStyle from Graph.style
    args = {
        #'name': here or as class variable ?
        'start': None,
        'end': None,
        'step': None,
        'imgformat': None,
        #Values: PNG|SVG|EPS|PDF
        'border': None,
        #Border width (in pixels)
        'color': {},
        #Graph elements colors, eg. {'CANVAS':'ffaa00', 'GRID':'cc00cc'}
        #BACK background
        #CANVAS:background of the actual graph,
        #FRAME: line around the color spots
        #FONT: font color
        #GRID, MGRID: the (major) grid
        #AXIS graph axish
        #ARROW: xy arrow heads
        #SHADEA: top border
        #SHADEB: right and bottom border
        'slope-mode': None,
        #Enable curving the staircase data, although it is not all true
        'grid-dash': None,
        #Values: on, off
        'watermark': '',
        #String to use for watermark drawing
        'disable-rrdtool-tag': True, #FIXME: set to none by default
        #Hides Tobis credits
        'graph-render-mode': None,
        #Graph antialias ('normal': enabled (default), 'mono': disabled)
        'font-render-mode': None,
        #Font antialias (normal (default), light, mono)
        'zoom': None,
        #Zooms the graph by the given factor (>0)
        'base': None,
        #If you are graphing memory (and NOT network traffic) this switch
        #should be set to 1024 so that one Kb is 1024 byte. For traffic
        #measurement, 1 kb/s is 1000 b/s
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
    #FIXME: bad, unhandy signature
    def __init__(s, data, style, name=None, args={}):
        s.data = data
        s.style = style
        if name: s.name = name
        #FIXME: how to add options in constructor arguments, one by one or a list ?
        s.args = dict(s.args.items() + args.items())
    def __str__(s):
        def f(arg, value):
            return '--%s'%arg if type(value)==bool else '--%s %s'%(arg, value)
        #FIXME: mind the falsy values (eg 0)
        args = [f(arg, s.args.get(arg)) for arg in s.args if s.args.get(arg)]
        return 'graph %s %s %s %s' % (
            s.name,
            ' '.join(args),
            ' '.join([str(data) for data in s.data]),
            ' '.join([str(style) for style in s.style]))
    def draw(s):
        "Returns the graph binary"
        #FIXME: handle options (imageformat, etc.)
        return _call(str(s))

class GraphElement(Component):
    #FIXME: we might use the following common string serializer
    #def __str__(s):
    #    return '%s:%s' % (
    #        s.__class__.__name__,
    #        '...')
    pass

# Below are graph data classes
class GraphData(GraphElement):
    "Base class for graph data definition classes"
    "http://oss.oetiker.ch/rrdtool/doc/rrdgraph_data.en.html"
class DEF(GraphData):
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
    @staticmethod
    def from_variable(variable, config={}):
        "Creates and returns an instance from the given variable and config"
        #FIXME: define what is config
        baseconfig = {
            'vname': variable.vname,
            'rrdfile': variable.rrd.filename(),
            'ds_name': variable.ds.name,
            #FIXME: arbitratily uses the first available RRA
            'cf': variable.rra[0].cf
            #FIXME: also set remaining args, using config ?
        }
        return DEF(**dict(baseconfig.items() + config.items()))
class GraphData_Common():
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
class CDEF(GraphData_Common):
    pass
class VDEF(GraphData_Common):
    pass

# Below are graph style classes
# FIXME: it should be (but it is to complicated, for now Data Def&Style are merged into LINE, AREA,... classes)
# GraphElement
# +-Graph (contains a graph style)
# +-GraphStyle (overall style; graph cmd options: --border, --color, --...)
# +-GraphData
# | +-DEF, CDEF, VDEF
# +-GraphDataStyle
#   +-LINE, AREA, PRINT, etc,
#     #FIXME: me wight separate style and ds-definition, but that's more complexity than benefit.
class GraphStyle(GraphElement):
    "Base class for graph print elements classes"
    "http://oss.oetiker.ch/rrdtool/doc/rrdgraph_graph.en.html"
    args = {}
    order = []
    def __init__(s, args={}):
        s.args = dict(s.args.items() + args.items())
    def __str__(s):
        "Returns a rrdtool-formatted arguments line"
        "Note: if value is falsy, the function returns an empty string"
        "therefore, in order to create arguments with falsy values,"
        "the value must be initialized as a string, eg '0' instead of 0"
        return s.__class__.__name__+reduce(
            lambda x, y: x + y,
            [s.format(arg) for arg in s.order if s.args.get(arg)])
        #return s.__class__.__name__ + ''.join([s.format(arg) for arg in s.order])
        #return reduce(lambda string, arg: string + f(arg, s.args.get(arg)), order, '')
    def format(s, argument_key):
        "Returns a rrdtool-formatted argument and value"
        "from the given argument_key"
        raise NotImplementedError('This method must be implemented by subclasses')
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
        'dash-offset': None
    }
    order = ['width', 'value', 'color', 'legend', 'STACK', 'skipscale', 'dashes', 'dash-offset']
    @staticmethod
    def from_variable(variable, config={}):
        #print __class__ #should be LINE, if so, I can use this for GraphDataStyle.from_variable()
        baseconfig = { 'value': variable.vname } #if 'value' in LINE.args else {}
        return LINE(dict(baseconfig.items() + config.items()))
    def format(s, argument_key):
        #LINE[width]:value[#color][:[legend][:STACK][:skipscale]\
        #[:dashes[=on_s[,off_s[,on_s,off_s]...]][:dash-offset=offset]]
        value = s.args.get(argument_key)
        return {
            'width': '%s' % value,
            'value': ':%s' % value, # mandatory
            'color': '#%s' % value,
            'legend': ':%s' % value,
            'STACK': 'STACK', #FIXME: use lowercase for key ?
            'skipscale': 'skipscale',
            'dashes': ':dashes=%s' % value,
            'dash-offset': ':dashes-offset=%s' % value
        }[argument_key]
    def sapply(s, string):
        import re
        m = re.match(r'LINE(?P<width>\d+|)(:(?P<value>\w+)|)(#(?P<color>[\w\d]+)|)(:(?P<legend>[^:]+)|)(:(?P<STACK>STACK)|)(:(?P<skipscale>skipscale)|)(:dashes=(?P<dashes>\w+)|)(:dash-offset=(?P<dash_offset>\d+)|)', string)
        #FIXME: remove optional surrounding quotes (") from values, does rrd cli allows that ?
        #       same for every GraphStyle.sapply
        args = m.groupdict() if m else {}
        args['dash-offset'] = args.pop('dash_offset')
        args = {k:v if v <> '' else None for k, v in args.items()}
        s.args = dict(s.args.items() + args.items())
        return s

class AREA(GraphStyle):
    args = {
        'value':  None,
        'color':  None,
        'legend': None,
        'STACK': None,
        'skipscale': None
    }
    order = ['value', 'color', 'legend', 'STACK', 'skipscale']
    @staticmethod
    def from_variable(variable, config={}):
        baseconfig = { 'value': variable.vname }
        return AREA(dict(baseconfig.items() + config.items()))
    def format(s, argument_key):
        # AREA:value[#color][:[legend][:STACK][:skipscale]]
        value = s.args.get(argument_key)
        return {
            'value': ':%s' % value,
            'color': '#%s' % value,
            'legend': ':%s' % value,
            'STACK' : 'STACK',
            'skipscale': 'skipscale'
        }[argument_key]
    def sapply(s, string):
        import re
        m = re.match(r'AREA(:(?P<value>\w+)|)(#(?P<color>[\w\d]+)|)(:(?P<legend>[^:]+)|)(:(?P<STACK>STACK)|)(:(?P<skipscale>skipscale)|)', string)
        args = m.groupdict() if m else {}
        args = {k:v if v <> '' else None for k, v in args.items()}
        s.args = dict(s.args.items() + args.items())
        return s

class PRINT(GraphStyle):
    args = {
        'vname': None,
        'format': None,
    }
    order = ['vname', 'format']
    @staticmethod
    def from_variable(variable, config={}):
        baseconfig = { 'vname': variable.vname }
        return PRINT(dict(baseconfig.items() + config.items()))
    def format(s, argument_key):
        # PRINT|GPRINT:vname:format
        value = s.args.get(argument_key)
        return {
            'vname': ':%s' % value,
            'format': ':%s' % value,
        }[argument_key]
class GPRINT(PRINT):
    @staticmethod
    def from_variable(variable, config={}):
        baseconfig = { 'vname': variable.vname }
        return GPRINT(dict(baseconfig.items() + config.items()))
#or class GPRINT(PRINT): pass
#or class GPRINT(GraphStyle):
#    args = {
#        'vname': None,
#        'format': None,
#    }
#class COMMENT(GraphStyle):
#    args = {
#        'text': None,
#    }
class VRULE(GraphStyle):
    args = {
        'time': None,
        'color': None,
        'legend': None,
        'dashes': None,
        'dash-offset': None,
    }
    order = ['time', 'color', 'legend', 'dashes', 'dash-offset']
    @staticmethod
    def from_variable(variable, config={}):
        baseconfig = { 'vname': variable.vname }
        return VRULE(dict(baseconfig.items() + config.items()))
    def format(s, argument_key):
        # VRULE:time#color[:legend][:dashes[=on_s[,off_s[,on_s,off_s]...]]\
        # [:dash-offset=offset]]
        value = s.args.get(argument_key)
        return {
            'time': ':%s' % value,
            'color': '#%s' % value,
            'legend': ':%s' % value,
            'dashes': ':dashes=%s' % value,
            'dash-offset': ':dashes-offset=%s' % value
        }[argument_key]
class HRULE(GraphStyle):
    args = {
        'value': None,
        'color': None,
        'legend': None,
        'dashes': None,
        'dashOffset': None,
    }
    order = ['value', 'color', 'legend', 'dashes', 'dash-offset']
    @staticmethod
    def from_variable(variable, config={}):
        baseconfig = { 'vname': variable.vname }
        return HRULE(dict(baseconfig.items() + config.items()))
    def format(s, argument_key):
        # HRULE:value#color[:legend][:dashes[=on_s[,off_s[,on_s,off_s]...]]\
        # [:dash-offset=offset]]
        value = s.args.get(argument_key)
        return {
            'time': ':%s' % value,
            'color': '#%s' % value,
            'legend': ':%s' % value,
            'dashes': ':dashes=%s' % value,
            'dash-offset': ':dashes-offset=%s' % value
        }[argument_key]
#class TICK(GraphStyle):
#    args = {
#        'vname': None,
#        'color': None,
#        'alpha': None,
#        'fraction': None,
#        'legend': None,
#    }
#class SHIFT(GraphStyle):
#    args = {
#        'vname': None,
#        'offset': None,
#    }
#class TEXTALIGN(GraphStyle):
#    args = {
#        'value': None,
#        #"Values: left|right|justified|center"
#    }


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
    cmd = ['rrdtool'] + argline.split()
    #import subprocess
    #return subprocess.check_output(cmd, shell=False)
    #FIXME
    import subprocess
    process = subprocess.Popen(cmd,
        shell=False,
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE)
    out, err = process.communicate()
    #FIXME: Tobi says that rrdtool doesn't output an exit status,
    #       does it streams to stderr ?
    if (err):
        raise(Exception('%s (%s)' % (err.strip(),
                                     process.returncode)))
    return out
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
#def create(filename, start=None, step=None, overwrite=True, ds=[], rra=[]):
#    pass

# http://oss.oetiker.ch/rrdtool/doc/rrdupdate.en.html
# rrdtool {update | updatev} filename [--template|-t ds-name[:ds-name]...] [--daemon address] [--] N|timestamp:value[:value...] at-timestamp@value[:value...] [timestamp:value[:value...] ...]
# rrdtool update test.rrd 920804700:12345 920805000:12357 920805300:12363
#def update(filename, value, time='N', verbose=False):
#    # rrdtool update filename time:value
#    # use updatev if verbose=True
#    pass

# http://oss.oetiker.ch/rrdtool/doc/rrdfetch.en.html
# rrdtool fetch filename CF [--resolution|-r resolution] [--start|-s start] [--end|-e end] [--daemon address]
# rrdtool fetch test.rrd AVERAGE --start 920804400 --end 920809200
#def fetch(filename, consolidation='AVERAGE', start=None, end=None, resolution=None, daemon=None):
##    pass

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
#def graph(indicators=[], outfile='-', options=[], data=[]):
#    #FIXME: Shall we enumerate all (20+) cli options in the fn signature
#    #       or use a options list ? (with default best options)
#    pass

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
