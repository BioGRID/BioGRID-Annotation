
# Parse all the refseq mappings to Ensembl IDs
# into the external identifiers table

import Config
import sys, string
import MySQLdb
import Database
import gzip

from classes import EntrezGene

with Database.db as cursor :

	entrezGene = EntrezGene.EntrezGene( Database.db, cursor )
	
	existingEntrezGeneIDs = entrezGene.fetchExistingEntrezGeneIDs( )
	ensemblHash = entrezGene.fetchEnsemblHash( )
	
	insertCount = 0
	with gzip.open( Config.EG_GENE2ENSEMBL, 'r' ) as file :
		for line in file.readlines( ) :
			
			line = line.strip( )
			
			# Ignore Header Line
			if "#" == line[0] :
				continue
				
			splitLine = line.split( "\t" )
			entrezGeneTaxID = int(splitLine[0].strip( ))
			sourceID = splitLine[1].strip( )
			ensemblGeneID = splitLine[2].strip( )
			ensemblRNAID = splitLine[4].strip( )
			ensemblProteinID = splitLine[6].strip( )
			
			if sourceID in existingEntrezGeneIDs :
			
				insertCount = insertCount + 1
				currentGeneID = existingEntrezGeneIDs[sourceID]
				
				if "-" != ensemblGeneID and ensemblGeneID.upper( ) not in ensemblHash :
					cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_externals VALUES( '0',%s,%s,'active',NOW( ),%s )", [ensemblGeneID.upper( ), 'ENSEMBL GENE', currentGeneID] )
				
				if "-" != ensemblRNAID and ensemblRNAID.upper( ) not in ensemblHash :
					cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_externals VALUES( '0',%s,%s,'active',NOW( ),%s )", [ensemblRNAID.upper( ), 'ENSEMBL RNA', currentGeneID] )

				if "-" != ensemblProteinID and ensemblProteinID.upper( ) not in ensemblHash :
					cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_externals VALUES( '0',%s,%s,'active',NOW( ),%s )", [ensemblProteinID.upper( ), 'ENSEMBL PROTEIN', currentGeneID] )
				
			if 0 == (insertCount % Config.DB_COMMIT_COUNT ) :
				Database.db.commit( )
					
		Database.db.commit( )
			
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'EG_parseGene2Ensembl', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )
			