import mysql.connector as mariadb

# ===============================================================
# ====================[ DATABASE SETTINGS ]======================
# ===============================================================
mariadb_connection = mariadb.connect(user='cinemadb', password='raspberrypi', database='cinemadb')
mariadb_connection.autocommit = True
#cursor = mariadb_connection.cursor()

def openConnection():
	print("Database reconnect")
	global mariadb_connection
	mariadb_connection = mariadb.connect(user='cinemadb', password='raspberrypi', database='cinemadb')
	mariadb_connection.autocommit = True
	#cursor = mariadb_connection.cursor()

# Id, name, type: button/slider, status 0-off 1-on, value for leds 0-255, default status, defaultValue
switches = [
    ["1", "Światło 1", "button", 0, 0],
    ["2", "Światło 2", "button", 0, 0],
    ["3", "Światło 3", "button", 0, 0],
    ["4", "Światło 4", "button", 0, 0],
    ["5", "Światło 5", "button", 0, 0],
    ["6", "Światło 6", "button", 0, 0],
    ["7", "Światło 7", "button", 0, 0],
    ["8", "Światło 8", "button", 0, 0],
    ["9", "Światło 9", "button", 0, 0],
    ["10", "Światło 10", "button", 0, 0],
    ["11", "LED", "slider", 0, 0],
]

if mariadb_connection.is_connected() == False:
    openConnection()
try:
    #drop all records in switches
    cursor = mariadb_connection.cursor()
    cursor.execute("DELETE FROM switches;")
except mariadb.Error as error:
    print("Error: {}".format(error))

try:
    for switch in switches:
        cursor = mariadb_connection.cursor()
        # put in DB
        stringToPaste = "INSERT INTO switches (id, name, type, status, value) VALUES ('"
        stringToPaste += switch[0]
        stringToPaste += "', '"
        stringToPaste += switch[1]
        stringToPaste += "', '"
        stringToPaste += switch[2]
        stringToPaste += "', '"
        stringToPaste += str(switch[3])
        stringToPaste += "', '"
        stringToPaste += str(switch[4])
        stringToPaste += "');"
        cursor.execute(stringToPaste)
    cursor.close()
except mariadb.Error as error:
    print("Error: {}".format(error))
