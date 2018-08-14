import os
import sys
import random
from pprint import pprint

import re


class Table9Class():
    def multi(self, print_number, group_times):
        row_number = 0
        with open('9x9.txt', 'w') as f:
            for times in range(group_times):
                unit = []
                total_number = 0
                print("="*80)
                f.write("="*80+"\n")
                for k in range(1000):
                    i = random.randint(2,9)
                    j = random.randint(2,9)
                    if (i,j) in unit:
                        continue
                    if total_number == print_number:
                        break
                    total_number += 1
                    unit.append((i,j))
                    row_number += 1
                    print (i,"x", j,"=", end=" ")
                    f.write(str(i)+" x "+str(j)+" =          ")
                    if row_number == 5:
                        print(end="\n")
                        f.write('\n')
                        row_number = 0


if __name__ == '__main__':
    p = Table9Class()
    p.multi(40, 4)
