#!/usr/bin/python3
from flask import Flask
from flask import jsonify
from flask_httpauth import HTTPBasicAuth
from flask import abort
import mysql.connector as mariadb
from datetime import datetime, timedelta
#import validator
#import converter

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

presets = [
	#presetId, [[switchNo, status, value]]
	[1, [["1", 1, 0],
		["2", 1, 0],
		["3", 1, 0],
		["4", 1, 0],
		["5", 0, 0],
		["6", 0, 0],
		["7", 0, 0],
		["8", 0, 0],
		["9", 0, 0],
		["10", 0, 0],
		]
	],
	[2, [["1", 0, 0],
		["2", 0, 0],
		["3", 0, 0],
		["4", 0, 0],
		["5", 1, 0],
		["6", 1, 0],
		["7", 1, 0],
		["8", 1, 0],
		["9", 0, 0],
		["10", 0, 0],
		]
	],
	[3, [["1", 0, 0],
		["2", 0, 0],
		["3", 0, 0],
		["4", 0, 0],
		["5", 0, 0],
		["6", 0, 0],
		["7", 0, 0],
		["8", 0, 0],
		["9", 1, 0],
		["10", 1, 0],
		]
	],
    [100, [["1", 0, 0],
		   ["2", 0, 0],
		   ["3", 0, 0],
		   ["4", 0, 0],
		   ["5", 0, 0],
		   ["6", 0, 0],
		   ["7", 0, 0],
		   ["8", 0, 0],
		   ["9", 0, 0],
		   ["10", 0, 0],
		  ]
	],
    [101, [["1", 1, 0],
		   ["2", 1, 0],
		   ["3", 1, 0],
		   ["4", 1, 0],
		   ["5", 1, 0],
		   ["6", 1, 0],
		   ["7", 1, 0],
		   ["8", 1, 0],
		   ["9", 1, 0],
		   ["10", 1, 0],
		  ]
	],
]

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

#@app.route('/set', methods=['GET'])
@app.route('/set/<int:switchNo>/<int:status>', methods=['GET'])
@app.route('/set/<int:switchNo>/<int:status>/<int:value>', methods=['GET'])
@auth.login_required
def setSwitch(switchNo, status, value = None):
	updateSwitch(switchNo, status, value)
	return getStatus()

# ===============================================================
# ===================[ LATEST MEASUREMENT ]======================
# ===============================================================

@app.route('/status', methods=['GET'])
@auth.login_required
def getStatus():
	global mariadb_connection
	if mariadb_connection.is_connected() == False:
		openConnection()
	try:
		switches = []
		cursor = mariadb_connection.cursor()
		cursor.execute("SELECT id, name, type, status, value FROM switches")
		for id, name, switchType, status, value in cursor:
			switches.append({'id': id, 'name': name, 'type': switchType, 'status': status, 'value': value})
		cursor.close()
	except mariadb.Error as error:
		print("Error: {}".format(error))
	#mariadb_connection.commit()
	return jsonify({'responseType': 'status', 'switches': switches})

# ===============================================================
# =====================[ PRESET ]=========================
# ===============================================================

@app.route('/preset/<int:presetNo>', methods=['GET'])
@auth.login_required
def setPreset(presetNo):
	global presets
	for preset in presets:
		if preset[0] == presetNo:
			for switch in preset[1]:
				updateSwitch(switch[0], switch[1], switch[2])
	return getStatus()


# ===============================================================
# ========================[ UPDATE SWITCH ]==========================
# ===============================================================
def updateSwitch(switchNo, status, value = None):
	global mariadb_connection
	if mariadb_connection.is_connected() == False:
		openConnection()
	try:
		cursor = mariadb_connection.cursor()
		query = "UPDATE switches SET status="
		query += str(status)
		if value != None:
			# if value != 0:
			# 	query += str(status)
			# else:
			# 	query += "0"
			query += ", value="
			query += str(value)
		# else:
		# 	query += str(status)
		query += " WHERE id="
		query += str(switchNo)

		print("query: {}".format(query))
		
		cursor.execute(query)
		cursor.close()
	except mariadb.Error as error:
		print("Error: {}".format(error))

# ===============================================================
# ========================[ START APP ]==========================
# ===============================================================

if __name__ == '__main__':
	#app.run(host='0.0.0.0', port=5000, debug=True, ssl_context='adhoc')
	app.run(host='0.0.0.0', port=5000, debug=True)
		
print("Closing database connection...")
mariadb_connection.close()
print("Server closed")
