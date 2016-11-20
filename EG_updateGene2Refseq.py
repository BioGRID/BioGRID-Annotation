
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
	refseq = Refseq.Refseq( Database.db, cursor )
	
	refseqMap = refseq.buildRefseqMappingHash( )
	organismList = entrezGene.fetchEntrezGeneOrganismMapping( )
	existingEntrezGeneIDs = { }
	organismID = 0
	missingRefseqs = set( )
	
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
		cursor.execute( "UPDATE " + Config.DB_NAME + ".gene_refseqs SET gene_refseq_status='inactive' WHERE gene_id=%s", [geneID] )
		
	Database.db.commit( )
	
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
			
			if sourceID in existingEntrezGeneIDs :
			
				insertCount = insertCount + 1
				currentGeneID = existingEntrezGeneIDs[sourceID]

				if "-" != proteinAccessionFull :
					proteinAccessionSplit = proteinAccessionFull.split( "." )
					proteinAccession = proteinAccessionSplit[0]
					proteinVersion = proteinAccessionSplit[1]
					
					if proteinAccession in refseqMap :
						refseqID = refseqMap[proteinAccession]
						
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

					else :
						missingRefseqs.add( str(proteinAccession) + "|" + str(currentGeneID) + "|" + str(entrezGeneTaxID) + "|" + status )
			
			if 0 == (insertCount % Config.DB_COMMIT_COUNT ) :
				Database.db.commit( )
	
	Database.db.commit( )
	
	# All ids not in our active set of proteins
	# are probably old mapped ids that are now
	# discontinued, disabled, etc.
	# Load these as external identifiers for the genes
	# simply for legacy purposes.
	# Any NP_ names we come across, load those into the sequence table
	# so we can load them later
	
	print len( missingRefseqs )
	for missingRefseq in missingRefseqs :
		refseqSplit = missingRefseq.split( "|" )
		
		#if "NP" == refseqSplit[0][:2] and int(refseqSplit[2]) in organismList :
		if int(refseqSplit[2]) in organismList :
		
			cursor.execute( "SELECT refseq_id FROM " + Config.DB_NAME + ".refseq WHERE refseq_accession=%s LIMIT 1", [refseqSplit[0]] )
			row = cursor.fetchone( )
			
			refseqID = ""
			if None == row :
				print "ADDING REFSEQ"
				cursor.execute( "INSERT INTO " + Config.DB_NAME + ".refseq VALUES( '0', %s, '0', '', '0', '', '1', %s, NOW( ), 'active' )", [refseqSplit[0], organismList[int(refseqSplit[2])]] )
				refseqID = cursor.lastrowid
			else :
				print "UPDATING REFSEQ"
				cursor.execute( "UPDATE " + Config.DB_NAME + ".refseq SET organism_id=%s, refseq_status='active' WHERE refseq_id=%s", [organismList[int(refseqSplit[2])], str(row[0])] )
				refseqID = str(row[0])
				
			cursor.execute( "SELECT gene_refseq_id FROM " + Config.DB_NAME + ".gene_refseqs WHERE refseq_id=%s AND gene_id=%s LIMIT 1", [refseqID, refseqSplit[1]] )
			row = cursor.fetchone( )
				
			if None == row :
				print "INSERTING REFSEQ MAPPING"
				cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_refseqs VALUES( '0', %s, %s, 'active', NOW( ), %s )", [refseqID, refseqSplit[3], refseqSplit[1]] )
			else :
				print "UPDATING REFSEQ MAPPING"
				cursor.execute( "UPDATE " + Config.DB_NAME + ".gene_refseqs SET gene_refseq_status='active', gene_refseq_modified=NOW( ) WHERE gene_refseq_id=%s", [row[0]] )
				
		else :
		
			cursor.execute( "SELECT gene_external_id FROM " + Config.DB_NAME + ".gene_externals WHERE gene_external_value=%s AND gene_external_source='REFSEQ_LEGACY' AND gene_id=%s LIMIT 1", [refseqSplit[0], refseqSplit[1]] )
			row = cursor.fetchone( )
		
			if None == row :
				print "INSERTING GENE EXTERNAL MAPPING"
				cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_externals VALUES( '0', %s, 'REFSEQ-LEGACY', 'active', NOW( ), %s )", [refseqSplit[0], refseqSplit[1]] )
			else :
				print "UPDATING GENE EXTERNAL MAPPING"
				cursor.execute( "UPDATE " + Config.DB_NAME + ".gene_externals SET gene_external_status='active', gene_external_modified=NOW( ) WHERE gene_external_id=%s", [row[0]] )
		
	Database.db.commit( )
				
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'EG_updateGene2Refseq', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )
			