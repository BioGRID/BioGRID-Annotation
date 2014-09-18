
# Download files from the UNIPROT containing
# proteins from organisms of interest

import Config
import sys, string
import MySQLdb
import Database
import urllib, urllib2
import time

searchURL = "http://www.uniprot.org/uniprot/"

searchData = { }
searchData["compress"] = "yes"
searchData["format"] = "xml"

MAX_ITERATIONS = 10

with Database.db as cursor :

	cursor.execute( "SELECT organism_id, organism_uniprot_taxid, organism_official_name, organism_strain FROM " + Config.DB_NAME + ".organisms WHERE organism_status='active'" )
	
	organismList = []
	organismHash = { }
	for row in cursor.fetchall( ) :
		organismList.append( str(row[1]) )
		organismHash[str(row[1])] = row
	
	fileCounter = 1
	iteration = 1
	while len(organismList) > 0 :
	
		currentOrganism = organismList.pop( )
		(organismID, organismUniprotTaxID, organismName, organismStrain) = organismHash[currentOrganism]
	
		searchData["query"] = "organism:" + currentOrganism
		
		print "Working on organism: " + str(fileCounter) + " (" + organismName + " " + organismStrain + ")"
		
		try :
		
			data = urllib.urlencode( searchData )
			request = urllib2.Request( searchURL, data )
			response = urllib2.urlopen( request )
			fetchData = response.read( )
			
			with open( Config.UP_PROTEINS_DIR + "uniprot_proteins_" + str(organismID) + ".xml.gz", 'wb' ) as proteinFile :
				proteinFile.write( fetchData )
				
			fileCounter = fileCounter + 1
			iteration = 1
			
			time.sleep( 5 )
			
		except :
		
			if iteration <= MAX_ITERATIONS :
				print "FAILED ITERATION " + str(iteration)
				iteration = iteration + 1
				organismList.append(currentOrganism)
				time.sleep( 10 )
			else :
				# Failed MAX_ITERATIONS times, move on to the next
				# set of identifiers
				fileCounter = fileCounter + 1
				iteration = 1
				
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'UNIPROT_downloadProteins', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )
			