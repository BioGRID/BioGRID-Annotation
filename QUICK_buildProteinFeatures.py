
# Create the quick lookup protein features
# table by combining annotation from other
# resources into a single table.

import Config
import sys, string
import MySQLdb
import Database

from classes import Quick

with Database.db as cursor :

	quick = Quick.Quick( Database.db, cursor )

	cursor.execute( "TRUNCATE TABLE " + Config.DB_QUICK + ".quick_protein_features" )
	Database.db.commit( )
	
	cursor.execute( "SELECT * FROM " + Config.DB_NAME + ".uniprot_features" )
	
	recordSize = 8 # Number of Columns in quick_protein_features table
	
	sqlFormat = ",".join( ['%s'] * recordSize )
	query = "INSERT INTO " + Config.DB_QUICK + ".quick_protein_features VALUES (%s)" % sqlFormat
	
	insertCount = 0
	for row in cursor.fetchall( ) :
	
		record = [row[0], row[1], row[2], row[3], row[4], row[5], row[6]]
		proteinID = quick.fetchProteinIDByUniprotID( str(row[9]) )
		
		if proteinID :
			cursor.execute( query, tuple(record + [proteinID]) )
				
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'QUICK_buildProteinFeatures', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )		