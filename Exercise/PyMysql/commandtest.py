
class test(object):
    @staticmethod
    def pp(a):
        for b in a:
            print(b)


if __name__ == '__main__':
    c = [0,1,2,3,4,5,6,7,8,9,10]
    c_inter =iter(c)
    for ck in c_inter:
        print(ck)
        if ck == 3:
            test.pp(c_inter)
