import unittest

from coderack import Rack

class TestRack(unittest.TestCase):

    def test_single(self):
        rack = Rack()
        rack.add("Hi", 1)

        self.assertEquals("Hi", rack.take())
        self.assertEquals(0, len(rack))

    def test_simple_equal_prob(self):
        rack = Rack()

        runs = 1000
        totals = { "10": 0, "10-2" : 0}
        for i in range(0,runs):
            rack.clear()
            rack.add("10",10)
            rack.add("10-2",10)
            val = rack.take()
            totals[val] = totals[val] + 1.0

        pct1 = 100.0 * (totals['10'] / runs)
        pct2 = 100.0 * (totals['10-2'] / runs)
        self.assertTrue(pct1 >= 47 and pct1 <= 53, "Percentages should be about 50/50, not %d" % (pct1,))
        self.assertTrue(pct2 >= 47 and pct2 <= 53, "Percentages should be about 50/50, not %d" % (pct2,))

    def test_higher_range_prob(self):
        """ 
        Test to ensure that even low probability events get taken at the appropriate rates
        """
        rack = Rack()
        runs = 1000
        totals = {"low":0, "mid": 0, "high": 0 }
        for i in range(0, runs):
            rack.clear()
            rack.add("low",1) 
            rack.add("mid",20)
            rack.add("high",79)
            val = rack.take()
            totals[val] = totals[val] + 1.0

        pctLow = 100.0 * (totals['low'] / runs)
        pctMid = 100.0 * (totals['mid'] / runs)
        pctHigh = 100.0 * (totals['high'] / runs)
        self.assertTrue(pctLow > 0 and pctLow <= 5, "Low should be around 1%%, not %d" % (pctLow,))
        self.assertTrue(pctMid > 15 and pctLow <= 25, "Mid should be around 20%% not %d" % (pctMid,))
        self.assertTrue(pctHigh > 75 and pctLow <= 90, "High should be around 80%%, not %d" % (pctHigh,))










if __name__ == '__main__':
        unittest.main()

