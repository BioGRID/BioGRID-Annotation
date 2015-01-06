
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
	
	for (proteinID, residueLoc, residue, ptmID, modID, geneID) in cursor.fetchall( ) :
		
		# If protein ID is not in the database any more
		# check to see if an identical protein exists
		# that matches the old protein
		if str(proteinID) not in proteinHash :
			missingSEQs.add( proteinID )
		else :
			# Check to see if PTM is still valid with the current sequence
			cursor.execute( "SELECT refseq_id, refseq_sequence, refseq_length FROM " + Config.DB_QUICK + ".quick_refseq WHERE refseq_id=%s LIMIT 1", [proteinID] )
			(refseqID, sequence, seqLength) = cursor.fetchone( )
			
			if not test.isPTMValid( residueLoc, residue, sequence ) :
				problemPTMs.add( str(ptmID) )
	
	# TRY AND RECOVER PROBLEMATIC PTMS
	for ptmID in problemPTMs :
		ptmDetails = test.processPTM( ptmID )
		#print "\t".join(ptmDetails)
		
	for proteinID in missingSEQs :
	
		# If protein ID is not in the database any more
		# check to see if an identical protein exists
		# that matches the old protein for the same gene
		
		cursor.execute( "SELECT refseq_id, refseq_protein_sequence, refseq_protein_length, gene_id FROM " + Config.DB_OLDQUICK + ".quick_refseq_proteins WHERE refseq_protein_id=%s LIMIT 1", [proteinID] )
		(oldRefID, oldSeq, oldSeqLength, geneID) = cursor.fetchone( )
		
		cursor.execute( "SELECT refseq_id, refseq_sequence, refseq_length FROM " + Config.DB_QUICK + ".quick_refseq WHERE gene_id=%s AND refseq_sequence=%s", [geneID, oldSeq] )
		if cursor.rowcount == 1 :
			row = cursor.fetchone( )
			
			print "FOUND ONE MATCH ONLY FOR " + str(proteinID)
		elif cursor.rowcount > 1 :
			print "FOUND MULTIPLE (" + str(cursor.rowcount) + ") MATCHES FOR " + str(proteinID)
		else :
			print "FOUND NO EXACT MATCH FOR " + str(proteinID)

sys.exit( )