# General
- "rrd does always preserve the area under the graph"
  i.e. it is coherent with the integrale (see tobi video to rephrase better)

# Performance

- About performance of graphing (important)
  http://youtu.be/JaK-IctEyWs?t=51m39s

- Use multiple datasources in the same rrdb
  as much as possible: it reduces the disk io
  but you have to acquire and update at the same time
  (and cost as much as one datasource update in disk io time)

- rrd structures can be modified by dumping data, recreating
  and reimporting dumped data 
  rdchick? from tobi 

- rrdb size has no impact on update performance
  (same amount of time)

- on the other hand, the *number* of rra affects update performance
  because the disk heads have to go from one archive to the next one,
  which are stored sequentially (ssd exclude this issue)

- 
