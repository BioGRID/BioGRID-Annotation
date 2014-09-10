
# Parse go mappings from ENTREZ GENE for genes

import Config
import sys, string
import MySQLdb
import Database
import urllib, urllib2
import time

from xml.etree import ElementTree
from classes import CommonFunctions

searchURL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

searchData = { }
searchData["db"] = "protein"
searchData["retmax"] = 1000000
searchData["email"] = "starkfree@gmail.com"
searchData["tool"] = "BioGRID Annotation Update"

MAX_ITERATIONS = 10

with Database.db as cursor :

	cursor.execute( "TRUNCATE TABLE " + Config.DB_STAGING + ".refseq_protein_ids" )

	common = CommonFunctions.CommonFunctions( Database.db, cursor )
	organismList = common.fetchOrganismList( False )
		
	for k,organismInfo in organismList.items( ) :
	
		successful = False
		iteration = 1
		(organism_id, organism_taxid, organism_common_name, organism_official_name, organism_abbreviation, organism_strain, organism_status) = organismInfo

		# If network connection fails, try up to 10 more times with
		# a minor pause in between, and then move on.
		while not successful and not iteration > MAX_ITERATIONS :
			
			print "Processing Organism: " + organism_common_name + "(" + str(organism_id) + ")"
			searchData["term"] = "refseq[filter] AND txid%s[organism]" % organism_taxid
			
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
			cursor.execute( "INSERT INTO " + Config.DB_STAGING + ".refseq_protein_ids VALUES( '0', %s, %s, 'false' )", [id,organism_id] )
			
		Database.db.commit( )
		time.sleep( 5 )
	
sys.exit( )
			