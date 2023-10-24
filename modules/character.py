import mysql.connector

from modules.ConfigReader import Config
from modules.log import LOG
from modules.strings import Console

# find id of account
class FindCharacters():
    def __init__(self):
        self.username = Config.read()['TC']['username']
        self.password = Config.read()['TC']['password']
        self.port = Config.read()['TC']['port']

    def FindID(self, email, realmip, target):
        try:
            auth_connection = mysql.connector.connect(host=realmip,
                database='auth',
                user=self.username,
                password=self.password,
                port=self.port)
            cursor = auth_connection.cursor()
            cursor.execute(f"SELECT * FROM account WHERE {target}='{email.upper()}'")
            accountdetail = cursor.fetchall()
            auth_connection.disconnect()
            return accountdetail[0][0]
        except:
            LOG.error(Console.ConnSQLError.value.format(ip=realmip))

    #extract character from result
    def ExtractNames(self, characters):
        charactersnames = []
        for character in characters:
            charactersnames.append(character[2])
        return charactersnames

    # find character for specific account
    def FindCharactersNames(self, email, username, realmip, version):
        if int(version.replace(".", "")) > 335:
            id = self.FindID(email, realmip, "email")
        else:
            id = self.FindID(username, realmip, "username")
        try:
            character_connection = mysql.connector.connect(host=realmip,
                database='characters',
                user=self.username,
                password=self.password,
                port=self.port)
            cursor = character_connection.cursor()
            cursor.execute(f"SELECT * FROM characters WHERE account='{id}'")
            characters = cursor.fetchall()
            character_connection.disconnect()
            return self.ExtractNames(characters)
        except:
            LOG.error(Console.ConnSQLError.value.format(ip=realmip))

CharacterFinder = FindCharacters()