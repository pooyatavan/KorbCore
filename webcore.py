import logging, sys, eventlet
from eventlet import wsgi

# no cache files for python
sys.dont_write_bytecode = True

from modules.log import LOG
from modules.Captcha import Captcha
from modules.ConfigReader import Config

LOG.logo()
Captcha.RemoveAllCaptchas()

if Config.read()['log']['clear'] == "enable":
    LOG.clearlogfile()

from modules.FlaskApp import app, FlaskpApp, FlaskSetup

from modules.strings import Console
from modules.tools import network

try:
    if Config.read()['core']['setup'] == "enable":
        FlaskSetup()
        LOG.info(Console.FlaskRunning.value.format(ip=network(), port="80"))
    else:
        FlaskpApp()
        LOG.info(Console.FlaskRunning.value.format(ip=Config.read()['core']['ip'], port=Config.read()['core']['port']))
except:
    LOG.error(Console.FlaskError.value)
else:
    LOG.info(Console.NetworkInfo.value.format(ip=network()))

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    logging.getLogger("waitress.queue").setLevel(logging.ERROR)
    if Config.read()['core']['setup'] == "disable":
        wsgi.server(eventlet.listen((str(Config.read()['core']['ip']), int(Config.read()['core']['port']))), app, log_output=False)
    else:
        wsgi.server(eventlet.listen((str(network()), 80)), app, log_output=False)