
# Parse go mappings from ENTREZ GENE for genes
# that are specifically from the organism we are
# looking for.

import Config
import sys, string, argparse
import MySQLdb
import Database
import gzip

from classes import EntrezGene, GeneOntology

# Process Command Line Input
argParser = argparse.ArgumentParser( description = 'Update all GO from Entrez Gene that are relevant to the organism id passed in via the command line.' )
argGroup = argParser.add_mutually_exclusive_group( required=True )
argGroup.add_argument( '-o', help = 'NCBI Organism ID', type=int, dest = 'organismID', action='store' )
argGroup.add_argument( '-g', dest='genes', nargs = '+', help = 'An Entrez Gene ID List to Update', action='store' )
inputArgs = vars( argParser.parse_args( ) )

isOrganism = False
isGene = False

if None != inputArgs['organismID'] :
	isOrganism = True
elif None != inputArgs['genes'] :
	isGene = True

with Database.db as cursor :

	entrezGene = EntrezGene.EntrezGene( Database.db, cursor )
	geneOntology = GeneOntology.GeneOntology( Database.db, cursor )
	organismList = entrezGene.fetchEntrezGeneOrganismMapping( )
	existingEntrezGeneIDs = { }
	organismID = 0
	
	if isOrganism :
		if inputArgs['organismID'][0] in organismList :
			organismID = organismList[inputArgs['organismID'][0]]
			
		existingEntrezGeneIDs = entrezGene.fetchExistingEntrezGeneIDsByOrganism( organismID )
		
	elif isGene :
	
		for gene in inputArgs['genes'] :
			geneID = entrezGene.geneExists( gene )
		
			if geneID :
				existingEntrezGeneIDs[gene] = geneID
				
	for entrezGeneID, geneID in existingEntrezGeneIDs.iteritems( ) :		
		cursor.execute( "UPDATE " + Config.DB_NAME + ".gene_go SET gene_go_status='inactive' WHERE gene_id=%s", [geneID] )
	
	insertCount = 0
	with gzip.open( Config.EG_GENE2GO, 'r' ) as file :
		for line in file.readlines( ) :
			
			line = line.strip( )
			
			# Ignore Header Line
			if "#" == line[0] :
				continue
				
			splitLine = line.split( "\t" )
			sourceID = splitLine[1].strip( )
			goFullID = splitLine[2].strip( )
			goEvidence = splitLine[3].strip( )
			goShortID = goFullID[3:]
			
			# Get the existing ID or insert to establish a new one
			goEvidenceID = geneOntology.fetchEvidenceIDFromEvidenceSymbol( goEvidence )
			
			if sourceID in existingEntrezGeneIDs :
			
				currentGeneID = existingEntrezGeneIDs[sourceID]
					
				if "-" != goEvidence :
					insertCount = insertCount + 1
					
					cursor.execute( "SELECT gene_go_id FROM " + Config.DB_NAME + ".gene_go WHERE go_id=%s AND go_evidence_code_id=%s AND gene_id=%s LIMIT 1", [goShortID, goEvidenceID, currentGeneID] )
					row = cursor.fetchone( )
					
					if None == row :
						print "INSERTING GO"
						cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_go VALUES ( '0', %s, %s, 'active', NOW( ), %s )", [goShortID, goEvidenceID, currentGeneID] )
					else :
						print "UPDATING GO"
						cursor.execute( "UPDATE " + Config.DB_NAME + ".gene_go SET gene_go_status='active', gene_go_modified=NOW( ) WHERE gene_go_id=%s", [row[0]] )

											
			if 0 == (insertCount % Config.DB_COMMIT_COUNT ) :
				Database.db.commit( )
				
	Database.db.commit( )
	
	# Update the set of Possible Evidence Codes to Reflect the Currently Loaded Set
	cursor.execute( "UPDATE " + Config.DB_NAME + ".go_evidence_codes SET go_evidence_code_status='inactive'" )
	cursor.execute( "UPDATE " + Config.DB_NAME + ".go_evidence_codes SET go_evidence_code_status='active' WHERE go_evidence_code_id = ANY ( SELECT go_evidence_code_id FROM " + Config.DB_NAME + ".gene_go WHERE gene_go_status='active' GROUP BY go_evidence_code_id )" )
	Database.db.commit( )
				
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'EG_updateGO', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )
			