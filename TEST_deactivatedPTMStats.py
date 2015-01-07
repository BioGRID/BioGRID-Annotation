
# Generate Statistics on Deactivated Genes when
# comparing to the IMS database.

import Config
import sys, string
import MySQLdb
import Database

from classes import Quick, Test

with Database.db as cursor :

	quick = Quick.Quick( Database.db, cursor )
	test = Test.Test( Database.db, cursor )
	proteinHash = quick.fetchValidRefseqIDHash( )
	
	cursor.execute( "SELECT refseq_protein_id, ptm_residue_location, ptm_residue, ptm_id, modification_id, gene_id FROM " + Config.DB_IMS + ".ptms WHERE ptm_status='active'" )
	
	missingSEQs = set( )
	problemPTMs = set( )
	validPTMs = set( )
	
	for (proteinID, residueLoc, residue, ptmID, modID, geneID) in cursor.fetchall( ) :
		
		# If protein ID is not in the database any more
		# check to see if an identical protein exists
		# that matches the old protein
		if str(proteinID) not in proteinHash :
			missingSEQs.add( str(proteinID) )
			problemPTMs.add( str(ptmID) )
		else :
		
			# Check to see if PTM is still valid with the current sequence
			cursor.execute( "SELECT refseq_id, refseq_sequence, refseq_length FROM " + Config.DB_QUICK + ".quick_refseq WHERE refseq_id=%s LIMIT 1", [proteinID] )
			(refseqID, sequence, seqLength) = cursor.fetchone( )
			
			if not test.isPTMValid( residueLoc, residue, sequence ) :
				ptmDetails = test.processPTMByFragment( ptmID, refseqID )
				problemPTMs.add( str(ptmID) )
				print "\t".join(ptmDetails)
			else :
				validPTMs.add( str(ptmID) )
		
	for proteinID in missingSEQs :
	
		# If protein ID is not in the database any more
		# check to see if an identical protein exists
		# that matches the old protein for the same gene
		
		# See if there are additional sequences matching the
		# old protein for the same gene.
		
		ptmSet = []
		
		(oldRefID, oldSeq, oldSeqLength, geneID) = test.fetchOldSequenceDetails( proteinID )
		potentialNewSequences = test.fetchNewSequenceDetailsByGeneAndSequence( geneID, oldSeq )
		
		if len(potentialNewSequences) == 1 :
			# Found only one EXACT matching sequence for this protein
			# So test that PTM sites are still valid and output details for swapping
			# the protein ID
			(newRefID, newSeq, newSeqLength, newGeneID) = potentialNewSequences[0]
			ptmSet = test.processPTMs( oldRefID, newRefID, True )
		elif len(potentialNewSequences) > 1 :
			# Found multiple EXACT matching sequences for this protein
			# So output all the matching protein IDs so one can be selected
			# later manually
			
			(newRefID, newSeq, newSeqLength, newGeneID) = potentialNewSequences[0]
			ptmSet = test.processPTMs( oldRefID, newRefID, True )
			
			sequenceIDs = set( )
			for (newRefID, newSeq, newSeqLength, newGeneID) in potentialNewSequences :
				sequenceIDs.add( str(newRefID) )
			
			for ptmDetails in ptmSet :
				ptmDetails[4] = "|".join(sequenceIDs)
				ptmDetails[7] = "MULTI EXACT SEQUENCE RECOVERY"
			
		else :
			# Found zero EXACT matching sequences for this protein
			# So instead, grab all proteins for this gene, if any exist
			# and use fragment matching to see if we can find the same 
			# PTM site in one of the candidates.
			potentialNewSequences = test.fetchNewSequenceDetailsByGene( geneID )
			
			if len(potentialNewSequences) == 1 :
				# Only one potential matching new sequence
				(newRefID, newSeq, newSeqLength, newGeneID) = potentialNewSequences[0]
				ptmSet = test.processPTMs( oldRefID, newRefID, False, False )
			elif len(potentialNewSequences) > 1 :
				# Multiple matching potential new sequences
				# but each one would need to be validated as a potential option
				
				
				finalPTMs = { }
				for (newRefID, newSeq, newSeqLength, newGeneID) in potentialNewSequences :
					ptmSet = test.processPTMs( oldRefID, newRefID, False, False )
					
					for ptmDetails in ptmSet :
						ptmID = ptmDetails[0]
						if ptmID not in finalPTMs :
							finalPTMs[ptmID] = []
						finalPTMs[ptmID].append( ptmDetails )
				
				ptmSet = []
				for (ptmID,ptmList) in finalPTMs.items( ) :
					ptmEntry = []
					ptmInfo = ptmList[0]
					ptmEntry.extend( [ptmInfo[0], ptmInfo[1], ptmInfo[2], ptmInfo[3]] )
					ptmSeqs = []
					ptmLocs = []
					ptmResidues = []
					for ptmDetails in ptmList :
						if ptmDetails[4] != "dead" :
							ptmSeqs.append( ptmDetails[4] )
							ptmLocs.append( ptmDetails[5] )
							ptmResidues.append( ptmDetails[6] )
					
					if len(ptmSeqs) > 0 :
						ptmEntry.extend( ["|".join(ptmSeqs), "|".join(ptmLocs), "|".join(ptmResidues), "MULTI FRAGMENT SEQUENCE RECOVERY"] )
					else :
						ptmEntry.extend( ["dead","dead","dead", "INVALID PTM ON NEW SEQUENCE"] )
						
					
					ptmSet.append( ptmEntry )
				
			else :
				# No sequences for this gene, these PTMs are dead
				ptmSet = test.processPTMs( oldRefID, "", False, True )
			
		for ptmDetails in ptmSet :
			print "\t".join(ptmDetails)
				
				
print "TOTAL NUMBER OF PROBLEM PTMS: " + str(len(problemPTMs))
print "TOTAL NUMBER OF MISSING SEQS: " + str(len(missingSEQs))
print "TOTAL NUMBER OF VALID PTMS  : " + str(len(validPTMs))

sys.exit( )