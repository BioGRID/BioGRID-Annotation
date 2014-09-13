
# Parse all the refseq mappings to Entrez Gene IDs
# into a mapping table

import Config
import sys, string
import MySQLdb
import Database
import gzip

from classes import EntrezGene, Refseq

with Database.db as cursor :

	entrezGene = EntrezGene.EntrezGene( Database.db, cursor )
	refseq = Refseq.Refseq( Database.db, cursor )
	
	existingEntrezGeneIDs = entrezGene.fetchExistingEntrezGeneIDs( )
	refseqMap = refseq.buildRefseqMappingHash( )
	organismList = entrezGene.fetchEntrezGeneOrganismMapping( )
	
	cursor.execute( "TRUNCATE TABLE " + Config.DB_NAME + ".gene_refseqs" )
	Database.db.commit( )
	
	missingRefseqs = set( )
	completedMappings = set( )
	
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
						
						# Test to see if this pairing is already
						# added so we don't add the same pairing
						# multiple times.
						idPair = str(currentGeneID) + "|" + str(refseqID)
						
						if idPair not in completedMappings :
							insertCount = insertCount + 1
							completedMappings.add( idPair )
							
							cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_refseqs VALUES( '0', %s, %s, 'active', NOW( ), %s )", [refseqID, status, currentGeneID] )

							if "-" != rnaAccessionFull :
							
								rnaAccessionSplit = rnaAccessionFull.split( "." )
								rnaAccession = rnaAccessionSplit[0]
								rnaVersion = rnaAccessionSplit[1]
							
								cursor.execute( "INSERT INTO " + Config.DB_NAME + ".refseq_identifiers VALUES ( '0', %s, %s, %s, 'active', NOW( ), %s )", [rnaAccession, 'rna-accession', rnaVersion, refseqID] )

							if "-" != rnaGI :
								cursor.execute( "INSERT INTO " + Config.DB_NAME + ".refseq_identifiers VALUES ( '0', %s, %s, '0', 'active', NOW( ), %s )", [rnaGI, 'rna-gi', refseqID] )
					
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
		
		if "NP" == refseqSplit[0][:2] and int(refseqSplit[2]) in organismList :
			cursor.execute( "INSERT INTO " + Config.DB_NAME + ".refseq VALUES( '0', %s, '0', '', '0', '', '1', %s, NOW( ), 'active' )", [refseqSplit[0], organismList[int(refseqSplit[2])]] )
			refseqID = cursor.lastrowid
			cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_refseqs VALUES( '0', %s, %s, 'active', NOW( ), %s )", [refseqID, refseqSplit[3], refseqSplit[1]] )
		else :
			cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_externals VALUES( '0', %s, 'REFSEQ_LEGACY', 'active', NOW( ), %s )", [refseqSplit[0], refseqSplit[1]] )
		
	Database.db.commit( )
				
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'EG_parseExternals', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )
			