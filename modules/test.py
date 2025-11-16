import mysql.connector

navigation = []

def ReadLinks():
    webcore = mysql.connector.connect(host='10.10.90.13', database='webcore', user='pooya', password='pooya!@#', port='3306')
    webcore.reconnect()
    cursor = webcore.cursor()
    cursor.execute('Select * From navlinks')
    for row in cursor:
        navigation.append({'href': row[1],'title': row[2], 'pos': row[3], 'name': row[4]})
    print(navigation)


ReadLinks()