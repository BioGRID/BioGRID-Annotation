
# Create the quick lookup organism table

import Config
import sys, string
import MySQLdb
import Database

with Database.db as cursor :

	# EMPTY EXISTING DATA
	cursor.execute( "TRUNCATE TABLE " + Config.DB_QUICK + ".quick_organisms" )
	cursor.execute( "TRUNCATE TABLE " + Config.DB_QUICK + ".quick_protein_organisms" )
	
	# GRAB ONLY ORGANISMS THAT HAVE GENES AVAILABLE
	# IN OUR ANNOTATION
	cursor.execute( "SELECT organism_id FROM " + Config.DB_NAME + ".genes WHERE gene_status='active' GROUP BY organism_id" )
	
	orgIDs = set( )
	for row in cursor.fetchall( ) :
		orgIDs.add( row[0] )
		
	orgFormat = ",".join( ['%s'] * len(orgIDs) )
	cursor.execute( "INSERT INTO " + Config.DB_QUICK + ".quick_organisms SELECT organism_id, organism_entrez_taxid, organism_uniprot_taxid, organism_common_name, organism_official_name, organism_abbreviation, organism_strain FROM " + Config.DB_NAME + ".organisms WHERE organism_id IN (%s) AND organism_status='active'" % orgFormat, tuple(orgIDs) )
	Database.db.commit( )
	
	# GRAB ONLY ORGANISMS THAT HAVE PROTEINS AVAILABLE
	# IN OUR ANNOTATION
	cursor.execute( "SELECT organism_id FROM " + Config.DB_NAME + ".uniprot WHERE uniprot_status='active' GROUP BY organism_id" )
	
	orgIDs = set( )
	for row in cursor.fetchall( ) :
		orgIDs.add( row[0] )
		
	cursor.execute( "SELECT organism_id FROM " + Config.DB_NAME + ".refseq WHERE refseq_status='active' GROUP BY organism_id" )
	
	for row in cursor.fetchall( ) :
		orgIDs.add( row[0] )
		
	orgFormat = ",".join( ['%s'] * len(orgIDs) )
	cursor.execute( "INSERT INTO " + Config.DB_QUICK + ".quick_protein_organisms SELECT organism_id, organism_entrez_taxid, organism_uniprot_taxid, organism_common_name, organism_official_name, organism_abbreviation, organism_strain FROM " + Config.DB_NAME + ".organisms WHERE organism_id IN (%s) AND organism_status='active'" % orgFormat, tuple(orgIDs) )
	Database.db.commit( )
	
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'QUICK_buildOrganisms', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )