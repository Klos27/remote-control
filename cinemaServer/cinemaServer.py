#!/usr/bin/python3
from flask import Flask
from flask import jsonify
from flask_httpauth import HTTPBasicAuth
from flask import abort
import mysql.connector as mariadb
from datetime import datetime, timedelta
import validator
import converter

#import sys
#sys.setDefaultEncoding('utf-8')

#import os
#os.putenv('LANG', 'en_US.UTF-8')
#os.putenv('LC_ALL', 'en_US.UTF-8')

"""
	TODO list:
- [OBLIGATORY] Add tests - in another file in python do test to call "curl and check return type"
- Get user login and password from file or database
- Add user list
- [optional] Change error return type to return HTTP staus codes
- [optional] add POST method to change user password
- [optional] Do something with timezones?

"""

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

# ===============================================================
# ======================[ APP SETTINGS ]=========================
# ===============================================================

app = Flask(__name__)

# ===============================================================
# =================[ AUTHORIZATION SETTINGS ]====================
# ===============================================================
# Test: curl -u username:password -i 127.0.0.1:5000/current

auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
	if username == 'cinema':
		return 'server'
	return None


@auth.error_handler
def unauthorized():
	err = [{
		'type' : 'error',
		'number' : '401',
		'description' : 'Unauthorized access'
	}]
	return jsonify({'responseType': 'notification', 'notification': err})

# ===============================================================
# ===========================[ HOME ]============================
# ===============================================================

@app.route('/')
def index():
	about = [{
		'type' : 'about',
		'title' : 'Raspberry Pi Cinema Server',
		'author' : 'Paweł Wądolny',
		'email' : 'pawel.wadolny.x@gmail.com'
	}]
	return jsonify({'responseType': 'notification', 'notification': about})

# ===============================================================
# ===========================[ 404 ]=============================
# ===============================================================

@app.errorhandler(404)
def page_not_found(error):
	err = [{
		'type' : 'error',
		'number' : '404',
		'description' : 'Page not found'
	}]
	return jsonify({'responseType': 'notification', 'notification': err})
	
# ===============================================================
# ==================[ MEASUREMENTS' HISTORY ]====================
# ===============================================================
# DATE IN ISO 8601 FORMAT yyyymmddThhmmssZ (i.e. 20180829T074657Z)

@app.route('/set', methods=['GET'])
@app.route('/set/<integer:switchNo>/<integer:value>', methods=['GET'])
@auth.login_required
def getHistory(switchNo = None, value = None):
	global mariadb_connection
	if mariadb_connection.is_connected() == False:
		openConnection()
	try:
		validationFlag = True
		if(dateFrom == None or dateTo == None):
			# default one day before
			now = datetime.now()
			dateTo = now.strftime("%Y-%m-%d %H:%M:%S")
			dateFrom = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
		elif (not validator.isIso8601(dateFrom) or not validator.isIso8601(dateTo)):
			validationFlag = False
		else:
			dateFrom = converter.iso8601toDateStr(dateFrom) 
			dateTo = converter.iso8601toDateStr(dateTo)
		measurements = []
		if validationFlag:
			cursor = mariadb_connection.cursor()
			cursor.execute("SELECT id, DATE_FORMAT(time, \"%d-%m-%Y %T\"), tempinside1, tempinside2, tempoutside, pressure, humidity FROM measurements WHERE time between %s and %s", (dateFrom, dateTo))
			for id, time, tempinside1, tempinside2, tempoutside, pressure, humidity in cursor:
				measurements.append({'id': id, 'time': time, 'tempinside1': tempinside1, 'tempinside2': tempinside2, 'tempoutside': tempoutside, 'pressure': pressure, 'humidity': humidity})
			cursor.close()
		else:
			err = [{
				'type' : 'error',
				'number' : '400',
				'description' : 'Wrong GET parameters'
			}]
			return jsonify({'responseType': 'notification', 'notification': err})
	except mariadb.Error as error:
		print("Error: {}".format(error))
	#mariadb_connection.commit()
	return jsonify({'responseType': 'measurements', 'measurements': measurements})

# ===============================================================
# ===================[ LATEST MEASUREMENT ]======================
# ===============================================================

@app.route('/current', methods=['GET'])
#@auth.login_required
def getCurrent():
	global mariadb_connection
	if mariadb_connection.is_connected() == False:
		openConnection()
	try:
		measurement = []
		cursor = mariadb_connection.cursor()
		cursor.execute("SELECT id, DATE_FORMAT(time, \"%d-%m-%Y %T\"), tempinside1, tempinside2, tempoutside, pressure, humidity FROM measurements WHERE id = (SELECT MAX(id) FROM measurements)")
		for id, time, tempinside1, tempinside2, tempoutside, pressure, humidity in cursor:
			measurement.append({'id': id, 'time': time, 'tempinside1': tempinside1, 'tempinside2': tempinside2, 'tempoutside': tempoutside, 'pressure': pressure, 'humidity': humidity})
		cursor.close()
	except mariadb.Error as error:
		print("Error: {}".format(error))
	#mariadb_connection.commit()
	return jsonify({'responseType': 'measurement', 'measurements': measurement})

# ===============================================================
# =====================[ DATABASE INFO ]=========================
# ===============================================================

@app.route('/database', methods=['GET'])
#@auth.login_required
def getDatabaseSize():
	global mariadb_connection
	if mariadb_connection.is_connected() == False:
		openConnection()
	try:
		db = []
		cursor = mariadb_connection.cursor()
		cursor.execute("SELECT MAX(id) FROM measurements")
		numOfMeasurements = 0
		for maxId in cursor:
			numOfMeasurements = maxId[0]
		cursor.execute("SELECT table_schema AS \"Database\", SUM(data_length + index_length) / 1024 / 1024 AS \"Size (MB)\" FROM information_schema.TABLES WHERE table_schema LIKE \"weatherstation\" GROUP BY table_schema")
		for database, size in cursor:
			db.append({'database': database, 'numOfMeasurements': str(numOfMeasurements), 'size': size})
		cursor.close()
	except mariadb.Error as error:
		print("Error: {}".format(error))
	#mariadb_connection.commit()
	return jsonify({'responseType': 'database', 'database': db})

# ===============================================================
# ========================[ START APP ]==========================
# ===============================================================

if __name__ == '__main__':
	#app.run(host='0.0.0.0', port=5000, debug=True, ssl_context='adhoc')
	app.run(host='0.0.0.0', port=5000, debug=True)
		
print("Closing database connection...")
mariadb_connection.close()
print("Server closed")
