
# Create the quick lookup gene identifier
# table by combining annotation from other
# resources into a single table.

import Config
import sys, string
import MySQLdb
import Database

from classes import Quick

with Database.db as cursor :

	quick = Quick.Quick( Database.db, cursor )

	cursor.execute( "TRUNCATE TABLE " + Config.DB_QUICK + ".quick_identifiers" )
	Database.db.commit( )
	
	cursor.execute( "SELECT gene_id, systematic_name, official_symbol, aliases, definition, external_ids, external_ids_types, organism_id, organism_common_name, organism_official_name, organism_abbreviation, organism_strain FROM " + Config.DB_QUICK + ".quick_annotation" )
	
	recordSize = 12 # Number of Columns in quick_identifiers table
	
	sqlFormat = ",".join( ['%s'] * recordSize )
	query = "INSERT INTO " + Config.DB_QUICK + ".quick_identifiers VALUES (%s)" % sqlFormat
	
	insertCount = 0
	for row in cursor.fetchall( ) :
	
		record = [row[0]] # Before ID data
		recordBase = [row[1],row[2],row[4],row[7],row[8],row[9],row[10],row[11], '0'] # After ID Data
		
		cursor.execute( query, tuple(record + [row[0], "BIOGRID"] + recordBase) )
		
		if "-" != row[1] :
			cursor.execute( query, tuple(record + [row[1], "SYSTEMATIC NAME"] + recordBase) )
			cursor.execute( query, tuple(record + [row[1], "ORDERED LOCUS"] + recordBase) )
			
		if "-" != row[2] :
			cursor.execute( query, tuple(record + [row[2], "OFFICIAL SYMBOL"] + recordBase) )
			
		if "-" != row[3] :
			aliases = row[3].split( "|" )
			for alias in aliases :
				if alias.upper( ) != row[1].upper( ) and alias.upper( ) != row[2].upper( ) :
					cursor.execute( query, tuple(record + [alias, "SYNONYM"] + recordBase) )
				
		if "-" != row[5] :
			externalIDs = row[5].split( "|" )
			externalTypes = row[6].split( "|" )
			
			for externalID, externalType in zip( externalIDs, externalTypes ) :
				cursor.execute( query, tuple(record + [externalID, externalType] + recordBase) )
				
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'QUICK_buildIdentifiers', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )		