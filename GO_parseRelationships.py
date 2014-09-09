
# Parse all relationships between terms for go from GO XML

import Config
import sys, string
import MySQLdb
import Database
import gzip

from xml.etree import ElementTree

with Database.db as cursor :
	
	cursor.execute( "TRUNCATE TABLE " + Config.DB_NAME + ".go_relationships" )
	Database.db.commit( )
	
	with gzip.open( Config.GO_DEFINITIONS, 'r' ) as file :
	
		ontology = ElementTree.parse( file ).getroot( )
		
		insertCount = 0
		for element in ontology.findall( 'term' ) :
		
			goFullID = element.find( 'id' ).text.strip( )
			goShortID = goFullID[3:]
					
			for goISA in element.findall( 'is_a' ) :
			
				goISA_id = goISA.text
				goISA_short = goISA_id[3:]
				
				cursor.execute( "INSERT INTO " + Config.DB_NAME + ".go_relationships VALUES ( '0',%s, %s,'active' )", [goShortID, goISA_short] )
			
			insertCount = insertCount + 1
			if 0 == (insertCount % Config.DB_COMMIT_COUNT ) :
				Database.db.commit( )
			
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'GO_parseRelationships', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )
			