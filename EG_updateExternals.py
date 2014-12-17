
# Parse all external database ids for genes from Entrez Gene that
# are relevant to the organism we want loaded

import Config
import sys, string, argparse
import MySQLdb
import Database
import gzip

from classes import EntrezGene

# Process Command Line Input
argParser = argparse.ArgumentParser( description = 'Update all External IDs from Entrez Gene that are relevant to the organism id passed in via the command line.' )
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
			dbxrefs = (splitLine[5].strip( )).split( "|" )
			
			if sourceID in existingEntrezGeneIDs :
				
				currentGeneID = existingEntrezGeneIDs[sourceID]
				cursor.execute( "UPDATE " + Config.DB_NAME + ".gene_externals SET gene_external_status='inactive' WHERE gene_id=%s AND gene_external_source != 'GRID LEGACY'", [currentGeneID] )
								
				if "-" == splitLine[5].strip( ) :
					dbxrefs = []
					
				dbxrefs.append( "ENTREZ_GENE:" + str(currentGeneID) )
				dbxrefs.append( "ENTREZ_GENE_ETG:ETG" + str(currentGeneID) )
				
				insertCount = insertCount + 1
				for dbxref in dbxrefs :
					dbxrefInfo = dbxref.split( ":" )
						
					cursor.execute( "SELECT gene_external_id FROM " + Config.DB_NAME + ".gene_externals WHERE gene_external_value=%s AND gene_external_source=%s AND gene_id=%s LIMIT 1", [dbxrefInfo[1].strip( ), dbxrefInfo[0].strip( ).upper( ), currentGeneID] )
					row = cursor.fetchone( )
						
					if None == row :
						print "INSERTING EXTERNAL"
						cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_externals VALUES ( '0', %s, %s, 'active', NOW( ), %s )", [dbxrefInfo[1].strip( ), dbxrefInfo[0].strip( ).upper( ), currentGeneID] )
					else :
						print "UPDATING EXTERNAL"
						cursor.execute( "UPDATE " + Config.DB_NAME + ".gene_externals SET gene_external_status='active', gene_external_modified=NOW( ) WHERE gene_external_id=%s", [row[0]] )

									
			if 0 == (insertCount % Config.DB_COMMIT_COUNT ) :
				Database.db.commit( )
		
	Database.db.commit( )
	
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'EG_updateExternals', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )
			