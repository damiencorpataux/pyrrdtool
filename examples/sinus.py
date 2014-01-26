import pyrrdtool as rrd
import pprint as pp
import time
import math as m
import sys

start_ts = int(time.mktime(time.strptime('01/12/2001', "%d/%m/%Y")))

# Database
d = rrd.RRD('tests/tmp/sinus',
            [rrd.DataSource('speed', rrd.GAUGE(60))],
            [rrd.RRA('AVERAGE', xff=0.5, step=1, rows=60),
             rrd.RRA('AVERAGE', 0.5, 10, 15),
             rrd.RRA('AVERAGE', 0.5, 60, 600)],
             step=60,
             start=start_ts - 1)
print
print "Database definition: %s" % d

print
print "Database creation..."
rrd._call(str(d)) #FIXME: should be rrd.create(str(d))

#print "Created database info:"
#pp.pprint(rrd.info('tests/tmp/update-test.rrd'))

# Data (creates a sinusoidal speed)
print
print "Generating data, please wait... (we're measuring say, a sinus)"
i = 0 #ugly?
for cycle in range(1):
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
        d.update({'speed': sin}, timestamp=timestamp)
print '  Data start: %s' % time.ctime(start_ts)
print '  Data end: %s' % time.ctime(timestamp)

# Graph
speed = rrd.Variable(d, 'speed')
g = rrd.Graph([rrd.DEF.from_variable(speed)],
              [
               rrd.AREA.from_variable(speed, {'color': 'ffffcc'}),
               rrd.LINE.from_variable(speed, {'width': 2, 'color': 'ccff33'}),
              ],
              'tests/tmp/sinus.png', {
                  #FIXME: should rrdtool graph adapt to rrd data timespan ?
                  'start': start_ts,
                  #'start': timestamp - 20000,
                  'end': timestamp
              })
print
print "Graph definition: %s" % g

print
print "Drawing graph in %s..." % g.name
g.draw()

print "Done."
