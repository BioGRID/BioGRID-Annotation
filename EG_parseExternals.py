
# Parse all external database ids for genes from Entrez Gene that
# are relevant to the organisms we want loaded
# via the organisms table.

import Config
import sys, string
import MySQLdb
import Database
import gzip

from classes import EntrezGene

with Database.db as cursor :

	entrezGene = EntrezGene.EntrezGene( Database.db, cursor )
	existingEntrezGeneIDs = entrezGene.fetchExistingEntrezGeneIDs( )
	
	cursor.execute( "DELETE FROM " + Config.DB_NAME + ".gene_externals WHERE gene_external_source != 'GRID LEGACY'" )
	Database.db.commit( )
	cursor.execute( "OPTIMIZE TABLE " + Config.DB_NAME + ".gene_externals" )
	Database.db.commit( )
	
	insertCount = 0
	with gzip.open( Config.EG_GENEINFO, 'r' ) as file :
		for line in file.readlines( ) :
			
			line = line.strip( )
			
			# Ignore Header Line
			if "#" == line[0] :
				continue
				
			splitLine = line.split( "\t" )
			sourceID = splitLine[1].strip( )
			dbxrefs = (splitLine[5].strip( )).split( "|" )
			
			if sourceID in existingEntrezGeneIDs :
				currentGeneID = existingEntrezGeneIDs[sourceID]
								
				if "-" != splitLine[5].strip( ) :
					insertCount = insertCount + 1
					for dbxref in dbxrefs :
						dbxrefInfo = dbxref.split( ":" )
						cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_externals VALUES ( '0', %s, 'ENTREZ_GENE', 'active', NOW( ), %s )", [sourceID, currentGeneID] )
						cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_externals VALUES ( '0', %s, 'ENTREZ_GENE_ETG', 'active', NOW( ), %s )", [sourceID, currentGeneID] )	
						cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_externals VALUES ( '0', %s, %s, 'active', NOW( ), %s )", [dbxrefInfo[1].strip( ), dbxrefInfo[0].strip( ).upper( ), currentGeneID] )
			
			if 0 == (insertCount % Config.DB_COMMIT_COUNT ) :
				Database.db.commit( )
				
	cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_externals SELECT '0', gene_source_id, 'SGD', 'active', NOW( ), gene_id FROM " + Config.DB_NAME + ".genes WHERE gene_source='SGD'" )
	Database.db.commit( )
		
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'EG_parseExternals', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )
			