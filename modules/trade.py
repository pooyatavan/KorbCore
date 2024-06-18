import mysql.connector

from modules.soap import SOAPC
from modules.ConfigReader import Config
from modules.strings import SOAPCS, Console
from modules.log import LOG
from modules.strings import MSGList

class trade():
    def __init__(self):
        self.database = 'characters'
        self.host = Config.read()['TC']['ip']
        self.username = Config.read()['TC']['username']
        self.password = Config.read()['TC']['password']
        self.port = Config.read()['TC']['port']
        self.character_tarder = Config.read()['TC']['character_trader']
        try:
            self.character_connection = mysql.connector.connect(host=self.host, database=self.database, user=self.username, password=self.password, port=self.port)
        except:
            LOG.error(Console.ConnSQLError.value.format(ip=self.host))

    def calcgold(self, gold):
        if len(str(gold)) > 4:
            gold = str(gold)[0: int(len(str(gold))) - 4]
            return gold
        else:
            return 0

    def characternames(self, id):
        self.character_connection.reconnect()
        cursor = self.character_connection.cursor()
        cursor.execute(f'SELECT * FROM characters Where guid="{id}"')
        records = cursor.fetchall()
        if not records:
            pass
        else:
            return records[0][2]

    def inmail(self):
        mailgold = []
        allgoldinmail = 0
        try:
            self.character_connection.reconnect()
            cursor = self.character_connection.cursor()
            cursor.execute(f'SELECT * FROM mail Where receiver="{self.character_tarder}"')
            records = cursor.fetchall()
            for row in records:
                mailgold.append({'sender': self.characternames(row[4]), 'money': self.calcgold(row[11])})
                allgoldinmail = allgoldinmail + int(row[11])
            return self.calcgold(allgoldinmail), mailgold
        except:
            LOG.error(MSGList.CoreConnection.value)

    def SendGold(self, character, money):
        SOAPC.Command(SOAPCS.Gold.value.format(character=character, money=money))

    def BuyGold(self):
        pass

Trade = trade()