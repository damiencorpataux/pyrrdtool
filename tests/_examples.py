import unittest
#import pyrrdtool as rrd
import pprint as pp
import os

class Examples(unittest.TestCase):
    """
    Examples testing
    """

    def test_sinus(self):
        from examples import sinus
        print sinus.g.name
        self.assertEqual(os.path.getsize(sinus.g.name), 6094)

if __name__ == '__main__':
    unittest.main()
