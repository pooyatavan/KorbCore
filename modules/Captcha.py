from captcha.image import ImageCaptcha
import random, os.path, shutil

from modules.strings import Console
from modules.ConfigReader import Config
from modules.log import LOG

Captchas = {}

class captcha():
    def __init__(self):
        if Config.read()['captcha']['latin'] == "no":
            self.imageconfig = ImageCaptcha(width= int(Config.read()['captcha']['width']), height= int(Config.read()['captcha']['height']), fonts=['static/css/shabnam.woff'])
        else:
            self.imageconfig = ImageCaptcha(width= int(Config.read()['captcha']['width']), height= int(Config.read()['captcha']['height']))
        self.path = "static/captcha/"

    def gencode(self):
        return str(random.sample(range(int(Config.read()['captcha']['rangestart']), int(Config.read()['captcha']['rangeend'])), 1)).replace("[", "").replace("]", "")

    def generateimage(self, ip):
        if ip not in Captchas:
            code = self.gencode()
            Captchas[ip] = {'code': code}
            self.imageconfig.generate(code)
            filename = os.path.join(self.path, ip + ".png")  
            self.imageconfig.write(code, filename)

    def regenerateimage(self, ip):
        code = self.gencode()
        Captchas[ip] = {'code': code}
        self.imageconfig.generate(code)
        filename = os.path.join(self.path, ip + ".png")  
        self.imageconfig.write(code, filename)
        
    def removecaptcha(self, ip):
        try:
            if ip in Captchas:
                Captchas.pop(ip)
                os.remove(f"{self.path}{ip}.png")
        except:
            pass

    def CompareCaptcha(self, code, ip):
        if ip not in Captchas:
            return False
        else:
            if code == Captchas[ip]['code']:
                self.removecaptcha(ip)
                return True
            else:
                return False

    def RemoveAllCaptchas(self):
        for filename in os.listdir(self.path):
            file_path = os.path.join(self.path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        LOG.info(Console.RemoveAllCaptchas.value)

Captcha = captcha()