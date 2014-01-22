#FIXME: turn this into a unit test

import pyrrdtool as rrd

ds = rrd.DataSource('speed', rrd.COUNTER(600))
print ds

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

print

#FIXME: Quickly implement a database loading function to create a
#       database object fully configured by using rddtool info file.rrd
#       this is neat! for quickly drawing graphs !
#FIXME: And then create an json api to explore arbitrary rrd files definitions
#       showing their DSes/DST, RRAs config
#       and even a overview of the data using rrdtool fetch
d = rrd.RRD('test',
    [rrd.DataSource('speed', rrd.COUNTER(600))],
    [rrd.RRA('AVERAGE', 0.5, 1, 24)],
    start=920804400)
print d

#FIXME: it should not be necessary to get ds though rrd.datasource()
#       because the backrefs to rrd & rra should be done by RRD.setter()
#ds = rrd.datasources()['speed']
ds = rrd.Variable(d, 'speed')
import pprint as pp
#pp.pprint(ds.__dict__)

g = rrd.Graph(
    #FIXME: Data and Style will be expressed with using their own class
#    [rrd.GraphData('DEF', ['myspeed=test.rrd','speed','AVERAGE'])],
    [
        rrd.eDEF(ds), #FIXME: find way to specify which CF
    ],
    #FIXME: same as Data
    [rrd.GraphStyle('LINE2', ['myspeed#FF0000'])]
)
print g
