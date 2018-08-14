import random


def transfer_number_to_digital_list(number):
    print('Number:', number)
    digital_list = [d for d in number]
    for i in range(4-len(number)):
        digital_list.insert('0')
    print(digital_list)
    return digital_list


# same: bull
# different:cow
def compare_list(target, guess):
    global bulls
    global cows
    for i in range(4):
        if target[i] == guess[i]:
           bulls = bulls + 1
        else:
           cows = cows + 1
    print (cows, 'cows', bulls, 'bulls')
    return True if bulls == 4 else False


if __name__ == '__main__':
    print("Welcome to the Cows and Bulls Game")
    record = []
    i = 0
    target_number_list = transfer_number_to_digital_list(str(random.randint(0, 9999)))
    while True:
        bulls = 0
        cows = 0
        guess_number_list = transfer_number_to_digital_list(input("Enter a number:"))
        status = compare_list(target_number_list, guess_number_list)
        i = i + 1
        record.append(i)
        record.append("".join(target_number_list))
        record.append("".join(guess_number_list))
        record.append(str(bulls)+' bulls '+str(cows)+' cows')
        if status:
            break
    print(record)
