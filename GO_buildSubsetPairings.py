
# Build a table of pairings for terms bubbling up to GO SLIM subsets

import Config
import sys, string
import MySQLdb
import Database
import gzip

from xml.etree import ElementTree
from classes import GeneOntology

with Database.db as cursor :

	geneOntology = GeneOntology.GeneOntology( Database.db, cursor )
	
	cursor.execute( "TRUNCATE TABLE " + Config.DB_NAME + ".go_subset_pairings" )
	Database.db.commit( )
	
	mappingHash = geneOntology.getMappingHash( )
	
	insertCount = 0
	for key,value in mappingHash.items( ) :
		cursor.execute( "SELECT go_id FROM " + Config.DB_NAME + ".go_definitions WHERE go_status='active'" )
		for row in cursor.fetchall( ) :
			subsetParents = geneOntology.findSubsetParents( row[0], key )
			subsetParents = set(subsetParents) # Remove Duplicates
			for subsetParent in subsetParents :
				cursor.execute( "INSERT INTO " + Config.DB_NAME + ".go_subset_pairings VALUES( '0', %s, %s, %s, 'active' )", [row[0], key, subsetParent] )
				insertCount = insertCount + 1
		
				if 0 == (insertCount % Config.DB_COMMIT_COUNT ) :
					Database.db.commit( )
	
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'EG_buildSubsetPairings', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )
			