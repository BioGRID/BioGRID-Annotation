
# Update all genes from Entrez Gene that
# are relevant to the organism we passed in via the
# command line

import Config
import sys, string, argparse
import MySQLdb
import Database
import gzip

from classes import EntrezGene

# Process Command Line Input
argParser = argparse.ArgumentParser( description = 'Update all genes from Entrez Gene that are relevant to the organism id passed in via the command line.' )
argParser.add_argument( '-o', help = 'NCBI Organism ID', type=int, dest = 'organismID', required=True, action='store' )
inputArgs = vars( argParser.parse_args( ) )

with Database.db as cursor :

	entrezGene = EntrezGene.EntrezGene( Database.db, cursor )
	organismList = entrezGene.fetchEntrezGeneOrganismMapping( )
	
	organismID = 0
	if inputArgs['organismID'] in organismList :
		organismID = organismList[inputArgs['organismID']]
		
	existingEntrezGeneIDs = entrezGene.fetchExistingEntrezGeneIDsByOrganism( organismID )
	
	cursor.execute( "UPDATE " + Config.DB_NAME + ".genes SET gene_status='inactive' WHERE organism_id=%s", [organismID] )
	Database.db.commit( )
	
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
				
			if inputArgs['organismID'] == entrezGeneTaxID :
				
				if sourceID in existingEntrezGeneIDs :
			
					# Found Gene ID already in the Database
					# Update info with no problems
					currentGeneID = existingEntrezGeneIDs[sourceID]
					insertCount = insertCount + 1
					print "UPDATING EXISTING GENE"
					cursor.execute( "UPDATE " + Config.DB_NAME + ".genes SET gene_type=%s, gene_name=%s, gene_name_type=%s, gene_status='active', gene_updated=NOW( ) WHERE gene_id=%s", [geneType, officialSymbol, 'entrez-official', currentGeneID] )
					
				else :
				
					# Not already in Database
					# insert it.
					insertCount = insertCount + 1
					print "INSERTING NEW GENE"
					cursor.execute( "INSERT INTO " + Config.DB_NAME + ".genes VALUES( '0', %s, %s, %s, %s, %s, 'active', NOW( ), NOW( ), %s, '0' )", [officialSymbol, 'entrez-official', sourceID, geneType, organismID, 'ENTREZ'] )
			
			if 0 == (insertCount % Config.DB_COMMIT_COUNT ) :
				Database.db.commit( )
				
	Database.db.commit( )
				
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'EG_updateGenes', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )
			