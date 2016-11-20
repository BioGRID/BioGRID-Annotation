
# Parse all the refseq mappings to Entrez Gene IDs
# into a mapping table by a single organism

import Config
import sys, string, argparse
import MySQLdb
import Database
import gzip

from classes import EntrezGene, Refseq

# Process Command Line Input
argParser = argparse.ArgumentParser( description = 'Update all Refseq to Gene mappings from Entrez Gene that are relevant to the organism id passed in via the command line.' )
argGroup = argParser.add_mutually_exclusive_group( required=True )
argGroup.add_argument( '-r', dest='refseqIDStart', type=int, nargs = 1, help = 'A refseq id to start working from', action='store' )
inputArgs = vars( argParser.parse_args( ) )

with Database.db as cursor :

	entrezGene = EntrezGene.EntrezGene( Database.db, cursor )
	refseq = Refseq.Refseq( Database.db, cursor )
	
	organismList = entrezGene.fetchEntrezGeneOrganismMapping( )
	refseqAccessions = { }
	organismID = 0
	missingRefseqs = set( )
	
	cursor.execute( "SELECT refseq_id, refseq_accession FROM " + Config.DB_NAME + ".refseq WHERE refseq_id > %s", [inputArgs['refseqIDStart'][0]] )
	for row in cursor.fetchall( ) :
		refseqAccessions[row[1]] = row[0]
		
	print refseqAccessions
	
	insertCount = 0
	with gzip.open( Config.EG_GENE2REFSEQ, 'r' ) as file :
		for line in file.readlines( ) :
			
			line = line.strip( )
			
			# Ignore Header Line
			if "#" == line[0] :
				continue
				
			splitLine = line.split( "\t" )
			entrezGeneTaxID = int(splitLine[0].strip( ))
			sourceID = splitLine[1].strip( )
			status = splitLine[2].strip( )
			rnaAccessionFull = splitLine[3].strip( )
			rnaGI = splitLine[4].strip( )
			proteinAccessionFull = splitLine[5].strip( )
			proteinGI = splitLine[6].strip( )
			
			if "-" != proteinAccessionFull :
				proteinAccessionSplit = proteinAccessionFull.split( "." )
				proteinAccession = proteinAccessionSplit[0]
				proteinVersion = proteinAccessionSplit[1]
				
				if proteinAccession in refseqAccessions :
					refseqID = refseqAccessions[proteinAccession]
			
					insertCount = insertCount + 1
					currentGeneID = entrezGene.geneExists( sourceID )
					
					if currentGeneID :

						cursor.execute( "SELECT gene_refseq_id FROM " + Config.DB_NAME + ".gene_refseqs WHERE refseq_id=%s AND gene_id=%s LIMIT 1", [refseqID, currentGeneID] )
						row = cursor.fetchone( )
						
						if None == row :
							print "INSERTING REFSEQ MAPPING"
							cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_refseqs VALUES( '0', %s, %s, 'active', NOW( ), %s )", [refseqID, status, currentGeneID] )
						else :
							print "UPDATING REFSEQ MAPPING"
							cursor.execute( "UPDATE " + Config.DB_NAME + ".gene_refseqs SET gene_refseq_status='active', gene_refseq_modified=NOW( ) WHERE gene_refseq_id=%s", [row[0]] )
						
						if "-" != rnaAccessionFull :
							
							rnaAccessionSplit = rnaAccessionFull.split( "." )
							rnaAccession = rnaAccessionSplit[0]
							rnaVersion = rnaAccessionSplit[1]
							
							cursor.execute( "SELECT refseq_identifier_id FROM " + Config.DB_NAME + ".refseq_identifiers WHERE refseq_id=%s AND refseq_identifier_value=%s LIMIT 1", [refseqID, rnaAccession] )
							row = cursor.fetchone( )
							
							if None == row :
								print "INSERTING REFSEQ RNA ACCESSION IDENTIFIER"
								cursor.execute( "INSERT INTO " + Config.DB_NAME + ".refseq_identifiers VALUES ( '0', %s, %s, %s, 'active', NOW( ), %s )", [rnaAccession, 'rna-accession', rnaVersion, refseqID] )
							else :
								print "UPDATING REFSEQ RNA ACCESSION IDENTIFIER"
								cursor.execute( "UPDATE " + Config.DB_NAME + ".refseq_identifiers SET refseq_identifier_status='active', refseq_identifier_version=%s, refseq_identifier_modified=NOW( ) WHERE refseq_identifier_id=%s", [rnaVersion, row[0]] )

						if "-" != rnaGI :
						
							cursor.execute( "SELECT refseq_identifier_id FROM " + Config.DB_NAME + ".refseq_identifiers WHERE refseq_id=%s AND refseq_identifier_value=%s LIMIT 1", [refseqID, rnaGI] )
							row = cursor.fetchone( )
							
							if None == row :
								print "INSERTING REFSEQ RNA GI IDENTIFIER"
								cursor.execute( "INSERT INTO " + Config.DB_NAME + ".refseq_identifiers VALUES ( '0', %s, %s, '0', 'active', NOW( ), %s )", [rnaGI, 'rna-gi', refseqID] )

							else :
								print "UPDATING REFSEQ RNA GI IDENTIFIER"
								cursor.execute( "UPDATE " + Config.DB_NAME + ".refseq_identifiers SET refseq_identifier_status='active', refseq_identifier_version='0', refseq_identifier_modified=NOW( ) WHERE refseq_identifier_id=%s", [row[0]] )
			
			if 0 == (insertCount % Config.DB_COMMIT_COUNT ) :
				Database.db.commit( )
	
	Database.db.commit( )
	
sys.exit( )
			