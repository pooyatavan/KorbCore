import mysql.connector

from modules.ConfigReader import Config
from modules.strings import MSGList

class skillstructure():
    def __init__(self):
        self.username = Config.read()['TC']['username']
        self.password = Config.read()['TC']['password']
        self.port = Config.read()['TC']['port']

    def ProfessionSkillUpdate(self, idcharacter, idwork, maxskill, realmip):
        character_connection = mysql.connector.connect(host=realmip, database='characters', user=self.username, password=self.password, port=self.port)
        cursor = character_connection.cursor()
        cursor.execute(f"UPDATE character_skills SET value='{maxskill}' WHERE guid={idcharacter} and skill={idwork}")
        character_connection.commit()
        cursor.execute(f"UPDATE character_skills SET max='{maxskill}' WHERE guid={idcharacter} and skill={idwork}")
        character_connection.commit()

    def CheckCharacterLevel(self, charactername, realmip, maxlevel):
        character_connection = mysql.connector.connect(host=realmip, database='characters', user=self.username, password=self.password, port=self.port)
        cursor = character_connection.cursor()
        cursor.execute(f'SELECT * FROM characters Where name="{charactername}"')
        records = cursor.fetchall()
        if records[0][6] == int(maxlevel):
            return records[0][0]
        else:
            return False

    def CheckCharacterOffline(self, charactername, realmip):
        character_connection = mysql.connector.connect(host=realmip, database='characters', user=self.username, password=self.password, port=self.port)
        cursor = character_connection.cursor()
        cursor.execute(f'SELECT * FROM characters Where name="{charactername}" and online="0"')
        records = cursor.fetchall()
        if records == []:
            return False
        else:
            return True

    def CheckCharacterProfessions(self, idcharacter, realmip, workid):
        character_connection = mysql.connector.connect(host=realmip, database='characters', user=self.username, password=self.password, port=self.port)
        cursor = character_connection.cursor()
        cursor.execute(f'SELECT * FROM character_skills Where skill="{workid}" and guid={idcharacter}')
        records = cursor.fetchall()
        if records == []:
            return False
        else:
            return True

    def SetProfessionSkill(self, charactername, workid, skill, realmip, maxlevel):
        if self.CheckCharacterOffline(charactername, realmip) == True:
            res = self.CheckCharacterLevel(charactername, realmip, maxlevel)
            if type(res) == bool:
                if res == False:
                    return MSGList.CharacterLevel.value.format(level=maxlevel)
            else:
                if self.CheckCharacterProfessions(res, realmip, workid) == True:
                    self.ProfessionSkillUpdate(res, workid, skill, realmip)
                    return True
                else:
                    return MSGList.Profession.value
        else:
            return MSGList.CharacterOnline.value

    def SetRepSkill(self, idcharacter, realmip, itemid, maxskill):
        character_connection = mysql.connector.connect(host=realmip, database='characters', user=self.username, password=self.password, port=self.port)
        cursor = character_connection.cursor()
        cursor.execute(f"UPDATE character_reputation SET standing='{maxskill}', flags='{17}' WHERE guid={idcharacter} and faction={itemid}")
        character_connection.commit()

    def SetReputationSkill(self, realmip, charactername, maxlevel, itemid, maxskill):
        if self.CheckCharacterOffline(charactername, realmip) == True:
            res = self.CheckCharacterLevel(charactername, realmip, maxlevel)
            if type(res) == bool:
                if res == False:
                    return MSGList.CharacterLevel.value.format(level=maxlevel)
            else:
                self.SetRepSkill(res, realmip, itemid, maxskill)
                return True
        else:
            return MSGList.CharacterOnline.value

SkillStructure = skillstructure()