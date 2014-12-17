
# Parse all definitions for genes from Entrez Gene that
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
			definition = splitLine[8].strip( )
			fullName = splitLine[11].strip( )
			otherDesignations = (splitLine[13].strip( )).split( "|" )
			
			if sourceID in existingEntrezGeneIDs :
				
				currentGeneID = existingEntrezGeneIDs[sourceID]
				cursor.execute( "UPDATE " + Config.DB_NAME + ".gene_definitions SET gene_definition_status='inactive' WHERE gene_id=%s", [currentGeneID] )
								
				if "-" != definition :
				
					insertCount = insertCount + 1
					cursor.execute( "SELECT gene_definition_id FROM " + Config.DB_NAME + ".gene_definitions WHERE gene_definition_text=%s AND gene_definition_source='ENTREZ-DESCRIPTION' AND gene_id=%s LIMIT 1", [definition, currentGeneID] )
					row = cursor.fetchone( )
					
					if None == row :
						print "INSERTING ENTREZ-DESCRIPTION"
						cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_definitions VALUES ( '0', %s, 'ENTREZ-DESCRIPTION', 'active', NOW( ), %s )", [definition, currentGeneID] )
					else :
						print "UPDATING ENTREZ-DESCRIPTION"
						cursor.execute( "UPDATE " + Config.DB_NAME + ".gene_definitions SET gene_definition_status='active', gene_definition_modified=NOW( ) WHERE gene_definition_id=%s", [row[0]] )
								
				if "-" != fullName and fullName.lower( ) != definition.lower( ) :
				
					insertCount = insertCount + 1
					cursor.execute( "SELECT gene_definition_id FROM " + Config.DB_NAME + ".gene_definitions WHERE gene_definition_text=%s AND gene_definition_source='ENTREZ-NOMENNAME' AND gene_id=%s LIMIT 1", [fullName, currentGeneID] )
					row = cursor.fetchone( )
					
					if None == row :
						print "INSERTING ENTREZ-NOMENNAME"
						cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_definitions VALUES ( '0', %s, 'ENTREZ-NOMENNAME', 'active', NOW( ), %s )", [fullName, currentGeneID] )			
					else :
						print "UPDATING ENTREZ-NOMENNAME"
						cursor.execute( "UPDATE " + Config.DB_NAME + ".gene_definitions SET gene_definition_status='active', gene_definition_modified=NOW( ) WHERE gene_definition_id=%s", [row[0]] )
							
				if "-" != splitLine[13].strip( ) :
				
					insertCount = insertCount + 1
					for otherDesignation in otherDesignations :
						otherDesignation = otherDesignation.strip( )
						if otherDesignation != "-" and otherDesignation.lower( ) != definition.lower( ) and otherDesignation.lower( ) != fullName.lower( ) :
							cursor.execute( "SELECT gene_definition_id FROM " + Config.DB_NAME + ".gene_definitions WHERE gene_definition_text=%s AND gene_definition_source='ENTREZ-OTHERDESIGNATION' AND gene_id=%s LIMIT 1", [otherDesignation, currentGeneID] )
							row = cursor.fetchone( )
							
							if None == row :
								print "INSERTING ENTREZ-OTHERDESIGNATION"
								cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_definitions VALUES ( '0', %s, 'ENTREZ-OTHERDESIGNATION', 'active', NOW( ), %s )", [otherDesignation, currentGeneID] )
							else :
								print "UPDATING ENTREZ-OTHERDESIGNATION"
								cursor.execute( "UPDATE " + Config.DB_NAME + ".gene_definitions SET gene_definition_status='active', gene_definition_modified=NOW( ) WHERE gene_definition_id=%s", [row[0]] )

			
			if 0 == (insertCount % Config.DB_COMMIT_COUNT ) :
				Database.db.commit( )
				
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'EG_updateDefinitions', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )
			