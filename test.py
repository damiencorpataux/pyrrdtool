import pyrrdtool as rrd

dt = rrd.DataType()
dt.type = 'COUNTER'
dt.args = [600,0,100]
print dt
ds = rrd.DataSource()
ds.name = 'speed'
ds.type = dt
print ds
rra = rrd.RRA() # alias of rrd.RoundRobinArchive()
rra.consolidation = 'AVERAGE'
rra.args = [0.5, 1, 24]
print rra

d = rrd.Database('test', [ds], [rra], start=920804400)
#d.name = 'test'
#d.start = 920804400
#d.datasources = [ds]
#d.rrarchives = [rra]
print d


g = rrd.Graph()
#g.name = 'speed1.png'
print g
