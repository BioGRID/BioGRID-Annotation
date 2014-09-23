
# Create the quick lookup organism table

import Config
import sys, string
import MySQLdb
import Database

with Database.db as cursor :

	cursor.execute( "TRUNCATE TABLE " + Config.DB_QUICK + ".quick_organisms" )
	cursor.execute( "INSERT INTO " + Config.DB_QUICK + ".quick_organisms SELECT organism_id, organism_entrez_taxid, organism_uniprot_taxid, organism_common_name, organism_official_name, organism_abbreviation, organism_strain FROM " + Config.DB_NAME + ".organisms WHERE organism_status='active'" )
	Database.db.commit( )
	
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'QUICK_buildQuickOrganisms', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )