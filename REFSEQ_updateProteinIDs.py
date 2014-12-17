
# Load protein IDs for an organism passed in
# via the command line.

import Config
import sys, string, argparse
import MySQLdb
import Database
import urllib, urllib2
import time

from xml.etree import ElementTree
from classes import CommonFunctions, EntrezGene

# Process Command Line Input
argParser = argparse.ArgumentParser( description = 'Load REFSEQ protein IDs that are relevant to the organism id passed in via the command line.' )
argParser.add_argument( '-o', help = 'NCBI Organism ID', type=int, dest = 'organismID', required=True, action='store' )
inputArgs = vars( argParser.parse_args( ) )

searchURL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

searchData = { }
searchData["db"] = "protein"
searchData["retmax"] = 1000000
searchData["email"] = Config.APP_EMAIL
searchData["tool"] = Config.APP_TOOL

MAX_ITERATIONS = 10

with Database.db as cursor :

	common = CommonFunctions.CommonFunctions( Database.db, cursor )
	entrezGene = EntrezGene.EntrezGene( Database.db, cursor )
	organismList = entrezGene.fetchEntrezGeneOrganismMapping( )
	
	organismID = 0
	if inputArgs['organismID'] in organismList :
		organismID = organismList[inputArgs['organismID']]
	
	successful = False
	iteration = 1

	# If network connection fails, try up to 10 more times with
	# a minor pause in between, and then move on.
	while not successful and not iteration > MAX_ITERATIONS :
		
		print "Processing Organism: " + str(organismID) + ")"
		searchData["term"] = "refseq[filter] AND txid%s[organism]" % inputArgs['organismID']
		
		try :
	
			data = urllib.urlencode( searchData )
			request = urllib2.Request( searchURL, data )
			response = urllib2.urlopen( request )
			esearchData = response.read( )

			results = ElementTree.fromstring( esearchData )
			idsToFetch = []
			for uid in results.findall( 'IdList/Id' ) :
				idsToFetch.append( uid.text.strip( ) )
				
			successful = True

		except :
		
			print "Failed Iteration " + str(iteration)
			iteration = iteration + 1
			time.sleep( 10 )
				
	for id in idsToFetch :
	
		cursor.execute( "SELECT refseq_protein_id FROM " + Config.DB_STAGING + ".refseq_protein_ids WHERE refseq_protein_uid=%s LIMIT 1", [id] )
		row = cursor.fetchone( )
		
		if None == row :
			print "ADDING UID " + str(id)
			cursor.execute( "INSERT INTO " + Config.DB_STAGING + ".refseq_protein_ids VALUES( '0', %s, %s, 'false' )", [id,organismID] )
			
	Database.db.commit( )
	
sys.exit( )
			