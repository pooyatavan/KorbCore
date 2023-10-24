import enum, datetime

from modules.strings import Console

class colors(enum.Enum):
    gray = '\033[90m'
    green =  '\033[32m'
    cyan =  '\x1b[36m'
    red = '\033[31m'
    magenta = '\u001b[35m'
    orange = '\033[0;33m'

class Log:
    def __init__(self):
        self.format = "%d/%m/%Y %H:%M:%S"
        self.date = datetime.datetime.now().strftime(self.format)

    def logfile(self, label, date, msg):
        with open('log.txt', 'a') as file:
            file.writelines(f'{label} {date} {msg} \n')
            file.close()

    def colorized(self, color, msg, label):
        self.logfile(label, self.date, msg)
        return f'{color} {label} {colors.gray.value} {self.date} {msg}'

    def info(self, msg):
        print(self.colorized(colors.green.value, msg, "[INFO]"))
        
    def warning(self, msg):
        print(self.colorized(colors.orange.value, msg, "[WARNING]"))

    def error(self, msg):
        print(self.colorized(colors.red.value, msg, "[ERROR]"))

    def debug(self, msg):
        print(self.colorized(colors.magenta.value, msg, "[DEBUG]"))

    def clearlogfile(self):
        with open('log.txt', 'w'):      
            pass
        LOG.info(Console.LogClrear.value)

LOG = Log()