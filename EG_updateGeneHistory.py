
# Uses staged entrez_gene_history
# table to update history and deprecation
# of currently supported genes 

import Config
import sys, string, time
import MySQLdb
import Database

from classes import EntrezGene

with Database.db as cursor :

	entrezGene = EntrezGene.EntrezGene( Database.db, cursor )

	cursor.execute( "TRUNCATE TABLE " + Config.DB_STATS + ".gene_history" )

	cursor.execute( "SELECT gene_id, gene_source_id FROM " + Config.DB_NAME + ".genes WHERE gene_source='ENTREZ' AND gene_status='ACTIVE'" )

	for row in cursor.fetchall( ) :
		entrezGene.processGeneHistory( row[0], row[1] )

	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'Entrez-Gene History', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )