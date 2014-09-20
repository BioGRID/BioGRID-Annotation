
# Parse UNIPROT XML files and load sequence data
# into the database

import Config
import sys, string, argparse
import MySQLdb
import Database
import glob
import os

from gzip import open as gopen
from xml.sax import parse
from classes import UniprotProteinXMLParser, UniprotKB

# Process input in case we want to skip to a specific organism
argParser = argparse.ArgumentParser( description = "Download Protein Files Grouped by Organism from Uniprot" )
argGroup = argParser.add_mutually_exclusive_group( )
argGroup.add_argument( '-o', dest='organism', type = int, nargs = 1, help = "An organism id to start at" )
inputArgs = vars( argParser.parse_args( ) )

with Database.db as cursor :

	uniprotKB = UniprotKB.UniprotKB( Database.db, cursor )

	if inputArgs['organism'] is None :
	
		# Simply inactivate these two tables because we want to maintain ids
		# when possible.
		cursor.execute( "UPDATE " + Config.DB_NAME + ".uniprot SET uniprot_status='inactive'" )
		cursor.execute( "UPDATE " + Config.DB_NAME + ".uniprot_features SET uniprot_feature_status='inactive'" )
		
		cursor.execute( "TRUNCATE TABLE " + Config.DB_NAME + ".uniprot_aliases" )
		cursor.execute( "TRUNCATE TABLE " + Config.DB_NAME + ".uniprot_definitions" )
		cursor.execute( "TRUNCATE TABLE " + Config.DB_NAME + ".uniprot_externals" )
		cursor.execute( "TRUNCATE TABLE " + Config.DB_NAME + ".uniprot_go" )
	
		Database.db.commit( )

	startParse = False
	for filename in reversed( sorted( glob.glob( Config.UP_PROTEINS_DIR + "*.gz" ), key=os.path.getsize ) ) :

		organismID = filename[filename.rfind( "_" )+1:filename.rfind( ".xml" )]
		print "Working on : " + str(organismID) + " (" + filename + ")"
		
		if inputArgs['organism'] is not None :
		
			if str(inputArgs['organism'][0]) == organismID :
				startParse = True
				
			if not startParse :
				continue
		
		with gopen( filename ) as uniprotFile :
			parse( uniprotFile, UniprotProteinXMLParser.UniprotProteinXMLParser( uniprotKB, organismID ) )
		
		Database.db.commit( )
	
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'UNIPROT_parseProteins', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )
			