#FIXME: turn this into a unit test

import pyrrdtool as rrd
import pprint as pp

print; print "# Atomic objects instanciation, parametrization and composition"
ds = rrd.DataSource('speed', rrd.COUNTER(600))
pp.pprint(ds)
print ds

#rra = rrd.RRA() # alias of rrd.RoundRobinArchive()
rra = rrd.RRA('AVERAGE', 0.5, 1, 24)
#rra = rrd.RRA(rra.AVERAGE(0.5, 1, 24))
pp.pprint(ds)
print rra

d = rrd.Database('test', [ds], [rra], start=920804400)
#d.name = 'test'
#d.start = 920804400
#d.datasources = [ds]
#d.rrarchives = [rra]
pp.pprint(d)
print d

print
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
pp.pprint(d)
print d


print; print "# Database metainfo parsing from rrd file"
#pp.pprint(rrd.info_raw('tests/samples/mini.rrd'))
#pp.pprint(rrd.info('tests/samples/mini.rrd'))
info = rrd.info('tests/samples/two-datasources.rrd')
pp.pprint(info)
d = rrd.Database.create(info)
pp.pprint(d)
print d


print; print "# Variable extraction from Database obejct"
speed = rrd.Variable(d, 'speed')
pp.pprint(speed)
print speed.__dict__


print; print "# Base styling components instanciation and parametrization"
print rrd.LINE({'width':2, 'value':'VNAME', 'color': 'ffaacc', 'dashes': 'abc'})
print rrd.AREA({'width':2, 'value':'VNAME', 'color': 'ffaacc', 'dashes': 'abc'})


print; print "# Graph data component test"
speed = rrd.Variable(d, 'speed')
print rrd.DEF.from_variable(speed)


print; print "# Variable styling components test"
print rrd.LINE.from_variable(speed)
print rrd.LINE.from_variable(speed, {'color':'ff0000'})


print; print "# Whole graph command generation"
d = rrd.Database.create(rrd.info('tests/samples/two-datasources.rrd'))
speed = rrd.Variable(d, 'speed')
g = rrd.Graph([
    rrd.DEF.from_variable(speed), #FIXME: find way to specify which CF (from available
                                  #       CFs in rra, or take first found as default ?
], [
    #rrd.GraphStyle('LINE2', ['myspeed#FF0000']),
    rrd.LINE.from_variable(speed, {'width':2, 'color': 'aacc00'})
])
print g


print; print "# Graph binary"
#print g.draw()

g.name = 'tests/tmp/g.png'
g.args['border'] = '0'
print g


print; print "# Error catching test"
try:
    d = rrd.Database.create(rrd.info('tests/samples/mini.rrd'))
    print d.update({'ds_name': 'value', 'b': 2})
except Exception, e:
    print 'Catched exception:', e


print; print "# Database values update"
import time
start_ts = int(time.mktime(time.strptime('01/12/2001', "%d/%m/%Y")))
d = rrd.RRD('tests/tmp/update-test',
            [rrd.DataSource('speed', rrd.GAUGE(60))],
            [rrd.RRA('AVERAGE', xff=0.5, step=1, rows=60),
             rrd.RRA('AVERAGE', 0.5, 10, 15),
             rrd.RRA('AVERAGE', 0.5, 60, 600)],
             step=60,
             start=start_ts - 1)
print d
print rrd._call(str(d))
pp.pprint(rrd.info('tests/tmp/update-test.rrd'))
#d = rrd.Database.create(rrd.info('tests/tmp/update-test.rrd'))
print d
# Creates a sinusoidal speed
import math as m
import sys
i = 0 #ugly?
for cycle in range(2):
    for degree in range(360):
        # Timestamp
        i += 1
        delta = i * d.step
        timestamp = start_ts + delta
        # Sinus value 
        amp = 1000
        sin = int(amp + (amp * m.sin(m.radians(degree))))
        # Update
        #print "Update:", i, timestamp, time.ctime(timestamp), sin
        sys.stdout.write('.')
        d.update({'speed': sin}, timestamp=timestamp)
print
print 'Data start:', time.ctime(start_ts)
print 'Data end:', time.ctime(timestamp)

# Creates graph
speed = rrd.Variable(d, 'speed')
g = rrd.Graph([rrd.DEF.from_variable(speed)],
              [
               rrd.AREA.from_variable(speed, {'color': 'ffffcc'}),
               rrd.LINE.from_variable(speed, {'width': 2, 'color': 'ccff33'}),
              ],
              'g.png', {
                  #FIXME: should rrdtool graph adapt to rrd data timespan ?
                  'start': start_ts,
                  #'start': timestamp - 20000,
                  'end': timestamp
              })
print g
g.draw()


#print; print "# Database fetch"
#print d.fetch()
