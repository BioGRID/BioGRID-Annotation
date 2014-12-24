
# Create the quick lookup protein identifier
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
argGroup.add_argument( '-o', dest='organismID', type = int, nargs = 1, help = 'An organism id to update annotation for', action='store' )
argGroup.add_argument( '-p', dest='proteinID', type = int, nargs = 1, help = 'A Protein ID to Update', action='store' )
argGroup.add_argument( '-all', dest='allRecords', help = 'Build from All Records, Starting from Scratch', action='store_true' )
inputArgs = vars( argParser.parse_args( ) )

isOrganism = False
isProtein = False
isAll = False

if None != inputArgs['organismID'] :
	isOrganism = True
elif None != inputArgs['proteinID'] :
	isProtein = True
else :
	isAll = True


with Database.db as cursor :

	quick = Quick.Quick( Database.db, cursor )
	
	if isOrganism :
		cursor.execute( "DELETE FROM " + Config.DB_QUICK + ".quick_protein_identifiers WHERE organism_id=%s", [inputArgs['organismID']] )
		cursor.execute( "SELECT protein_id, protein_identifier_value, protein_isoform, protein_name, protein_description, protein_source, protein_version, organism_id, organism_common_name, organism_official_name, organism_abbreviation, organism_strain, interaction_count, protein_aliases, protein_externalids, protein_externalids_types FROM " + Config.DB_QUICK + ".quick_proteins WHERE organism_id=%s", [inputArgs['organismID']] )

	elif isProtein :
		cursor.execute( "DELETE FROM " + Config.DB_QUICK + ".quick_protein_identifiers WHERE protein_id=%s", [inputArgs['proteinID']] )
		cursor.execute( "SELECT protein_id, protein_identifier_value, protein_isoform, protein_name, protein_description, protein_source, protein_version, organism_id, organism_common_name, organism_official_name, organism_abbreviation, organism_strain, interaction_count, protein_aliases, protein_externalids, protein_externalids_types FROM " + Config.DB_QUICK + ".quick_proteins WHERE protein_id=%s", [inputArgs['proteinID']] )
		
	else :
		cursor.execute( "TRUNCATE TABLE " + Config.DB_QUICK + ".quick_protein_identifiers" )
		Database.db.commit( )

		cursor.execute( "SELECT protein_id, protein_identifier_value, protein_isoform, protein_name, protein_description, protein_source, protein_version, organism_id, organism_common_name, organism_official_name, organism_abbreviation, organism_strain, interaction_count, protein_aliases, protein_externalids, protein_externalids_types FROM " + Config.DB_QUICK + ".quick_proteins" )
	
	recordSize = 15 # Number of Columns in quick_protein_identifiers table
	
	sqlFormat = ",".join( ['%s'] * recordSize )
	query = "INSERT INTO " + Config.DB_QUICK + ".quick_protein_identifiers VALUES (%s)" % sqlFormat
	
	insertCount = 0
	for row in cursor.fetchall( ) :
	
		record = [row[0]] # Before ID data
		recordBase = [row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11], row[12]] # After ID Data
		
		cursor.execute( query, tuple(record + [row[0], "BIOGRID_PROTEIN"] + recordBase) )
		
		if "-" != row[1] :
			cursor.execute( query, tuple(record + [row[1], "PRIMARY ACCESSION"] + recordBase) )
			
		if "-" != row[3] :
			cursor.execute( query, tuple(record + [row[3], "OFFICIAL SYMBOL"] + recordBase) )
			
		if "-" != row[13] :
			aliases = row[13].split( "|" )
			for alias in aliases :
				if alias.upper( ) != row[1].upper( ) :
					cursor.execute( query, tuple(record + [alias, "SYNONYM"] + recordBase) )
				
		if "-" != row[14] :
			externalIDs = row[14].split( "|" )
			externalTypes = row[15].split( "|" )
			
			for externalID, externalType in zip( externalIDs, externalTypes ) :
				cursor.execute( query, tuple(record + [externalID, externalType] + recordBase) )
				
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'QUICK_buildProteinIdentifiers', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )		