
# Create the quick lookup gene identifier
# table by combining annotation from other
# resources into a single table.

import Config
import sys, string, argparse
import MySQLdb
import Database

from classes import Quick

# Process Command Line Input
argParser = argparse.ArgumentParser( description = 'Update all Annotation Records' )
argGroup = argParser.add_mutually_exclusive_group( required=True )
argGroup.add_argument( '-o', dest='organismID', type = int, nargs = 1, help = 'An organism id to update annotation for', action='store' )
argGroup.add_argument( '-g', dest='geneID', type = int, nargs = 1, help = 'A Gene ID to Update', action='store' )
argGroup.add_argument( '-d', dest='dateVal', type = str, nargs = 1, help = 'A date value (YYYY-MM-DD 00:00:00)', action='store' )
argGroup.add_argument( '-all', dest='allRecords', help = 'Build from All Records, Starting from Scratch', action='store_true' )
inputArgs = vars( argParser.parse_args( ) )

isOrganism = False
isGene = False
isDate = False
isAll = False

if None != inputArgs['organismID'] :
	isOrganism = True
elif None != inputArgs['geneID'] :
	isGene = True
elif None != inputArgs['dateVal'] :
	isDate = True
else :
	isAll = True

with Database.db as cursor :

	quick = Quick.Quick( Database.db, cursor )
	
	if isOrganism :
		cursor.execute( "DELETE FROM " + Config.DB_QUICK + ".quick_identifiers WHERE organism_id=%s", [inputArgs['organismID']] )
		cursor.execute( "SELECT gene_id, systematic_name, official_symbol, aliases, definition, external_ids, external_ids_types, organism_id, organism_common_name, organism_official_name, organism_abbreviation, organism_strain, uniprot_aliases FROM " + Config.DB_QUICK + ".quick_annotation WHERE organism_id=%s", [inputArgs['organismID']] )

	elif isGene :
		cursor.execute( "DELETE FROM " + Config.DB_QUICK + ".quick_identifiers WHERE gene_id=%s", [inputArgs['geneID']] )
		cursor.execute( "SELECT gene_id, systematic_name, official_symbol, aliases, definition, external_ids, external_ids_types, organism_id, organism_common_name, organism_official_name, organism_abbreviation, organism_strain, uniprot_aliases FROM " + Config.DB_QUICK + ".quick_annotation WHERE gene_id=%s", [inputArgs['geneID']] )
		
	elif isDate :
		cursor.execute( "DELETE FROM " + Config.DB_QUICK + ".quick_identifiers WHERE gene_id IN (SELECT gene_id FROM " + Config.DB_NAME + ".genes WHERE gene_updated>%s AND gene_status='active')", [inputArgs['dateVal']] )
		cursor.execute( "SELECT gene_id, systematic_name, official_symbol, aliases, definition, external_ids, external_ids_types, organism_id, organism_common_name, organism_official_name, organism_abbreviation, organism_strain, uniprot_aliases FROM " + Config.DB_QUICK + ".quick_annotation WHERE gene_id IN (SELECT gene_id FROM " + Config.DB_NAME + ".genes WHERE gene_updated>%s AND gene_status='active')", [inputArgs['dateVal']] )
		
	else :
		cursor.execute( "TRUNCATE TABLE " + Config.DB_QUICK + ".quick_identifiers" )
		Database.db.commit( )
		
		cursor.execute( "SELECT gene_id, systematic_name, official_symbol, aliases, definition, external_ids, external_ids_types, organism_id, organism_common_name, organism_official_name, organism_abbreviation, organism_strain, uniprot_aliases FROM " + Config.DB_QUICK + ".quick_annotation ORDER BY gene_id ASC" )
	
	Database.db.commit( )
	recordSize = 12 # Number of Columns in quick_identifiers table
	
	sqlFormat = ",".join( ['%s'] * recordSize )
	query = "INSERT INTO " + Config.DB_QUICK + ".quick_identifiers VALUES (%s)" % sqlFormat
	
	insertCount = 0
	for row in cursor.fetchall( ) :
	
		duplicates = set( )
	
		record = [row[0]] # Before ID data
		recordBase = [row[1],row[2],row[4],row[7],row[8],row[9],row[10],row[11], '0'] # After ID Data
		
		cursor.execute( query, tuple(record + [row[0], "BIOGRID"] + recordBase) )
		
		if "-" != row[1] :
			cursor.execute( query, tuple(record + [row[1], "SYSTEMATIC NAME"] + recordBase) )
			cursor.execute( query, tuple(record + [row[1], "ORDERED LOCUS"] + recordBase) )
			duplicates.add( str(row[1].upper( )) )
			
		if "-" != row[2] :
			cursor.execute( query, tuple(record + [row[2], "OFFICIAL SYMBOL"] + recordBase) )
			duplicates.add( str(row[2].upper( )) )
			
		if "-" != row[3] :
			aliases = row[3].split( "|" )
			for alias in aliases :
				if alias.upper( ) != row[1].upper( ) and alias.upper( ) != row[2].upper( ) and str(alias.upper( )) not in duplicates :
					cursor.execute( query, tuple(record + [alias, "SYNONYM"] + recordBase) )
					duplicates.add( str(alias.upper( )) )
					
		if "-" != row[12] :
			aliases = row[12].split( "|" )
			for alias in aliases :
				if alias.upper( ) != row[1].upper( ) and alias.upper( ) != row[2].upper( ) and str(alias.upper( )) not in duplicates :
					cursor.execute( query, tuple(record + [alias, "SYNONYM"] + recordBase) )
					duplicates.add( str(alias.upper( )) )
				
		if "-" != row[5] :
			externalIDs = row[5].split( "|" )
			externalTypes = row[6].split( "|" )
			
			for externalID, externalType in zip( externalIDs, externalTypes ) :
				cursor.execute( query, tuple(record + [externalID, externalType] + recordBase) )
				
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'QUICK_buildIdentifiers', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )		