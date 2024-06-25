import mysql.connector

from modules.ConfigReader import Config
from modules.sql import SQL
from modules.log import LOG
from modules.strings import Console

if Config.read()['core']['setup'] == "disable":
    realmlists = SQL.ReadRealms()
else:
    realmlists = []
    
def RealmFlagCheck(flag):
    if int(flag) == 66:
        return "Offline"
    elif int(flag) == 0:
        return "Online"
    elif int(flag) == 128:
        return "Full"
    elif int(flag) == 32:
        return "New Players"
    elif int(flag) == 2:
        return "Offline"
    elif int(flag) == 64:
        return "Recommended"

def ExpansionCheck(expanstion):
    if str(expanstion) == "12340":
        return "3.3.5"
    elif str(expanstion) == "15595":
        return "4.3.4"
    elif str(expanstion) == "8606":
        return "2.4.3"
    elif str(expanstion) == "6005":
        return "1.12.2"

def PopulationCheck(value):
    if value == "0.0" or "0":
        return "Low"
    elif value == "0.5":
        return "Low"
    elif value == "1.0":
        return "Medium"
    elif value == "2.0":
        return "High"

def IconCheck(icon):
    if icon == 4 or 0:
        return "Normal"
    elif icon == 1:
        return "PVP"

def RealmCheck():
    realms = []
    if Config.read()['TC']['scan_realm'] == "on":
        for row in realmlists:
            try:
                realmcon = mysql.connector.connect(host=realmlists[row]['localip'], database='auth', user=Config.read()['TC']['username'], password=Config.read()['TC']['password'])
                if realmcon.is_connected():
                    cursor = realmcon.cursor()
                    cursor.execute('SELECT * FROM realmlist')
                    records = cursor.fetchall()
                    for id, roww in enumerate(records):
                        realms.append({'name': records[id][1],
                        'address': records[id][2],
                        'status': RealmFlagCheck(records[id][7]),
                        'population': PopulationCheck(records[id][10]),
                        'expansion': ExpansionCheck(records[id][11]),
                        'icon': IconCheck(records[id][6]),
                        'domain': realmlists[row]['domain']})
                        realmcon.disconnect()
            except:
                LOG.error(Console.RealmFailed.value.format(ip=row))
    else:
        realms.append({'name': "Disable", 'address': "Disable", 'status': "Disable", 'population': "Disable", 'expansion': "Disable", 'icon': "Disable", 'domain': "Disable"})
        return realms