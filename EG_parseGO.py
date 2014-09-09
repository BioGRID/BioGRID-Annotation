
# Parse go mappings from ENTREZ GENE for genes

import Config
import sys, string
import MySQLdb
import Database
import gzip

from classes import EntrezGene, GeneOntology

with Database.db as cursor :

	entrezGene = EntrezGene.EntrezGene( Database.db, cursor )
	geneOntology = GeneOntology.GeneOntology( Database.db, cursor )
	
	existingEntrezGeneIDs = entrezGene.fetchExistingEntrezGeneIDs( )
	
	cursor.execute( "TRUNCATE TABLE " + Config.DB_NAME + ".gene_go" )
	Database.db.commit( )
	
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
					cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_go VALUES ( '0', %s, %s, 'active', NOW( ), %s )", [goShortID, goEvidenceID, currentGeneID] )
											
			if 0 == (insertCount % Config.DB_COMMIT_COUNT ) :
				Database.db.commit( )
				
	Database.db.commit( )
	
	# Update the set of Possible Evidence Codes to Reflect the Currently Loaded Set
	cursor.execute( "UPDATE " + Config.DB_NAME + ".go_evidence_codes SET go_evidence_code_status='inactive'" )
	cursor.execute( "UPDATE " + Config.DB_NAME + ".go_evidence_codes SET go_evidence_code_status='active' WHERE go_evidence_code_id = ANY ( SELECT go_evidence_code_id FROM " + Config.DB_NAME + ".gene_go WHERE gene_go_status='active' GROUP BY go_evidence_code_id )" )
	Database.db.commit( )
				
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'EG_parseGO', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )
			