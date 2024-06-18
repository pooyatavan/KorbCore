import random, datetime, hashlib, binascii
from string import ascii_uppercase

from modules.sms import SMS
from modules.log import LOG
from modules.strings import MSGList

recovery_codes = {}

class password():
    def __init__(self):
        self.PasswordSymbols = ["!", "@", "#"]

    def SendSMSTimeCalc(self):
        sendtime = datetime.datetime.now()
        return sendtime.strftime("%X")

    def DeltaTimeCalc(self, SendSMSTime):
        time = datetime.datetime.now()
        now = time.strftime("%X")
        DeltaTime = int(SendSMSTime.replace(":", "")) - int(now.replace(":", ""))
        return -DeltaTime

    def GenCode(self):
        code = str(random.sample(range(10000, 90000), 1))
        code = code.replace("[", "").replace("]", "")
        return code

    def RecPass(self, phonenumber):
        code = self.GenCode()
        if not recovery_codes:
            recovery_codes[phonenumber] = {'code': f"{code}", 'sendtime': self.SendSMSTimeCalc()}
            try:
                SMS.SendSMS(phonenumber, MSGList.RecoveryPassword.value.format(code=code))
            except:
                LOG.error(MSGList.Error.value)
            return True
        else:
            if phonenumber not in recovery_codes:
                recovery_codes[phonenumber] = {'code': f"{code}", 'sendtime': self.SendSMSTimeCalc()}
                SMS.SendSMS(phonenumber, MSGList.RecoveryPassword.value.format(code=code))
                return True
            else:
                if int(self.DeltaTimeCalc(recovery_codes[phonenumber]['sendtime']) >= 120):
                    recovery_codes.pop(phonenumber)
                    code = self.GenCode()
                    recovery_codes[phonenumber] = {'code': f"{code}", 'sendtime': self.SendSMSTimeCalc()}
                    SMS.SendSMS(phonenumber, MSGList.RecoveryPassword.value.format(code=code))
                    return True
                else:
                    return False

    def PasswordChecker(self, password):
        if len(password) > 8:
            for i in self.PasswordSymbols:
                if password.find(i) == -1:
                    return False
                else:
                    return True
        else:
            return False

    def PasswordEqual(self, password, repassword):
        if password == repassword:
            return True
        else:
            return False

    def Generate(self, username, password):
        username = username.upper()
        password = password.upper()
        username = hashlib.sha256(username.encode('utf-8'))
        username = username.hexdigest().upper()
        EmailPassword = username + ":" + password.upper()
        EmailPassword = hashlib.sha256(EmailPassword.encode('utf-8')).hexdigest().upper()
        EmailPassword = binascii.unhexlify(EmailPassword)[::-1]
        FinalPass = str(EmailPassword.hex()).upper()
        return FinalPass
    
Password = password()