#FIXME: see if we shall use doctest

import unittest
import pyrrdtool as rrd
import pprint as pp

class Component_sapply(unittest.TestCase):
    """
    Tests all possible GraphStyle subclasses
    Tests all possible GraphStyle arguments combinaisons
    Tests all allowed GraphStyle arguments characters (FIXME:TODO)
    Failtests the test procedure
    """

    def apply_test(self, cls, tests):
        # Test
        for line, expected_args in tests:
            expected = dict(cls.args.items() + expected_args.items())
            config = cls.sapply(cls(), line).args
            self.assertDictEqual(expected, config,
                                 "Parser failed.\nExpected: %s\nGot: %s"
                                 % (pp.pformat(expected), pp.pformat(config)))
        # Failtest
        expected = dict(rrd.LINE.args.items() + {}.items())
        config = rrd.LINE.sapply(rrd.LINE(), 'LINE:speed').args
        with self.assertRaises(AssertionError):
            self.assertDictEqual(expected, config)

    def test_LINE(self):
        # Test definitions: a list of ('cli-line-string', {expected-args})
        tests = [
            ('LINE', #FIXME: this is probably invalid in rrdtool
             {}),
            ('LINE:speed',
             {'value': 'speed'}),
            ('LINE2:speed',
             {'width': '2', 'value': 'speed'}),
            ('LINE2:speed:legend',
             {'width': '2', 'value': 'speed', 'legend': 'legend'}),
            ('LINE2:speed#ccff33:legend',
             {'width': '2', 'value': 'speed', 'color': 'ccff33', 'legend': 'legend'}),
            ('LINE2:speed#ccff33:legend:STACK',
             {'width': '2', 'value': 'speed', 'color': 'ccff33', 'legend': 'legend', 'STACK': 'STACK'}),
            #...
            ('LINE2:speed#ccff33:legend:STACK:skipscale:dashes=on_s:dash-offset=10',
             {'width': '2', 'value': 'speed', 'color': 'ccff33', 'legend': 'legend',
              'STACK': 'STACK', 'skipscale': 'skipscale', 'dashes':'on_s', 'dash-offset': '10'}),
            # Non sequential args, FIXME: fails
            ('LINE2:speed:STACK',
             {'width': '2', 'value': 'speed', 'STACK': 'STACK'}),
            ('LINE2:speed:dash-offset=10',
             {'width': '2', 'value': 'speed', 'dash-offset': '10'}),
        ]
        self.apply_test(rrd.LINE, tests)

    def test_AREA(self):
        # Test definitions: a list of ('cli-line-string', {expected-args})
        tests = [
            ('AREA:vname',
             {'value': 'vname'}),
            ('AREA:vname#aabbcc',
             {'value': 'vname', 'color': 'aabbcc'}),
            ('AREA:vname#aabbcc:mylegend',
             {'value': 'vname', 'color': 'aabbcc', 'legend': 'mylegend'}),
            ('AREA:vname#aabbcc:mylegend:skipscale',
             {'value': 'vname', 'color': 'aabbcc', 'legend': 'mylegend', 'skipscale': 'skipscale'}),
            ('AREA:vname:mylegend',
             {'value': 'vname',  'legend': 'mylegend'}),
            # Non sequential args, FIXME: fails
            ('AREA:vname:STACK',
             {'value': 'vname',  'STACK': 'STACK'}),
        ]
        self.apply_test(rrd.AREA, tests)

if __name__ == '__main__':
    unittest.main()

#FIXME
# DS:speed:COUNTER:600:U:U
# RRA:AVERAGE:0.5:1:24
# create test.rrd --start 920804400 DS:speed:COUNTER:600:U:U DS:speed_max:COMPUTE:speed,MAX RRA:AVERAGE:0.5:1:24
# DEF:speed=tests/tmp/update-test.rrd:speed:AVERAGE
# AREA, PRINT, GPRINT, HRULE, VRULE, ...
# graph g.png --end 1007204400 --start 1007161200 --disable-rrdtool-tag DEF:speed=tests/tmp/update-test.rrd:speed:AVERAGE AREA:speed#ffffcc LINE2:speed#ccff33
