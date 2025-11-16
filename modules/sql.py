import mysql.connector, time, sys

from modules.ConfigReader import Config
from modules.strings import Console, MSGList
from modules.log import LOG
from modules.tools import TimeDo

accounts = {}
store = []
redeemcodes = {}
history = []
navlinks = {}
blogs = {}
homewidth = {}
phonenumbers = []
statics = {}
versions = []
bugs = {}
navigation = []
language = {}

class sql():
    def __init__(self):
        if Config.read()['core']['setup'] == "disable":
            try:
                self.webcore = mysql.connector.connect(host=Config.read()['webdb']['ip'],
                    database='webcore',
                    user=Config.read()['webdb']['username'],
                    password=Config.read()['webdb']['password'],
                    port=Config.read()['webdb']['port'])
                self.cursor = self.webcore.cursor()
            except:
                LOG.error(Console.ConnSQLError.value.format(ip=Config.read()['webdb']['ip']))
                sys.exit(1)

    def empty(self, value):
        if value == 0:
            return ""
        else:
            return value

    def InvertIDict(self, dic): 
        return dict(reversed(list(dic.items())))

    def ReadAccounts(self):
        start = time.perf_counter()
        self.cursor.execute('SELECT * FROM users')
        for row in self.cursor:
            accounts[row[3]] = {
            'firstname': row[1],
            'lastname': row[2],
            'email': row[3],
            'password': row[4],
            'token': row[5],
            'gold': row[6],
            'regdate': str(row[7]),
            'status': row[8],
            'phonenumber': row[9],
            'username': row[10],
            'code': self.empty(row[11]),
            'count': row[12],
            'recover': "0",
            'characters': [],
            'rank': row[13]}
        LOG.info(Console.Load.value.format(number=len(accounts), table="users", time=TimeDo(start)))
        return accounts

    def ImportNumbers(self):
        self.webcore.reconnect()
        cursor = self.webcore.cursor()
        cursor.execute('SELECT * FROM users')
        for row in cursor:
            if row[9] in phonenumbers:
                pass
            else:
                phonenumbers.append(row[9])
        return phonenumbers
        
    def StoreItems(self):
        start = time.perf_counter()
        self.cursor.execute('SELECT * FROM store')
        for row in self.cursor:
            store.append({
            'id': int(row[0]) - 1,
            'image': row[1],
            'token': row[2],
            'detail': row[3],
            'title': row[4],
            'mode': row[5],
            'version': row[7],
            'itemid': row[8],
            'service': row[9],
            'maxskill': row[10]})
        LOG.info(Console.Load.value.format(number=len(store), table="store", time=TimeDo(start)))
        return store

    def ReadRedeemCode(self):
        start = time.perf_counter()
        self.cursor.execute('SELECT * FROM redeemcode')
        for row in self.cursor:
            redeemcodes[row[0]] = {'codes': row[0],
            'usedto': row[1]}
        LOG.info(Console.Load.value.format(number=len(redeemcodes), table="redeemcodes", time=TimeDo(start)))
        return redeemcodes

    def ReadRealms(self):
        start = time.perf_counter()
        realmlists = {}
        self.cursor.execute('SELECT * FROM realmaddress')
        for row in self.cursor:
            realmlists[row[2]] = {'localip': row[1], 'maxskill': row[3], 'maxlevel': row[4], 'domain': row[5]}
        LOG.info(Console.Load.value.format(number=len(realmlists), table="realmlist", time=TimeDo(start)))
        return realmlists

    def ReadLinks(self):
        start = time.perf_counter()
        self.webcore.reconnect()
        self.cursor.execute('Select * From navlinks')
        for row in self.cursor:
            #navlinks[row[1]] = {'href': row[1],'title': row[2], 'pos': row[3], 'name': row[4]}
            navigation.append({'href': row[1],'title': row[2], 'pos': row[3], 'name': row[4]})
        LOG.info(Console.Load.value.format(number=len(navlinks), table="navlinks", time=TimeDo(start)))
        return navlinks, navigation

    def ReadArtciles(self):
        start = time.perf_counter()
        self.webcore.reconnect()
        self.cursor.execute(f'SELECT * FROM news')
        for row in self.cursor:
            if row[5] == "blog":
                blogs[row[8]] = {'title': row[1],
                'by': row[2],
                'newsdate': row[3],
                'article': row[4],
                'image': row[6],
                'link': row[8],
                'exclusive': row[9],
                'short': row[10],
                'type': row[5]}
            
            elif row[5] == "static":
                statics[row[8]] = {'title': row[1],
                'by': row[2],
                'newsdate': row[3],
                'article': row[4],
                'image': row[6],
                'link': row[8],
                'exclusive': row[9],
                'short': row[10],
                'type': row[5]}
                
            elif row[5] == "home":
                homewidth[row[7]] = {'title': row[1],
                'by': row[2],
                'newsdate': row[3],
                'article': row[4],
                'image': row[6],
                'link': row[8],
                'exclusive': row[9],
                'detail': row[4],
                'type': row[5]}
        self.webcore.disconnect()
        return statics, self.InvertIDict(blogs), homewidth

    def ReadVersions(self):
        self.webcore.reconnect()
        start = time.perf_counter()
        self.cursor.execute('SELECT * FROM versions')
        for row in self.cursor:
            versions.append(row[1])
        LOG.info(Console.Load.value.format(number=len(redeemcodes), table="redeemcodes", time=TimeDo(start)))
        return versions

    def ReadBugs(self):
        start = time.perf_counter()
        self.cursor.execute('SELECT * FROM bugs')
        for row in self.cursor:
            bugs[row[4]] = {'kind': row[1], 'detail': row[2], 'status': row[3], 'user': row[4]}
        LOG.info(Console.Load.value.format(number=len(bugs), table="bugs", time=TimeDo(start)))

    def ReadLanguage(self):
        start = time.perf_counter()
        self.cursor.execute('SELECT * FROM language')
        for row in self.cursor:
            language[row[0]] = {'name': row[2], 'language': row[1]}
        LOG.info(Console.Load.value.format(number=len(bugs), table="Language", time=TimeDo(start)))
        return language

    def homewidth(self, where, target):
        start = time.perf_counter()
        self.webcore.reconnect()
        self.cursor.execute(f'SELECT * FROM news Where {where}="{target}"')
        for row in self.cursor:
            if row[5] == "home":
                homewidth[row[1]] = {
                'title': row[1],
                'by': row[2],
                'newsdate': row[3],
                'detail': row[4],
                'image': row[6],
                'tools': row[7]}
        self.webcore.disconnect()
        return homewidth

    def GetBuyHistory(self, email, rank):
        start = time.perf_counter()
        self.webcore.reconnect()
        if int(rank) == 3:
            self.cursor.execute(f'SELECT * FROM history')
            history = self.cursor.fetchall()
        else:
            self.cursor.execute(f'SELECT * FROM history Where email="{email}"')
            history = self.cursor.fetchall()
        self.webcore.disconnect()
        LOG.info(Console.Load.value.format(number=len(history), table="history", time=TimeDo(start)))
        return history

    def Register(self, firstname, lastname, email, password, regdate, phonenumber, username):
        self.webcore.reconnect()
        self.cursor.execute("INSERT INTO users (firstname, lastname, email, password, token, gold, regdate, status, phonenumber, username, code, count) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (firstname, lastname, email, password, 0, 0, regdate, MSGList.ActiveAccount.value, phonenumber, username, 0, 0))
        self.webcore.commit()
        accounts[email] = {'firstname': firstname, 'lastname': lastname, 'email': email, 'password': password, 'token': 0, 'gold': 0, 'regdate': regdate, 'status': MSGList.ActiveAccount.value, 'phonenumber': phonenumber, 'username': username, 'code': 0, 'count': 0}

    def InsertHistory(self, email, item, date, username, charactername):
        self.webcore.reconnect()
        cursor = self.webcore.cursor()
        cursor.execute("INSERT INTO history (email, item, datepurch, username, charactername) VALUES (%s, %s, %s, %s, %s)", (email, item, date, username, charactername))
        self.webcore.commit()
        history.append({'email': email, 'item': item, 'date': date, 'username': username, 'charactername': charactername})
        self.webcore.disconnect()

    def BanUser(self):
        pass

    def ItemStore(self):
        self.webcore.reconnect()
        self.webcore.cursor().execute("INSERT INTO store (image, price, detail, ttile, mode, faction, version, itemid, service, maxskil)")
        self.webcore.commit()
        store.append()
        self.webcore.disconnect()

    def CheckUsername(self, username):
        self.webcore.reconnect()
        self.cursor.execute(f"SELECT * FROM users WHERE username='{username}'")
        res = self.cursor.fetchall()
        self.webcore.disconnect()
        if res == []:
            return False
        else:
            return True

    def ChangePassword(self, email, password):
        self.webcore.reconnect()
        self.cursor.execute(f"UPDATE users SET password = '{password}' WHERE email = '{email}'")
        self.webcore.commit()
        accounts[email].update({'password': password})

    def RedeemCode(self, email, code):
        self.webcore.reconnect()
        self.cursor.execute(f"UPDATE redeemcode SET usedto = '{email}' WHERE code = '{code}'")
        self.webcore.commit()

    def token(self, email, token):
        self.webcore.reconnect()
        self.cursor.execute(f"UPDATE users SET token = '{token}' WHERE email = '{email}'")
        accounts[email].update({'token': token})
        self.webcore.commit()
    
    def rfcode(self, email, code):
        self.webcore.reconnect()
        self.cursor.execute(f"UPDATE users SET code = '{code}' WHERE email = '{email}'")
        accounts[email].update({'code': code})
        self.webcore.commit()

    def rfcount(self, email, count):
        self.webcore.reconnect()
        self.cursor.execute(f"UPDATE users SET count = '{count}' WHERE email = '{email}'")
        accounts[email].update({'count': int(accounts[email]['count']) + 1})
        self.webcore.commit()

    def InsertItem(self, image, title, price, detail, mode, faction, id):
        self.webcore.reconnect()
        cursor = self.webcore.cursor()
        cursor.execute("INSERT INTO store (image, price, detail, title, mode, faction, version, itemid, service, maxskill) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (image, price, detail, title, mode, faction,))
        self.webcore.commit()
        #history.append({'email': email, 'item': item, 'date': date, 'username': username, 'charactername': charactername})
        self.webcore.disconnect()

    def InsertBug(self, kind, detail, visible, user):
        self.webcore.reconnect()
        cursor = self.webcore.cursor()
        cursor.execute("INSERT INTO bugs (kind, detail, visible, user) VALUES (%s, %s, %s, %s)", (kind, detail, visible, user))
        self.webcore.commit()
        bugs.append({'kind': kind, 'detail': detail, 'visible': visible, 'user': user})
        self.webcore.disconnect()

SQL = sql()