
# Connects to the EUTILS service to download
# REFSEQ proteins that are not fully filled out
# in the refseq table.

import Config
import sys, string
import MySQLdb
import Database
import urllib, urllib2
import time

searchURL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

searchData = { }
searchData["db"] = "protein"
searchData["retmode"] = "fasta"
searchData["rettype"] = "text"
searchData["email"] = Config.APP_EMAIL
searchData["tool"] = Config.APP_TOOL

MAX_ITERATIONS = 10
MAX_PER = 10000

with Database.db as cursor :

	cursor.execute( "SELECT refseq_id, refseq_accession FROM " + Config.DB_NAME + ".refseq WHERE refseq_sequence='' AND refseq_status='active'" )

	accessionList = []
	mappingHash = { }
	for row in cursor.fetchall( ) :
		accessionList.append(str(row[1]))
		mappingHash[str(row[1])] = str(row[0])
		
	fileCounter = 1
	start = 0
	currentSet = accessionList[start:MAX_PER]
	
	iteration = 1
	while len(currentSet) > 0 :
	
		startID = currentSet[0]
		endID = currentSet[-1]
	
		print "Working on File: " + str(fileCounter) + " (" + str(startID) + "-" + str(endID) + ")"
		searchData["id"] = ",".join( currentSet )
		
		try :
				
			data = urllib.urlencode( searchData )
			request = urllib2.Request( searchURL, data )
			response = urllib2.urlopen( request )
			fetchData = response.read( )
			
			# Downloads the files only to minimize processing errors
			# which may result in too many hits to the eutils website
			with open( Config.PROTEIN_MISSING_DIR + "refseq_proteins_" + str(startID) + "-" + str(endID) + ".fasta", 'w' ) as fastaFile :
				fastaFile.write( fetchData )
									
			start = start + MAX_PER
			fileCounter = fileCounter + 1
			currentSet = accessionList[start:start+MAX_PER]
			iteration = 1
			
			time.sleep( 5 )
			
		except Exception as e :
					
			if iteration <= MAX_ITERATIONS :
				print "FAILED ITERATION " + str(iteration)
				iteration = iteration + 1
				time.sleep( 10 )
			else :
				# Failed MAX_ITERATIONS times, move on to the next
				# set of identifiers
				start = start + MAX_PER
				fileCounter = fileCounter + 1
				currentSet = uidList[start:start+MAX_PER]
				iteration = 1
				
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'REFSEQ_downloadMissingProteins', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )
			