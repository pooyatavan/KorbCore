import random, os.path, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from modules.strings import Console
from modules.ConfigReader import Config
from modules.log import LOG

Captchas = {}

class captcha():
    def __init__(self):
        if Config.read()['captcha']['latin'] == "disable":
            pass
        else:
            pass
        self.path = os.path.join(os.getcwd(), 'static\\captcha\\')
        if os.path.isdir(self.path):
            pass
        else:
            Path(self.path).mkdir()

    def GenCode(self):
        return str(random.sample(range(int(Config.read()['captcha']['rangestart']), int(Config.read()['captcha']['rangeend'])), 1)).replace("[", "").replace("]", "")

    def GenImage(self, ip, code):
        width = int(Config.read()['captcha']['width'])
        height = int(Config.read()['captcha']['height'])
        img = Image.new("RGB", (width, height), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("static/css/conduit.ttf", int(Config.read()['captcha']['fontsize']))
        except OSError:
            font = ImageFont.load_default()
        text_color = (255, 255, 255)
        bbox = draw.textbbox((0, 0), code, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        draw.text((x, y), code, fill=text_color, font=font)
        img.save(os.path.join(self.path, f"{ip}.png"))

    def GenCaptcha(self, ip):
        if ip not in Captchas:
            code = self.GenCode()
            Captchas[ip] = {'code': code}
            self.GenImage(ip, code)

    def RegenCaptcha(self, ip):
        code = self.GenCode()
        Captchas[ip] = {'code': code}
        self.GenImage(ip, code)

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
        dir = os.listdir(self.path) 
        if len(dir) == 0: 
            pass
        else: 
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