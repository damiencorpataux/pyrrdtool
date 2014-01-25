#FIXME: turn this into a unit test

import pyrrdtool as rrd
import pprint as pp

print; print "# Atomic objects instanciation, parametrization and composition"

ds = rrd.DataSource('speed', rrd.COUNTER(600))
pp.pprint(ds)

#rra = rrd.RRA() # alias of rrd.RoundRobinArchive()
rra = rrd.RRA('AVERAGE', 0.5, 1, 24)
#rra = rrd.RRA(rra.AVERAGE(0.5, 1, 24))
print rra

d = rrd.Database('test', [ds], [rra], start=920804400)
#d.name = 'test'
#d.start = 920804400
#d.datasources = [ds]
#d.rrarchives = [rra]
print d


print "(one round database instance definition)"
#FIXME: And then create an json api to explore arbitrary rrd files definitions
#       showing their DSes/DST, RRAs config
#       and even a overview of the data using rrdtool fetch
d = rrd.RRD('test',
    [
        rrd.DataSource('speed', rrd.COUNTER(600)),
        rrd.DataSource('speed_max', rrd.COMPUTE('speed,MAX')),
    ],
    [rrd.RRA('AVERAGE', 0.5, 1, 24)],
    start=920804400)
print d


print; print "# Database metareading"
#pp.pprint(rrd.info_raw('tests/samples/mini.rrd'))
#pp.pprint(rrd.info('tests/samples/mini.rrd'))
info = rrd.info('tests/samples/two-datasources.rrd')
pp.pprint(info)
d2 = rrd.Database.create(info)
print d2
#pp.pprint(d2)


print; print "# Variable extraction from Database obejct"
speed = rrd.Variable(d2, 'speed')
print speed


print; print "# Base styling components instanciation and parametrization"
print rrd.LINE({'width':2, 'value':'VNAME', 'color': 'ffaacc', 'dashes': 'abc'})
print rrd.AREA({'width':2, 'value':'VNAME', 'color': 'ffaacc', 'dashes': 'abc'})


print; print "# Graph data component test"
speed = rrd.Variable(d2, 'speed')
print rrd.DEF.from_variable(speed)


print; print "# Variable styling components test"
print rrd.LINE.from_variable(speed)
print rrd.LINE.from_variable(speed, {'color':'ff0000'})


print; print "# Whole graph command generation"
g = rrd.Graph(
    [
        rrd.DEF.from_variable(speed), #FIXME: find way to specify which CF (from available
                      #       CFs in rra, or take first found as default ?
    ],
    [
        #rrd.GraphStyle('LINE2', ['myspeed#FF0000']),
        rrd.LINE.from_variable(speed, {'width':2, 'color': 'aacc00'})
    ]
)
print g


print; print "# Graph binary"
g.draw()

g.name = 'g.png'
g.args['border'] = '0'
print g
g.draw()
