
# Parse all genes from Entrez Gene that
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
	organismList = entrezGene.fetchEntrezGeneOrganismMapping( )
	existingEntrezGeneIDs = entrezGene.fetchExistingEntrezGeneIDs( )

	missingOrgs = set( )
	
	insertCount = 0
	with gzip.open( Config.EG_GENEINFO, 'r' ) as file :
		for line in file.readlines( ) :
			
			line = line.strip( )
			
			# Ignore Header Line
			if "#" == line[0] :
				continue
				
			splitLine = line.split( "\t" )
			entrezGeneTaxID = int(splitLine[0].strip( ))
			sourceID = splitLine[1].strip( )
			officialSymbol = splitLine[2].strip( )
			geneType = splitLine[9].strip( )
			
			# Skip NEWENTRY records
			if "NEWENTRY" == officialSymbol :
				continue
			
			if sourceID in existingEntrezGeneIDs :
			
				currentGeneID = existingEntrezGeneIDs[sourceID]
				
				# Found Gene ID already in the Database
				# If for Organism we want
				# Update info with no problems
				if entrezGeneTaxID in organismList :
					insertCount = insertCount + 1
					cursor.execute( "UPDATE " + Config.DB_NAME + ".genes SET gene_type=%s, gene_name=%s, gene_name_type=%s, gene_status='active', gene_updated=NOW( ) WHERE gene_id=%s", [geneType, officialSymbol, 'entrez-official', currentGeneID] )
				else :
					# Found Gene ID for Organism that is
					# no longer one we are looking for
					# add to list of missing organisms
					insertCount = insertCount + 1
					cursor.execute( "UPDATE " + Config.DB_NAME + ".genes SET gene_status='inactive' WHERE gene_id=%s", [currentGeneID] )
					cursor.execute( "INSERT INTO " + Config.DB_STATS + ".gene_history VALUES( '0','DISCONTINUED',%s,%s,'-','Discontinued Due to Deprecated Organism', NOW( ) )", [currentGeneID,sourceID] )
					missingOrgs.add( entrezGeneTaxID )
			
			else :
				
				# Not already in Database
				# Check to see if it's an organism we want
				# if so, insert it.
				if entrezGeneTaxID in organismList :
					insertCount = insertCount + 1
					taxID = organismList[entrezGeneTaxID]
					cursor.execute( "INSERT INTO " + Config.DB_NAME + ".genes VALUES( '0', %s, %s, %s, %s, %s, 'active', NOW( ), NOW( ), %s, '0' )", [officialSymbol, 'entrez-official', sourceID, geneType, taxID, 'ENTREZ'] )
			
			if 0 == (insertCount % Config.DB_COMMIT_COUNT ) :
				Database.db.commit( )
				
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'EG_parseGenes', NOW( ) )" )
	Database.db.commit( )
				
	print missingOrgs
	
sys.exit( )
			