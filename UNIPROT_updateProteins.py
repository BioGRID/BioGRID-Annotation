
# Parse UNIPROT XML files and load sequence data
# into the database for organism of interest

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
argParser = argparse.ArgumentParser( description = 'Update all uniprot proteins that are relevant to the organism id passed in via the command line.' )
argParser.add_argument( '-o', help = 'BioGRID Organism ID', type=int, dest = 'organismID', required=True, action='store' )
inputArgs = vars( argParser.parse_args( ) )

with Database.db as cursor :

	uniprotKB = UniprotKB.UniprotKB( Database.db, cursor )
	
	organismID = inputArgs['organismID']
	
	# Get all existing uniprot ids for the organism we want.
	cursor.execute( "SELECT uniprot_id FROM " + Config.DB_NAME + ".uniprot WHERE organism_id=%s", [organismID] )
	
	for row in cursor.fetchall( ) :
	
		uniprotID = row[0]
	
		# Inactivate proteins in these two tables only for the specific organism
		cursor.execute( "UPDATE " + Config.DB_NAME + ".uniprot SET uniprot_status='inactive' WHERE uniprot_id = %s", [uniprotID] )
		cursor.execute( "UPDATE " + Config.DB_NAME + ".uniprot_features SET uniprot_feature_status='inactive' WHERE uniprot_id = %s", [uniprotID] )
		
		# Delete associated annotation that goes with the deactivated records
		cursor.execute( "DELETE FROM " + Config.DB_NAME + ".uniprot_aliases WHERE uniprot_id=%s", [uniprotID] )
		cursor.execute( "DELETE FROM " + Config.DB_NAME + ".uniprot_definitions WHERE uniprot_id=%s", [uniprotID] )
		cursor.execute( "DELETE FROM " + Config.DB_NAME + ".uniprot_externals WHERE uniprot_id=%s", [uniprotID] )
		cursor.execute( "DELETE FROM " + Config.DB_NAME + ".uniprot_go WHERE uniprot_id=%s", [uniprotID] )
		
	Database.db.commit( )
		
	filename = Config.UP_PROTEINS_DIR + "uniprot_proteins_" + str(organismID) + ".xml.gz"
	print "Working on : " + str(organismID) + " (" + filename + ")"
		
	with gopen( filename ) as uniprotFile :
		parse( uniprotFile, UniprotProteinXMLParser.UniprotProteinXMLParser( uniprotKB, organismID ) )
	
	Database.db.commit( )

	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'UNIPROT_updateProteins', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )
			