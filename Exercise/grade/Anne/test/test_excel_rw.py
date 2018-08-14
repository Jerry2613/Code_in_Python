import unittest
from Exercise.grade.Anne.excel_rw import ExcelRw


class Rxx(unittest.TestCase):
    def test_hi(self):
        print("Rxx:tetst_hi")


class TestExcelRw(unittest.TestCase):
    p = [['J', 1], ['B', 2], ['C', 3]]

    def setUp(self):
        self.filename = 'tabletest.xls'
        self.sheetname = 'hi'

    def test_createfile_ifneed(self):
        ExcelRw.createfile_ifneed(self.filename, self.sheetname)

    #    @unittest.skip('So happy!')
    def test_create_tample_file(self):
        sfilename = 'xxx.xls'
        slist = ['1', '2', '3']
        field_name = ["Number", "Name", "Math", "English", "Chinese", "History", "Geography", "Civic", "Biology",
                      "Total_score", "Ranking"]
        ExcelRw.create_tample_file(sfilename, slist)
        for sheetname in slist:
            for i, field in enumerate(field_name):
                ExcelRw.write(sfilename, sheetname, 0, i, field)

    def test_write(self):
        ExcelRw.write(self.filename, self.sheetname, 4, 4, "See")

    #    @unittest.skip('happy!')
    def test_write_table(self):
        ExcelRw.write_table(self.filename, self.sheetname, TestExcelRw.p)

    def test_read(self):
        cvalue = [ExcelRw.read(self.filename, self.sheetname, r, c) for r in range(2) for c in range(3)]
        print(cvalue)

    def tearDown(self):
        pass


if __name__ == '__main__':
    suite = unittest.TestSuite()
    #    suite.addTest(unittest.makeSuite(Rxx))
    suite.addTest(TestExcelRw('test_create_tample_file'))
    suite.addTest(TestExcelRw('test_createfile_ifneed'))
    suite.addTest(TestExcelRw('test_write'))
    suite.addTest(TestExcelRw('test_write_table'))
    suite.addTest(TestExcelRw('test_read'))

    results = unittest.TextTestRunner(verbosity=2).run(suite)
    print(results)
    if results.wasSuccessful():
        print('Success')
    elif not results.wasSuccessful():
        for failure in results.failures:
            print("FAIL", failure[0])
        for error in results.errors:
            print("FAIL", error[0])
