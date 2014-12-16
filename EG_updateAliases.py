
# Update all aliases for genes from Entrez Gene that
# are relevant to the organism we want loaded

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
				cursor.execute( "UPDATE " + Config.DB_NAME + ".gene_aliases SET gene_alias_status='inactive' WHERE gene_id=%s", [currentGeneID] )
			
				if "-" != officialSymbol :
				
					insertCount = insertCount + 1
					cursor.execute( "SELECT gene_alias_id FROM " + Config.DB_NAME + ".gene_aliases WHERE gene_alias_value=%s AND gene_alias_type='entrez-official' AND gene_id=%s LIMIT 1", [officialSymbol, currentGeneID] )
					row = cursor.fetchone( )
					
					if None == row :
						print "INSERTING OFFICIAL"
						cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_aliases VALUES ( '0', %s, 'active', 'entrez-official', NOW( ), %s )", [officialSymbol, currentGeneID] )
					else :
						print "UPDATING OFFICIAL"
						cursor.execute( "UPDATE " + Config.DB_NAME + ".gene_aliases SET gene_alias_status='active', gene_alias_modified=NOW( ) WHERE gene_alias_id=%s", [row[0]] )
					
				if "-" != systematicName :
					
					insertCount = insertCount + 1
					cursor.execute( "SELECT gene_alias_id FROM " + Config.DB_NAME + ".gene_aliases WHERE gene_alias_value=%s AND gene_alias_type='ordered locus' AND gene_id=%s LIMIT 1", [systematicName, currentGeneID] )
					row = cursor.fetchone( )
					
					if None == row :
						print "INSERTING SYSTEMATIC"
						cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_aliases VALUES ( '0', %s, 'active', 'ordered locus', NOW( ), %s )", [systematicName, currentGeneID] )
					else :
						print "UPDATING SYSTEMATIC"
						cursor.execute( "UPDATE " + Config.DB_NAME + ".gene_aliases SET gene_alias_status='active', gene_alias_modified=NOW( ) WHERE gene_alias_id=%s", [row[0]] )
					
				if "-" != splitLine[4].strip( ) :
					insertCount = insertCount + 1
					for synonym in synonyms :
						synonym = synonym.strip( )
						if synonym.lower( ) != officialSymbol.lower( ) and synonym.lower( ) != systematicName.lower( ) :
						
							cursor.execute( "SELECT gene_alias_id FROM " + Config.DB_NAME + ".gene_aliases WHERE gene_alias_value=%s AND gene_alias_type='synonym' AND gene_id=%s LIMIT 1", [synonym, currentGeneID] )
							row = cursor.fetchone( )
							
							if None == row :
								print "INSERTING SYNONYM"
								cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_aliases VALUES ( '0', %s, 'active', 'synonym', NOW( ), %s )", [synonym, currentGeneID] )
							else :
								print "UPDATING SYNONYM"
								cursor.execute( "UPDATE " + Config.DB_NAME + ".gene_aliases SET gene_alias_status='active', gene_alias_modified=NOW( ) WHERE gene_alias_id=%s", [row[0]] )
			
			if 0 == (insertCount % Config.DB_COMMIT_COUNT ) :
				Database.db.commit( )
				
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'EG_updateAliases', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )
			