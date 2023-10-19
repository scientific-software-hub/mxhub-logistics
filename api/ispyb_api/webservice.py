import os
import logging
import requests
from urllib.parse import urljoin
from flask import Flask, jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import json
import mysql.connector
from datetime import datetime
from . import db
import itertools


def update_comments(dewarid, comments):

	cnx = mysql.connector.connect(
		host='localhost',
		user='pxuser',
		password='1spybUser',
		database='pydb'
		)


	cursor = cnx.cursor()

    # Check if the dewar exists
	cursor.execute("SELECT dewarid FROM Dewar WHERE dewarid = %s", (dewarid,))
	dewars = cursor.fetchall()
	if not dewars:
		cursor.close()
		cnx.close()
		raise ValueError(f"Dewar not found")

	dewar = dewars[0]

    # Update the dewar comments
	if comments != None:
		update_query = ("UPDATE Dewar SET Comments = %s WHERE DewarId = %s")
		update_params = (comments, dewar[0])
		cursor.execute(update_query, update_params)

		cnx.commit()

		cursor.close()

		cnx.close()
	else:
		cursor.close()
		cnx.close()
	return {'DEWARID': dewars[0]}


def set_location(barcode, location, awb=None):

	track = None #because we dont use it yet
	result = None
	comments=None

	if "DESY" in barcode:
		print ("DESY")

		cnx = mysql.connector.connect(
               		host='localhost',
               		user='pxuser',
              		password='1spybUser',
               		database='pydb'
        		)

	if "EMBL" in barcode:
		print ("EMBL")

