import random

from modules.sql import SQL

class RecruitFreind:
    def __init__(self):
        pass

    def GenerateCode(self, email, accounts):
        if accounts[email]['code'] == "":
            code = str(random.sample(range(1000000000, 9999999999), 1))
            code = code.replace("[", "").replace("]", "")
            SQL.rfcode(email, code)
            return int(code)
        else:
            pass

RF = RecruitFreind()