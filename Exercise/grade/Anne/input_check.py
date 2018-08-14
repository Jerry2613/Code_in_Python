import re
from termcolor import colored


class InputCheck:
    number_check = re.compile(r'100|^\d?\d?$')
    name_check = re.compile(r'\w+')
    menu_check = re.compile(r'^[1-4]$')
    leave_check = re.compile(r'^\d$')

    @classmethod
    def check(cls, data, mode=0):
        """
        input:
        mode = 0:number
        mode = 1:string
        mode = 2:menu
        mode = 3:leave check
        output:
        True: match
        False: dismatch
        re.search(pattern, string)  //find one
        re.findall(pattern,string)  //find all
        """
        result = None
        if mode == 0:
            result = cls.number_check.match(data)
        elif mode == 1:
            result = cls.name_check.match(data)
        elif mode == 2:
            result = cls.menu_check.match(data)
        elif mode == 3:
            result = cls.leave_check.match(data)
        else:
            pass

        if result is None:
            print(colored('Unsupported mode or Input wrong data!!!', 'red'))
#        else:
#            print(result, result.group(), result.span(0))
        return result

