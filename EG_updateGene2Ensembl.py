
# Parse all the mappings to Ensembl IDs
# into the external identifiers table for
# an organism of interest.

import Config
import sys, string, argparse
import MySQLdb
import Database
import gzip

from classes import EntrezGene

# Process Command Line Input
argParser = argparse.ArgumentParser( description = 'Update all Ensembl External IDs from Entrez Gene that are relevant to the organism id passed in via the command line.' )
argParser.add_argument( '-o', help = 'NCBI Organism ID', type=int, dest = 'organismID', required=True, action='store' )
inputArgs = vars( argParser.parse_args( ) )

with Database.db as cursor :

	entrezGene = EntrezGene.EntrezGene( Database.db, cursor )
	organismList = entrezGene.fetchEntrezGeneOrganismMapping( )
	
	organismID = 0
	if inputArgs['organismID'] in organismList :
		organismID = organismList[inputArgs['organismID']]
		
	existingEntrezGeneIDs = entrezGene.fetchExistingEntrezGeneIDsByOrganism( organismID )
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
				cursor.execute( "UPDATE " + Config.DB_NAME + ".gene_externals SET gene_external_status='inactive' WHERE gene_id=%s AND gene_external_source = 'ENSEMBL'", [currentGeneID] )

				if "-" != ensemblGeneID and ensemblGeneID.upper( ) not in ensemblHash :
				
					cursor.execute( "SELECT gene_external_id FROM " + Config.DB_NAME + ".gene_externals WHERE gene_external_value=%s AND gene_external_source=%s AND gene_id=%s LIMIT 1", [ensemblGeneID.upper( ), 'ENSEMBL', currentGeneID] )
					row = cursor.fetchone( )
					
					if None == row :
						print "INSERTING ENSEMBL"
						cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_externals VALUES( '0',%s,%s,'active',NOW( ),%s )", [ensemblGeneID.upper( ), 'ENSEMBL', currentGeneID] )
					else :
						print "UPDATING ENSEMBL"
						cursor.execute( "UPDATE " + Config.DB_NAME + ".gene_externals SET gene_external_status='active', gene_external_modified=NOW( ) WHERE gene_external_id=%s", [row[0]] )

				if "-" != ensemblRNAID and ensemblRNAID.upper( ) not in ensemblHash :
				
					cursor.execute( "SELECT gene_external_id FROM " + Config.DB_NAME + ".gene_externals WHERE gene_external_value=%s AND gene_external_source=%s AND gene_id=%s LIMIT 1", [ensemblRNAID.upper( ), 'ENSEMBL', currentGeneID] )
					row = cursor.fetchone( )
					
					if None == row :
						print "INSERTING ENSEMBL RNA"
						cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_externals VALUES( '0',%s,%s,'active',NOW( ),%s )", [ensemblRNAID.upper( ), 'ENSEMBL', currentGeneID] )
					else :
						print "UPDATING ENSEMBL RNA"
						cursor.execute( "UPDATE " + Config.DB_NAME + ".gene_externals SET gene_external_status='active', gene_external_modified=NOW( ) WHERE gene_external_id=%s", [row[0]] )

				if "-" != ensemblProteinID and ensemblProteinID.upper( ) not in ensemblHash :
				
					cursor.execute( "SELECT gene_external_id FROM " + Config.DB_NAME + ".gene_externals WHERE gene_external_value=%s AND gene_external_source=%s AND gene_id=%s LIMIT 1", [ensemblProteinID.upper( ), 'ENSEMBL', currentGeneID] )
					row = cursor.fetchone( )
					
					if None == row :
						print "INSERTING ENSEMBL PROTEIN"
						cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_externals VALUES( '0',%s,%s,'active',NOW( ),%s )", [ensemblProteinID.upper( ), 'ENSEMBL', currentGeneID] )
					else :
						print "UPDATING ENSEMBL PROTEIN"
						cursor.execute( "UPDATE " + Config.DB_NAME + ".gene_externals SET gene_external_status='active', gene_external_modified=NOW( ) WHERE gene_external_id=%s", [row[0]] )
				
			if 0 == (insertCount % Config.DB_COMMIT_COUNT ) :
				Database.db.commit( )
					
		Database.db.commit( )
			
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'EG_updateGene2Ensembl', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )
			