import logging, sys
from waitress import serve

# no cache files for python
sys.dont_write_bytecode = True

from modules.log import LOG
from modules.Captcha import Captcha
from modules.network import network
from modules.logo import PrintLogo

PrintLogo()
Captcha.RemoveAllCaptchas()
LOG.clearlogfile()

from modules.FlaskApp import app, FlaskpApp
from modules.ConfigReader import Config
from modules.thread import thread
from modules.strings import Console

try:
    thread(FlaskpApp())
except:
    LOG.error(Console.FlaskError.value)
else:
    LOG.info(Console.NetworkInfo.value.format(ip=network()))
    LOG.info(Console.FlaskRunning.value.format(ip=Config.read()['flask']['ip'], port=Config.read()['flask']['port']))

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    logging.getLogger("waitress.queue").setLevel(logging.ERROR)
    serve(app, host=Config.read()['flask']['ip'], port=Config.read()['flask']['port'])