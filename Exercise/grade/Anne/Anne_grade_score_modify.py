import os
import xlrd
from termcolor import colored
from operator import itemgetter, attrgetter, methodcaller
import sys
sys.path.insert(0,'c:/Python_road/MyPython')
from Exercise.grade.Anne.excel_rw import ExcelRw
from Exercise.grade.Anne.input_check import InputCheck

class KidClass():
    def __init__(self):
        self.book = ["AnneClass.xls", ]
        self.sheet = ["Grade7-1st", "Grade7-2st", "Grade7-3st"]
        self.field_name = ["Number", "Name", "Math", "English", "Chinese", "History", "Geography", "Civic", "Biology",
                           "Total_score", "Ranking"]
        self.name = []
        self.number = []
        self.math = []
        self.english = []
        self.chinese = []
        self.history = []
        self.geography = []
        self.civic = []
        self.biology = []
        self.total_score = []
        self.ranking = []
        self.totaldatalist = [self.number, self.name, self.math, self.english, self.chinese, self.history,
                              self.geography, self.civic, self.biology, self.total_score, self.ranking]
        if not os.path.isfile(self.book[0]):
            ExcelRw.create_tample_file(self.book[0], self.sheet)
            for sheetname in self.sheet:
                for i, field in enumerate(self.field_name):
                    ExcelRw.write(self.book[0], sheetname, 0, i, field)
        self.init_table_for_exist_excel(self.book[0], self.sheet[0])

    def init_table_for_exist_excel(self, excel, excel_sheet):
        rb = xlrd.open_workbook(excel)
        rs = rb.sheet_by_name(excel_sheet)
        for column in range(rs.ncols):
            for i in rs.col_values(column, start_rowx=1):
                self.totaldatalist[column].append(i)

    def input_personal_data(self):
        data_sum = 0
        for i in range(len(self.totaldatalist)):
            if i <= 8:
                while True:
                    data = input(self.field_name[i]+":")
                    if i == 1:
                        if InputCheck.check(data, 1):
                            break
                    else:
                        if InputCheck.check(data, 0):
                            break
                if i <= 1:
                    self.totaldatalist[i].append(str(data))
                else:
                    data_sum += int(data)
                    self.totaldatalist[i].append(int(data))
            elif i == 9:
                self.totaldatalist[i].append(int(data_sum))
            elif i == 10:
                self.totaldatalist[i].append(0)  # fill temp number.
                self.sort_number()

    def show_internal_data(self, who=0xffff):
        """
           parameter:
           who: student location in self.name, 0xffff means show all
        """
        for i in range(len(self.field_name)):
            if who == 0xffff:
                print(self.field_name[i] + ":", self.totaldatalist[i])
            else:
                print(self.field_name[i] + ":", (self.totaldatalist[i])[who])

    def eachclass_status(self):
        print(colored("===== Top scores and the winner =====", "green"))
        for i, school_class in enumerate(self.totaldatalist):
            if 2 <= i <= 9:
                max_index = (self.totaldatalist[i]).index(max(self.totaldatalist[i]))
                print(self.field_name[i], max(self.totaldatalist[i]), "-->" + self.name[max_index])
        print(colored("===== low scores and the loser =====", "green"))
        for i, school_class in enumerate(self.totaldatalist):
            if 2 <= i <= 9:
                min_index = (self.totaldatalist[i]).index(min(self.totaldatalist[i]))
                print(self.field_name[i], min(self.totaldatalist[i]), "-->" + self.name[min_index])
        print(colored("===== average scores =====", "green"))
        for i, school_class in enumerate(self.totaldatalist):
            if 2 <= i <= 9:
                print(self.field_name[i], round(sum(self.totaldatalist[i]) / len(self.totaldatalist[i]), 2))

    def sort_number(self):
        pdata = zip(self.number, self.name, self.math, self.english, self.chinese, self.history, self.geography,
                    self.civic, self.biology, self.total_score)
        total_data_by_p = [j for j in pdata]
        sorted_total_data_by_p = sorted(total_data_by_p, key=itemgetter(9, 4, 2, 1))  # Total, Chinese, Math, English
        for j in range(len(self.name)):
            location = self.name.index(sorted_total_data_by_p[j][1])
            self.ranking[location] = str(len(self.name) - j)

    def list_personal_data(self, student_name):
        upper_name = [name.upper() for name in self.name]
        if student_name.upper() in upper_name:
            print(colored("===== Student's score =====", "green"))
            for i, name in enumerate(self.name):
                if student_name.upper() == name.upper():
                    self.show_internal_data(i)
        else:
            print(colored("No this personal data", "red"))

    def display_sort_by_totalscore(self):
        with open('rank.txt', 'w') as f:
            pdata = zip(self.number, self.name, self.math, self.english, self.chinese, self.history, self.geography,
                        self.civic, self.biology, self.total_score, self.ranking)
            total_data_by_p = [j for j in pdata]
            sorted_total_data_by_p = sorted(total_data_by_p, key = itemgetter(9, 4, 2, 1), reverse = True)  # Total, Chinese, Math, English
            for n in self.field_name:
                print('%10s' % n, end='')
                f.write('%10s' % n)
            print('\n','='*120)
            f.write('\n'+'='*120+'\n')
            for j in range(len(self.name)):
                for k in range(len(self.field_name)):
                    print('%10s' % sorted_total_data_by_p[j][k], end='')
                    f.write('%10s' % sorted_total_data_by_p[j][k])
                print('\n','*'*120)
                f.write('\n'+'*'*120+'\n')

if __name__ == '__main__':
    p = KidClass()
    while True:
        print(colored("=====Welcome to the Kid's data center=====", "blue"))
        print("What do you want to do ? \n"
              "(1) Key in the data of kids\n"
              "(2) List certain student data\n"
              "(3) List the Max, Min, equal \n"
              "(4) List ranking and write to rank.txt \n")
        key = input("Your choice:")
        if InputCheck.check(str(key), 2):
            break

    if key == '1':
        while True:
            print(colored("===Key in personal data===", "blue"))
            p.input_personal_data()
            print("==========================")
            while True:
                esc_key = input("Save and Leave choose 0. [1-9] continue:")
                if InputCheck.check(esc_key, 3):
                    break
            if esc_key == '0':
                ExcelRw.write_table(p.book[0], p.sheet[0], p.totaldatalist)
                break
    elif key == '2':
        while True:
            print(colored("===Which student that you want to check?===", "blue"))
            while True:
                name = input("Name:")
                if InputCheck.check(name, 1):
                    break
            p.list_personal_data(name)
            print("==========================")
            while True:
                esc_key = input("exit choose 0. [1-9] continue:")
                if InputCheck.check(esc_key, 3):
                    break
            if esc_key == '0':
                break
    elif key == '3':
        p.eachclass_status()

    elif key == '4':
        p.display_sort_by_totalscore()
