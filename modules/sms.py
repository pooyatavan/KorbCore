import requests

from modules.sql import SQL
from modules.log import LOG
from modules.strings import Console
from modules.ConfigReader import Config

recovery_codes = {}

class sms():
    def __init__(self):
        pass

    # Send Message
    def SendSMS(self, phonenumber, text):
        data = {'from': Config.read()['sms']['number'], 'to': phonenumber, 'text': text}
        response = requests.post('https://console.melipayamak.com/api/send/simple/ab4c3eb2e4504b3ba0d447fca555c728', json=data)

    # Check phonenumber length
    def PhoneNumberCheck(self, phonenumber):
        if len(phonenumber) == 11:
            return True
        else:
            return False

    # Send to every phonenumber in accounts
    def STA(self, text):
        phonenumbers = SQL.ImportNumbers()
        for number in phonenumbers:
            self.SendSMS("0" + str(number), text)
        LOG.debug(Console.STASMS.value.format(contact_count=len(phonenumbers)))

SMS = sms()