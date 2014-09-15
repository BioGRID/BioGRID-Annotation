
# Parse all aliases for genes from Entrez Gene that
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
	
	cursor.execute( "TRUNCATE TABLE " + Config.DB_NAME + ".gene_aliases" )
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
			officialSymbol = splitLine[2].strip( )
			systematicName = splitLine[3].strip( )
			synonyms = (splitLine[4].strip( )).split( "|" )
			
			if sourceID in existingEntrezGeneIDs :
				currentGeneID = existingEntrezGeneIDs[sourceID]
			
				if "-" != officialSymbol :
					insertCount = insertCount + 1
					cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_aliases VALUES ( '0', %s, 'active', 'entrez-official', NOW( ), %s )", [officialSymbol, currentGeneID] )
					
				if "-" != systematicName :
					insertCount = insertCount + 1
					cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_aliases VALUES ( '0', %s, 'active', 'ordered locus', NOW( ), %s )", [systematicName, currentGeneID] )
					
				if "-" != splitLine[4].strip( ) :
					insertCount = insertCount + 1
					for synonym in synonyms :
						synonym = synonym.strip( )
						if synonym.lower( ) != officialSymbol.lower( ) and synonym.lower( ) != systematicName.lower( ) :
							cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_aliases VALUES ( '0', %s, 'active', 'synonym', NOW( ), %s )", [synonym, currentGeneID] )
			
			if 0 == (insertCount % Config.DB_COMMIT_COUNT ) :
				Database.db.commit( )
				
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'EG_parseAliases', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )
			