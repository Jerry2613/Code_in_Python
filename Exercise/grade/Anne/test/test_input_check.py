import unittest
import sys
sys.path.append("c:\eclipse\MyPython\Exercise\grade\Anne")
print(sys.path)
from input_check import InputCheck


class TestInputCheck(unittest.TestCase):
    def test_checknumber(self):
        data = '100'

        self.assertIsNotNone(InputCheck.check(data, mode=0), 'Number error')

    def test_checkstring(self):
        data = 'Q123ertc'
        self.assertIsNotNone(InputCheck.check(data, mode=1))

    def test_checkmenu(self):
        data = '3'
        self.assertIsNotNone(InputCheck.check(data, mode=2))

    def test_checkleave(self):
        data = '9'
        self.assertIsNotNone(InputCheck.check(data, mode=3))

    def test_checkmaxmode(self):
        data = '0'
        self.assertIsNotNone(InputCheck.check(data, mode=3))

if __name__ == '__main__':
    switch = 3

    if switch == 1:
        suite = unittest.TestSuite()
        suite.addTest(TestInputCheck('test_checknumber'))
        suite.addTest(TestInputCheck('test_checkstring'))
        suite.addTest(TestInputCheck('test_checkmenu'))
        suite.addTest(TestInputCheck('test_checkleave'))
        suite.addTest(TestInputCheck('test_checkmaxmode'))
    elif switch == 2:
        tests = ['test_checknumber', 'test_checkstring', 'test_checkmenu', 'test_checkleave', 'test_checkmaxmode']
        suite = unittest.TestSuite(map(TestInputCheck, tests))
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(TestInputCheck)

    results = unittest.TextTestRunner(verbosity=2).run(suite)
    if not results.wasSuccessful():
        for failure in results.failures:
            print("FAIL", failure[0])
        for error in results.errors:
            print("FAIL", error[0])
