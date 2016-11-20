
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
argGroup.add_argument( '-r', dest='refseqID', type = int, nargs = 1, help = 'A Refseq ID to Update', action='store' )
argGroup.add_argument( '-d', dest='dateVal', type = str, nargs = 1, help = 'A date value (YYYY-MM-DD 00:00:00)', action='store' )
argGroup.add_argument( '-all', dest='allRecords', help = 'Build from All Records, Starting from Scratch', action='store_true' )
inputArgs = vars( argParser.parse_args( ) )

isOrganism = False
isRefseq = False
isDate = False
isAll = False

if None != inputArgs['organismID'] :
	isOrganism = True
elif None != inputArgs['refseqID'] :
	isRefseq = True
elif None != inputArgs['dateVal'] :
	isDate = True
else :
	isAll = True


with Database.db as cursor :

	quick = Quick.Quick( Database.db, cursor )
	
	if isOrganism :
		cursor.execute( "DELETE FROM " + Config.DB_QUICK + ".quick_refseq_identifiers WHERE organism_id=%s", [inputArgs['organismID']] )
		cursor.execute( "SELECT refseq_id, refseq_accession, refseq_gi, refseq_description, refseq_version, organism_id, organism_common_name, organism_official_name, organism_abbreviation, organism_strain, interaction_count, refseq_aliases, refseq_uniprot_aliases, refseq_externalids, refseq_externalids_types FROM " + Config.DB_QUICK + ".quick_refseq WHERE organism_id=%s", [inputArgs['organismID']] )

	elif isRefseq :
		cursor.execute( "DELETE FROM " + Config.DB_QUICK + ".quick_refseq_identifiers WHERE refseq_id=%s", [inputArgs['refseqID']] )
		cursor.execute( "SELECT refseq_id, refseq_accession, refseq_gi, refseq_description, refseq_version, organism_id, organism_common_name, organism_official_name, organism_abbreviation, organism_strain, interaction_count, refseq_aliases, refseq_uniprot_aliases, refseq_externalids, refseq_externalids_types FROM " + Config.DB_QUICK + ".quick_refseq WHERE refseq_id=%s", [inputArgs['refseqID']] )
		
	elif isDate :
		cursor.execute( "DELETE FROM " + Config.DB_QUICK + ".quick_refseq_identifiers WHERE refseq_id IN ( SELECT refseq_id FROM " + Config.DB_NAME + ".refseq WHERE refseq_modified>%s AND refseq_status='active')", [inputArgs['dateVal']] )
		cursor.execute( "SELECT refseq_id, refseq_accession, refseq_gi, refseq_description, refseq_version, organism_id, organism_common_name, organism_official_name, organism_abbreviation, organism_strain, interaction_count, refseq_aliases, refseq_uniprot_aliases, refseq_externalids, refseq_externalids_types FROM " + Config.DB_QUICK + ".quick_refseq WHERE refseq_id IN ( SELECT refseq_id FROM " + Config.DB_NAME + ".refseq WHERE refseq_modified>%s AND refseq_status='active')", [inputArgs['dateVal']] )
		
	else :
		cursor.execute( "TRUNCATE TABLE " + Config.DB_QUICK + ".quick_refseq_identifiers" )
		Database.db.commit( )

		cursor.execute( "SELECT refseq_id, refseq_accession, refseq_gi, refseq_description, refseq_version, organism_id, organism_common_name, organism_official_name, organism_abbreviation, organism_strain, interaction_count, refseq_aliases, refseq_uniprot_aliases, refseq_externalids, refseq_externalids_types FROM " + Config.DB_QUICK + ".quick_refseq ORDER BY refseq_id ASC" )
	
	recordSize = 13 # Number of Columns in quick_protein_identifiers table
	
	sqlFormat = ",".join( ['%s'] * recordSize )
	query = "INSERT INTO " + Config.DB_QUICK + ".quick_refseq_identifiers VALUES (%s)" % sqlFormat
	
	insertCount = 0
	for row in cursor.fetchall( ) :
	
		record = [row[0]] # Before ID data
		recordBase = [row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]] # After ID Data
		
		print "Working on: " + str(insertCount)
		
		cursor.execute( query, tuple(record + [row[0], "BIOGRID_REFSEQ_ID"] + recordBase) )
		
		if "-" != row[1] :
			cursor.execute( query, tuple(record + [row[1], "REFSEQ-PROTEIN-ACCESSION"] + recordBase) )
			
		if "-" != row[2] :
			cursor.execute( query, tuple(record + [row[2], "REFSEQ-PROTEIN-GI"] + recordBase) )
			
		if "-" != row[11] :
			aliases = row[11].split( "|" )
			for alias in aliases :
				if str(alias).upper( ) != str(row[1]).upper( ) and str(alias).upper( ) != str(row[2]).upper( ) :
					cursor.execute( query, tuple(record + [alias, "SYNONYM"] + recordBase) )
					
		if "-" != row[12] :
			aliases = row[12].split( "|" )
			for alias in aliases :
				if str(alias).upper( ) != str(row[1]).upper( ) and str(alias).upper( ) != str(row[2]).upper( ) :
					cursor.execute( query, tuple(record + [alias, "SYNONYM"] + recordBase) )
				
		if "-" != row[13] :
			externalIDs = row[13].split( "|" )
			externalTypes = row[14].split( "|" )
			
			for externalID, externalType in zip( externalIDs, externalTypes ) :
				cursor.execute( query, tuple(record + [str(externalID).upper( ), externalType] + recordBase) )
				
		insertCount = insertCount + 1
				
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'QUICK_buildRefseqIdentifiers', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )		