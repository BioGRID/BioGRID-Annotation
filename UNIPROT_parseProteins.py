
# Parse UNIPROT XML files and load sequence data
# into the database

import Config
import sys, string
import MySQLdb
import Database
import glob
import os

from gzip import open as gopen
from xml.sax import parse
from classes import UniprotProteinXMLParser, UniprotKB

with Database.db as cursor :

	uniprotKB = UniprotKB.UniprotKB( Database.db, cursor )

	# Simply inactivate these two tables because we want to maintain ids
	# when possible.
	cursor.execute( "UPDATE " + Config.DB_NAME + ".uniprot SET uniprot_status='inactive'" )
	cursor.execute( "UPDATE " + Config.DB_NAME + ".uniprot_features SET uniprot_feature_status='inactive'" )
	
	cursor.execute( "TRUNCATE TABLE " + Config.DB_NAME + ".uniprot_aliases" )
	cursor.execute( "TRUNCATE TABLE " + Config.DB_NAME + ".uniprot_definitions" )
	cursor.execute( "TRUNCATE TABLE " + Config.DB_NAME + ".uniprot_externals" )
	cursor.execute( "TRUNCATE TABLE " + Config.DB_NAME + ".uniprot_go" )
	
	Database.db.commit( )

	for filename in reversed( sorted( glob.glob( Config.UP_PROTEINS_DIR + "*.gz" ), key=os.path.getsize ) ) :

		organismID = filename[filename.rfind( "_" )+1:filename.rfind( ".xml" )]
		
		print "Working on : " + str(organismID) + " (" + filename + ")"

		with gopen( filename ) as uniprotFile :
			parse( uniprotFile, UniprotProteinXMLParser.UniprotProteinXMLParser( uniprotKB, organismID ) )
		
		Database.db.commit( )
	
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'UNIPROT_parseProteins', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )
			