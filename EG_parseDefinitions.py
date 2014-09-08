
# Parse all definitions for genes from Entrez Gene that
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
	
	cursor.execute( "TRUNCATE TABLE " + Config.DB_NAME + ".gene_definitions" )
	
	insertCount = 0
	with gzip.open( Config.EG_GENEINFO, 'r' ) as file :
		for line in file.readlines( ) :
			
			line = line.strip( )
			
			# Ignore Header Line
			if "#" == line[0] :
				continue
				
			splitLine = line.split( "\t" )
			sourceID = splitLine[1].strip( )
			definition = splitLine[8].strip( )
			fullName = splitLine[11].strip( )
			otherDesignations = (splitLine[13].strip( )).split( "|" )
			
			if sourceID in existingEntrezGeneIDs :
				currentGeneID = existingEntrezGeneIDs[sourceID]
								
				if "-" != definition :
					insertCount = insertCount + 1
					cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_definitions VALUES ( '0', %s, 'ENTREZ-DESCRIPTION', 'active', NOW( ), %s )", [definition, currentGeneID] )
								
				if "-" != fullName and fullName.lower( ) != definition.lower( ) :
					insertCount = insertCount + 1
					cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_definitions VALUES ( '0', %s, 'ENTREZ-NOMENNAME', 'active', NOW( ), %s )", [fullName, currentGeneID] )			
							
				if "-" != splitLine[13].strip( ) :
					insertCount = insertCount + 1
					for otherDesignation in otherDesignations :
						otherDesignation = otherDesignation.strip( )
						if otherDesignation != "-" and otherDesignation.lower( ) != definition.lower( ) and otherDesignation.lower( ) != fullName.lower( ) :
							cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_definitions VALUES ( '0', %s, 'ENTREZ-OTHERDESIGNATION', 'active', NOW( ), %s )", [otherDesignation, currentGeneID] )			
			
			if 0 == (insertCount % Config.DB_COMMIT_COUNT ) :
				Database.db.commit( )
				
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'EG_parseDefinitions', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )
			