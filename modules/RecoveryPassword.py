import random, datetime

from modules.sms import SMS
from modules.log import LOG
from modules.strings import SMSS

recovery_codes = {}

def SendSMSTimeCalc():
    sendtime = datetime.datetime.now()
    return sendtime.strftime("%X")

def DeltaTimeCalc(SendSMSTime):
    time = datetime.datetime.now()
    now = time.strftime("%X")
    DeltaTime = int(SendSMSTime.replace(":", "")) - int(now.replace(":", ""))
    return -DeltaTime

def GenCode():
    code = str(random.sample(range(10000, 90000), 1))
    code = code.replace("[", "").replace("]", "")
    return code

def RecPass(phonenumber):
    code = GenCode()
    if not recovery_codes:
        recovery_codes[phonenumber] = {'code': f"{code}", 'sendtime': SendSMSTimeCalc()}
        try:
            SMS.SendSMS(phonenumber, SMSS.RecoveryPassword.value.format(code=code))
        except:
            LOG.error(SMSS.Error.value)
        return True
    else:
        if phonenumber not in recovery_codes:
            recovery_codes[phonenumber] = {'code': f"{code}", 'sendtime': SendSMSTimeCalc()}
            SMS.SendSMS(phonenumber, SMSS.RecoveryPassword.value.format(code=code))
            return True
        else:
            if int(DeltaTimeCalc(recovery_codes[phonenumber]['sendtime']) >= 120):
                recovery_codes.pop(phonenumber)
                code = GenCode()
                recovery_codes[phonenumber] = {'code': f"{code}", 'sendtime': SendSMSTimeCalc()}
                SMS.SendSMS(phonenumber, SMSS.RecoveryPassword.value.format(code=code))
                return True
            else:
                return False