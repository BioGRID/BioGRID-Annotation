
# Parse all definitions for genes from Entrez Gene that
# are relevant to the organisms we want loaded
# via the organisms table.

import Config
import sys, string
import MySQLdb
import Database
import gzip

from xml.etree import ElementTree

with Database.db as cursor :
	
	cursor.execute( "TRUNCATE TABLE " + Config.DB_NAME + ".go_definitions" )
	cursor.execute( "TRUNCATE TABLE " + Config.DB_NAME + ".go_subsets" )
	cursor.execute( "TRUNCATE TABLE " + Config.DB_NAME + ".go_subset_mappings" )
	Database.db.commit( )
	
	ontology = ElementTree.parse( Config.GO_DEFINITIONS ).getroot( )
	goSubsets = { }
	
	for element in ontology.findall( 'header/subsetdef' ) :
	
		subsetID = element.find( 'id' ).text.strip( )
		subsetDesc = element.find( 'name' ).text.strip( )
		
		cursor.execute( "INSERT INTO " + Config.DB_NAME + ".go_subsets VALUES( '0', %s, %s, NOW( ), 'active' )", [subsetID, subsetDesc] )
		goSubsets[subsetID.upper( )] = cursor.lastrowid
		
	Database.db.commit( )
	
	insertCount = 0
	for element in ontology.findall( 'term' ) :
	
		goFullID = element.find( 'id' ).text.strip( )
		goName = element.find( 'name' ).text.strip( )
		goNamespace = element.find( 'namespace' ).text.strip( )
		goDefinition = element.find( 'def/defstr' )
		
		if None != goDefinition :
			goDefinition = goDefinition.text.strip( )
		else :
			goDefinition = ""
			
		goShortID = goFullID[3:]
		
		cursor.execute( "INSERT INTO " + Config.DB_NAME + ".go_definitions VALUES( %s, %s, %s, %s, %s, NOW( ), 'active' )", [goShortID, goFullID, goName, goDefinition, goNamespace] )
		
		for subset in element.findall( 'subset' ) :
		
			subsetName = subset.text.strip( )
			subsetID = goSubsets[subsetName.strip( ).upper( )]
			
			cursor.execute( "INSERT INTO " + Config.DB_NAME + ".go_subset_mappings VALUES ( '0',%s, %s,'active' )", [goShortID,subsetID] )
		
		insertCount = insertCount + 1
		if 0 == (insertCount % Config.DB_COMMIT_COUNT ) :
			Database.db.commit( )
			
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'GO_parseDefinitions', NOW( ) )" )
	Database.db.commit( )
sys.exit( )
			