import unittest


class test_myUnitTest(unittest.TestCase):

    def setUp(self):
        print ("****setUP****")
        print ("This will only run once when start-up the test program")
        print ("setUP is normally used to prepare testing data/env")

    def test_case1(self):
        print ("****test case 1P****")
        print ("this is testing case 1")

    def test_case2(self):
        print ("****test case 2P*****")
        print ("this is testing case 2")

    def tearDown(self):
        print ("****tear down****")
        print ("This will only run once while closing the test program")
        print ("tearDown is normally used to release/close system")

if __name__== "__main__":
    unittest.main()
