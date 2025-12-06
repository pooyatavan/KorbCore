import logging, sys
from gevent.pywsgi import WSGIServer

sys.dont_write_bytecode = True

from modules.log import LOG
from modules.Captcha import Captcha
from modules.ConfigReader import Config
from modules.tools import network, RemoveBOM

LOG.logo()
RemoveBOM()
Captcha.RemoveAllCaptchas()
LOG.clearlogfile()

from modules.FlaskApp import app, FlaskpApp
from modules.strings import Console
from modules.tools import network

try:
    FlaskpApp()
    LOG.info(Console.FlaskRunning.value.format(ip=network(), port=Config.read()['core']['port']))
except:
    LOG.error(Console.FlaskError.value)
else:
    LOG.info(Console.NetworkInfo.value.format(ip=network()))

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    logging.getLogger("waitress.queue").setLevel(logging.ERROR)
    http_server = WSGIServer((network(), int(Config.read()['core']['port'])), app, log=None)
    http_server.serve_forever()