import configparser

class config():
    def __init__(self):
        self.config = configparser.ConfigParser()

    def read(self):
        self.config.read('config.ini')
        return self.config

    def write(self, title, subject, value):
        self.config.set(f'{title}', f'{subject}', f'{value}')
        with open('config.ini', 'w') as ConfigFile:
            self.config.write(ConfigFile)

Config = config()