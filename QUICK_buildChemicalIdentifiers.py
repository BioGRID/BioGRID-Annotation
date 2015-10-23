
# Create the quick lookup chemical identifier
# table by combining annotation from other
# resources into a single table.

import Config
import sys, string, argparse
import MySQLdb
import Database

from classes import Quick

# Process Command Line Input
argParser = argparse.ArgumentParser( description = 'Update all Annotation Records' )
argGroup = argParser.add_mutually_exclusive_group( )
argGroup.add_argument( '-c', dest='chemicalID', type = int, nargs = 1, help = 'A Chemical ID to Update', action='store' )
argGroup.add_argument( '-all', dest='allRecords', help = 'Build from All Records, Starting from Scratch', action='store_true' )
inputArgs = vars( argParser.parse_args( ) )

isChem = False
isAll = False

if None != inputArgs['chemicalID'] :
	isChem = True
else :
	isAll = True

with Database.db as cursor :

	quick = Quick.Quick( Database.db, cursor )

	if isChem :
		cursor.execute( "DELETE FROM " + Config.DB_QUICK + ".quick_chemical_identifiers WHERE chemical_id=%s", [inputArgs['chemicalID']] )
		cursor.execute( "SELECT chemical_id, chemical_name, chemical_desc, chemical_type, chemical_source, chemical_source_id, chemical_synonyms, chemical_brands, chemical_formula, chemical_casnumber, chemical_atc_codes, chemical_external_ids_types, chemical_external_ids, chemical_smiles FROM " + Config.DB_QUICK + ".quick_chemicals WHERE chemical_id=%s", [inputArgs['chemicalID']] )
		
	else :
		cursor.execute( "TRUNCATE TABLE " + Config.DB_QUICK + ".quick_chemical_identifiers" )
		Database.db.commit( )
		
		cursor.execute( "SELECT chemical_id, chemical_name, chemical_desc, chemical_type, chemical_source, chemical_source_id, chemical_synonyms, chemical_brands, chemical_formula, chemical_casnumber, chemical_atc_codes, chemical_external_ids, chemical_external_ids_types, chemical_smiles FROM " + Config.DB_QUICK + ".quick_chemicals ORDER BY chemical_id ASC" )
	
	Database.db.commit( )
	recordSize = 11 # Number of Columns in quick_chemical_identifiers table
	
	sqlFormat = ",".join( ['%s'] * recordSize )
	query = "INSERT INTO " + Config.DB_QUICK + ".quick_chemical_identifiers VALUES (%s)" % sqlFormat
	
	insertCount = 0
	for row in cursor.fetchall( ) :
	
		duplicates = set( )
	
		record = [row[0]] # Before ID data
		recordBase = [row[1],row[2],row[3],row[4],row[5],row[6],row[7], '0'] # After ID Data
		
		cursor.execute( query, tuple(record + [row[0], "BIOGRID"] + recordBase) )
		cursor.execute( query, tuple(record + [row[1], "OFFICIAL NAME"] + recordBase) )
		duplicates.add( str(row[1]).upper( ) )
		
		# SOURCE ID
		cursor.execute( query, tuple(record + [row[5], row[4].upper( )] + recordBase) )
		
		# MOLECULAR FORMULA
		if "-" != row[8] :
			cursor.execute( query, tuple(record + [row[8], "MOLECULAR_FORMULA"] + recordBase) )
		
		# SYNONYMS	
		if "-" != row[6] :
			synonyms = row[6].split( "|" )
			for synonym in synonyms :
				if str(synonym.upper( )) not in duplicates :
					cursor.execute( query, tuple(record + [synonym, "SYNONYM"] + recordBase) )
					duplicates.add( str(synonym.upper( )) )
					
		# BRANDS	
		if "-" != row[7] :
			brands = row[7].split( "|" )
			for brand in brands :
				if str(brand.upper( )) not in duplicates :
					cursor.execute( query, tuple(record + [brand, "BRAND_NAME"] + recordBase) )
					duplicates.add( str(brand.upper( )) )
					
		# CAS NUMBER
		if "-" != row[9] :
			cursor.execute( query, tuple(record + [row[9], "CAS_NUMBER"] + recordBase) )
			
		# ATC CODES	
		if "-" != row[10] :
			atcCodes = row[10].split( "|" )
			for atcCode in atcCodes :
				if str(atcCode.upper( )) not in duplicates :
					cursor.execute( query, tuple(record + [atcCode, "ATC_CODE"] + recordBase) )
					duplicates.add( str(atcCode.upper( )) )
		
		# EXTERNAL IDS
		if "-" != row[11] :
			externalIDs = row[11].split( "|" )
			externalTypes = row[12].split( "|" )
			
			for externalID, externalType in zip( externalIDs, externalTypes ) :
				cursor.execute( query, tuple(record + [externalID, externalType.replace( ' ', '_' )] + recordBase) )
				
		# SMILES
		if "-" != row[13] :
			cursor.execute( query, tuple(record + [row[13], "SMILE"] + recordBase) )
				
				
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'QUICK_buildChemicalIdentifiers', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )		