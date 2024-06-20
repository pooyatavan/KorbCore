import logging, sys, eventlet
from eventlet import wsgi

# no cache files for python
sys.dont_write_bytecode = True

from modules.log import LOG
from modules.Captcha import Captcha

LOG.logo()
Captcha.RemoveAllCaptchas()
LOG.clearlogfile()

from modules.FlaskApp import app, FlaskpApp, FlaskSetup
from modules.ConfigReader import Config
from modules.strings import Console
from modules.tools import network

try:
    if Config.read()['flask']['setup'] == "enable":
        FlaskSetup()
    else:
        FlaskpApp()
except:
    LOG.error(Console.FlaskError.value)
else:
    LOG.info(Console.NetworkInfo.value.format(ip=network()))
    LOG.info(Console.FlaskRunning.value.format(ip=Config.read()['flask']['ip'], port=Config.read()['flask']['port']))

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    logging.getLogger("waitress.queue").setLevel(logging.ERROR)
    wsgi.server(eventlet.listen((str(Config.read()['flask']['ip']), int(Config.read()['flask']['port']))), app, log_output=False)