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

d = rrd.RRD('test',
    [rrd.DataSource('speed', rrd.COUNTER(600))],
    [rrd.RRA('AVERAGE', 0.5, 1, 24)],
    start=920804400)
print d

g = rrd.Graph(
    #FIXME: Data and Style will be expressed with using their own class
    [rrd.GraphData('DEF', ['myspeed=test.rrd','speed','AVERAGE'])],
    [rrd.GraphStyle('LINE2', ['myspeed#FF0000'])]
)
print g
