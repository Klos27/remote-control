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
]

#todo put in DB
for switch in switches:
    cursor = mariadb_connection.cursor()
    cursor.execute("SELECT id, DATE_FORMAT(time, \"%d-%m-%Y %T\"), tempinside1, tempinside2, tempoutside, pressure, humidity FROM measurements WHERE time between %s and %s", (dateFrom, dateTo))
    for id, time, tempinside1, tempinside2, tempoutside, pressure, humidity in cursor:
        measurements.append({'id': id, 'time': time, 'tempinside1': tempinside1, 'tempinside2': tempinside2, 'tempoutside': tempoutside, 'pressure': pressure, 'humidity': humidity})
    cursor.close()