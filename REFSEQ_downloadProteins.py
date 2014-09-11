
# Parse go mappings from ENTREZ GENE for genes

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
searchData["email"] = "starkfree@gmail.com"
searchData["tool"] = "BioGRID Annotation Update"

MAX_ITERATIONS = 10
MAX_PER = 10000

with Database.db as cursor :

	cursor.execute( "SELECT refseq_protein_id, refseq_protein_uid FROM " + Config.DB_STAGING + ".refseq_protein_ids WHERE refseq_protein_downloaded='false'" )

	uidList = []
	mappingHash = { }
	for row in cursor.fetchall( ) :
		uidList.append(str(row[1]))
		mappingHash[str(row[1])] = str(row[0])
		
	fileCounter = 1
	start = 0
	currentSet = uidList[start:MAX_PER]
	
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
			
			with open( Config.PROTEIN_DIR + "refseq_proteins_" + str(startID) + "-" + str(endID) + ".fasta", 'w' ) as fastaFile :
				fastaFile.write( fetchData )
			
			for uid in currentSet :
				dbID = mappingHash[uid]
				cursor.execute( "UPDATE " + Config.DB_STAGING + ".refseq_protein_ids SET refseq_protein_downloaded='true' WHERE refseq_protein_id=%s", [dbID] )
			
			Database.db.commit( )
			
			start = start + MAX_PER
			fileCounter = fileCounter + 1
			currentSet = uidList[start:start+MAX_PER]
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
				
	
	# common = CommonFunctions.CommonFunctions( Database.db, cursor )
	# organismList = common.fetchOrganismList( False )
		
	# for k,organismInfo in organismList.items( ) :
	
		# successful = False
		# iteration = 1
		# (organism_id, organism_taxid, organism_common_name, organism_official_name, organism_abbreviation, organism_strain, organism_status) = organismInfo

		# If network connection fails, try up to 10 more times with
		# a minor pause in between, and then move on.
		# while not successful and not iteration > MAX_ITERATIONS :
			
			# print "Processing Organism: " + organism_common_name + "(" + str(organism_id) + ")"
			# searchData["term"] = "refseq[filter] AND txid%s[organism]" % organism_taxid
			
			# try :
		
				# data = urllib.urlencode( searchData )
				# request = urllib2.Request( searchURL, data )
				# response = urllib2.urlopen( request )
				# esearchData = response.read( )
	
				# results = ElementTree.fromstring( esearchData )
				# idsToFetch = []
				# for uid in results.findall( 'IdList/Id' ) :
					# idsToFetch.append( uid.text.strip( ) )
					
				# successful = True
	
			# except :
			
				# print "Failed Iteration " + str(iteration)
				# iteration = iteration + 1
				# time.sleep( 10 )
				
		# for id in idsToFetch :
			# cursor.execute( "INSERT INTO " + Config.DB_STAGING + ".refseq_protein_ids VALUES( '0', %s, %s, 'false' )", [id,organism_id] )
			
		# Database.db.commit( )
		# time.sleep( 5 )
	
sys.exit( )
			