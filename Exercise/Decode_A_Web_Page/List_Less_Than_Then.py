import random


# write a password generator
# lowercase/uppercase letters,number and symbols
# random .
# include your run-time code in a main method???
# Extra. ask user how strong they want their password to be.
# Fow weak passwords , Pick a word or two from a list???
def generate_number():
    return random.randint(0, 9)

def generate_symbol():
    return random.choice('!@#$%^&*()_+~,./')

def generate_letter(case = 0):
    char = random.choice('qazwsxedcrfvtgbyhnujmikolp')
    if case == 1:
        return char.upper()
    return char


if __name__ == '__main__':
    count = int(input('How many digitals of the password? minimum >=4:'))
    password =[]
    for i in range(count):
        value = i%4
        if value == 0:
            password.append(str(generate_number()))
        elif value == 1:
            password.append(generate_symbol())
        elif value == 2:
            password.append(generate_letter())
        else:
            password.append(generate_letter(1))
    print('Password:', ''.join(password))

