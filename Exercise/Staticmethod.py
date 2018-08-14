class A(object):
    bar = 1
    def foo(selfself):
        print ('foo')

    @staticmethod
    def static_foo():
        print ('static_foo')
        print (A.bar)

    @classmethod
    def class_foo(cls):
        print ('class_foo')
        print (cls.bar)
        cls().foo()


A.static_foo()
A.class_foo()

