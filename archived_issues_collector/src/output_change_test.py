import unittest
import sys
import os
import logging
sys.path.append(os.path.dirname(__file__))
import output_changes

logging.basicConfig(filename="out/test.log",
                    format='%(asctime)s [%(levelname)s] (%(funcName)s) %(message)s',
                    filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class TestOutput(unittest.TestCase):
    def test_version(self):
        logger.debug('running test version')
        ret = output_changes.isVersionInRange(0,
        '0.99.914a7', '0.99.913', '0.99.914')
        logger.debug('ret %d' % ret)
        self.assertEqual(ret, output_changes.VersionCompareResult.RightWithinRange)

class TestOutput(unittest.TestCase):
    def test_version(self):
        logger.debug('running test version')
        ret = output_changes.isVersionInRange(0,
        '0.99.914a7', '0.99.913', '0.99.914a10')
        logger.debug('ret %d' % ret)
        self.assertEqual(ret, output_changes.VersionCompareResult.RightWithinRange)


if __name__ == '__main__':
    logger.debug('test starts')
    unittest.main()