
import random
from string import ascii_uppercase

rooms = {}

def RandomeCode(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        if code not in rooms:
            break
    return code