#needs to be changed to EMBL database

		cnx = mysql.connector.connect(
                        host='localhost',
                        user='pxuser',
                        password='1spybUser',
                        database='pydb'
                        )

	cursor = cnx.cursor()


	select_query = """
	SELECT CONCAT(CONCAT(pe.givenname, ' '), pe.familyname) as lcout, pe.emailaddress as lcoutemail,
	CONCAT(CONCAT(pe2.givenname, ' '), pe2.familyname) as lcret, pe2.emailaddress as lcretemail,
	CONCAT(CONCAT(CONCAT(p.proposalcode, p.proposalnumber), '-'), e.visit_number) as firstexp,
	DATE_FORMAT(e.startdate, '%d-%m-%Y %H:%i') as firstexpst,
	e.beamlinename, e.beamlineoperator, d.dewarid, d.trackingnumberfromsynchrotron,
	s.shippingid, s.shippingname, p.proposalcode, CONCAT(p.proposalcode, p.proposalnumber) as prop,
	d.barcode, d.facilitycode, d.firstexperimentid, d.dewarstatus
	FROM Dewar d
	INNER JOIN Shipping s ON s.shippingid = d.shippingid
	LEFT OUTER JOIN LabContact c ON s.sendinglabcontactid = c.labcontactid
	LEFT OUTER JOIN Person pe ON pe.personid = c.personid
	LEFT OUTER JOIN LabContact c2 ON s.returnlabcontactid = c2.labcontactid
	LEFT OUTER JOIN Person pe2 ON pe2.personid = c2.personid
	INNER JOIN Proposal p ON p.proposalid = s.proposalid
	LEFT OUTER JOIN BLSession e ON e.sessionid = d.firstexperimentid
	WHERE LOWER(barcode) LIKE LOWER(%s)
	"""

	insert_query = """
	INSERT INTO DewarTransportHistory (dewarid, dewarstatus, storagelocation, arrivaldate)
	VALUES (%s, LOWER(%s), LOWER(%s), CURRENT_TIMESTAMP)
	"""


        # Fetch the results
	cursor.execute(select_query, (barcode,))
	dew = cursor.fetchone()
	cursor.execute(select_query, (barcode,))
	results = cursor.fetchall()


        # Process the results
	for row in results:
		lcout = row[0]
		lcoutemail = row[1]
		lcret = row[2]
		lcretemail = row[3]
		firstexp = row[4]
		firstexpst = row[5]
		beamlinename = row[6]
		beamlineoperator = row[7]
		dewarid = row[8]
		trackingnumberfromsynchrotron = row[9]
		shippingid = row[10]
		shippingname = row[11]
		proposalcode = row[12]
		prop = row[13]
		barcode = row[14]
		facilitycode = row[15]
		firstexperimentid = row[16]
		dewarstatus = row[17]


        # Specify the parameter values for the query
	storagelocation = location

	r = update_comments(dewarid, comments)

	# Get the last storage location from dewartransporthistory
	if dew is not None:
		dewarid = dewarid
		if dewarid is not None:
			cursor.execute("SELECT storagelocation FROM DewarTransportHistory WHERE dewarid = %s ORDER BY dewartransporthistoryid DESC LIMIT 1", (dewarid,))

	last_history_result = cursor.fetchone()

	if last_history_result is not None:
		last_location = last_history_result[0]
	bls = ['p12', 'p13', 'p14', 'p11', 'i04']  # Replace with actual beamline names or retrieve them from a config object

	if last_location in bls:
		from_beamline = True
	else:
		print("No previous dewar transport history for DewarId", dewarid)

	if location.lower() == last_location:
		dewarId = dewarid
		cursor.execute("SELECT comments FROM Dewar WHERE dewarid = %s", (dewarid,))
		comments = cursor.fetchone()
		if comments is not None:
			cc = comments[0]
			comments = json.loads(cc)
		now = datetime.now().isoformat("T", "seconds")

		if 'toppedUp' in comments:
		#	comments['toppedUp'] = [now]
			comments['toppedUp'].append(now)
			comments['toppedUp'] = comments['toppedUp'][-5:]
			update_comments(dewarid, json.dumps(comments))
		else:
			comments['toppedUp'] = [now]
			update_comments(dewarid, json.dumps(comments))

	# Convert dewar status to lowercase
	dewarstatus = 'dispatch-requested' if dewarstatus.lower() == 'dispatch-requested' else 'at facility'

	#no two dewars in one Rack
	cursor.execute("SELECT dewarid FROM DewarTransportHistory WHERE storageLocation=%s",(location,))
	history = cursor.fetchall()
	empty = True
	entrys = len(history)
	if entrys < 50:
		limit = entrys
	else:
		limit = 50
	count = 0
	for row in history:
		cursor.execute("SELECT storageLocation FROM DewarTransportHistory WHERE dewarId=%s",(row[0],))
		idlocation = cursor.fetchall()
		last_position = idlocation[-1]
		last_position = last_position[0]
		if last_position == location.lower() and last_location != location.lower():
			empty = False

		count +=1
		if count == limit:
			break
	print ()
	if empty == False:
		print ("belegt")
	else:
		# Insert record into dewartransporthistory table
		cursor.execute("INSERT INTO DewarTransportHistory (dewartransporthistoryid, dewarid, dewarstatus, storagelocation, arrivaldate) VALUES (DEFAULT, %s, lower(%s), lower(%s), %s)",
		(dewarid, dewarstatus, location, datetime.now()))
		cursor.execute("SELECT LAST_INSERT_ID()")
		dhid = cursor.fetchone()[0]

		# Update dewar and shipping tables
		cursor.execute("UPDATE Dewar SET dewarstatus=lower(%s), storagelocation=lower(%s), trackingnumberfromsynchrotron=%s WHERE dewarid=%s",
        		(dewarstatus, location, track, dewarid))
		cursor.execute("UPDATE Shipping SET shippingStatus=lower(%s) WHERE shippingId=%s",
		(dewarstatus, shippingid))

		# Retrieve container IDs associated with the dewar
		cursor.execute("SELECT containerid FROM Container WHERE dewarid=%s",(dewarid,))
		containers = cursor.fetchall()

		# Insert record into containerhistory table for each container
		#for c in containers:
			#cursor.execute("INSERT INTO ContainerHistory (containerid, status) VALUES (%s, 'at facility')", (c['CONTAINERID'],))

	#Commit the changes and close the connection
	cnx.commit()
	cursor.close()
	cnx.close()

	logging.getLogger('ispyb-logistics').info("Set location in ISPyB via SynchWeb bc: {} loc: {} ".format(barcode, location))

	result = ({'DEWARHISTORYID': dhid})
	if result != None:
		logging.getLogger('ispyb-logistics').info("Set location in ISPyB via SynchWeb bc: {} loc: {} ".format(barcode, location))
	return result


def new_barcode(barcode):



	return result


def set_container_location(code, location):



        return result


def set_container_location_from_id(id, location):


        return result


