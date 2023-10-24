import requests, base64

from modules.ConfigReader import Config
from modules.strings import SOAPCS
from modules.log import LOG

class SOAP:
    def __init__(self):
        self.soapusername = Config.read()['soap']['username']
        self.soappassword = Config.read()['soap']['password']

    def SOAPPasswordGen(self):
        UsernamePassword = f"{self.soapusername}:{self.soappassword}"
        UsernamePassword_bytes = UsernamePassword.encode('ascii')
        base64_bytes = base64.b64encode(UsernamePassword_bytes)
        SOAPPassword = "Basic " + base64_bytes.decode('ascii')
        return SOAPPassword

    def Command(self, ip, command):
        try:
            headers = {'Authorization': SOAP.SOAPPasswordGen(self), 'Content-Type': 'application/xml'}
            payload = f"<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n<SOAP-ENV:Envelope xmlns:SOAP-ENV=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:ns1=\"urn:TC\" xmlns:xsd=\"http://www.w3.org/1999/XMLSchema\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:SOAP-ENC=\"http://schemas.xmlsoap.org/soap/encoding/\" SOAP-ENV:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\">\r\n    <SOAP-ENV:Body>\r\n        <ns1:executeCommand>\r\n            <command>{command}</command>\r\n        </ns1:executeCommand>\r\n    </SOAP-ENV:Body>\r\n</SOAP-ENV:Envelope>"
            response = requests.request("POST", url=SOAPCS.url.value.format(ip=ip), headers=headers, data=payload)
            return True
        except:
            LOG.error(SOAPCS.soaperror.value.format(ip=ip))
            return False

SOAPC = SOAP()