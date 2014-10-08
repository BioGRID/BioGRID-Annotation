
# Generate Statistics on Deactivated Genes when
# comparing to the IMS database.

import Config
import sys, string
import MySQLdb
import Database

from classes import Quick

with Database.db as cursor :

	quick = Quick.Quick( Database.db, cursor )
	proteinHash = quick.fetchValidProteinIDHash( )
	
	cursor.execute( "SELECT refseq_protein_id, ptm_residue_location, ptm_residue, ptm_id FROM " + Config.DB_IMS + ".ptms WHERE ptm_status='active'" )
	
	deactivatedSEQs = set( )
	deactivatedPTMs = set( )
	deactivatedSeqPTMs = set( )
	recoveredPTMs = set( )
	
	for row in cursor.fetchall( ) :
	
		if str(row[0]) not in proteinHash :
			deactivatedSEQs.add( row[0] )
			deactivatedPTMs.add( row[3] )
		else :
			
			cursor.execute( "SELECT protein_sequence, protein_sequence_length FROM " + Config.DB_QUICK + ".quick_proteins WHERE protein_id=%s LIMIT 1", [row[0]] )
			(seq, seqLength) = cursor.fetchone( )
			
			if row[1] > seqLength :
				deactivatedSeqPTMs.add( row[3] )
			elif seq[row[1]-1].upper( ) != row[2].upper( ) :
				deactivatedPTMs.add( row[3] )
				
				if row[1] > seqLength :
					print "SEQ IS TOO SHORT"
				else :
					print str(row[3])
					print str(row[0])
					print seq
					print "Looking for: " + row[2].upper( ) + " at location: " + str(row[1])
					
					if row[1]-2 < 0 :
						print "Found: " + seq[row[1]-1] + " with " + seq[row[1]].upper( ) + " Right." 
					elif row[1] >= seqLength :
						print "Found: " + seq[row[1]-1] + " with " + seq[row[1]-2].upper( ) + " Left." 
					else :
						print "Found: " + seq[row[1]-1] + " with " + seq[row[1]-2].upper( ) + " Left and " + seq[row[1]].upper( ) + " Right." 
						
				cursor.execute( "SELECT refseq_protein_sequence, refseq_protein_length FROM " + Config.DB_OLDQUICK + ".quick_refseq_proteins WHERE refseq_protein_id=%s", [row[0]] )
				(oldSeq, oldSeqLength) = cursor.fetchone( )
				
				startLoc = row[1]-10
				if startLoc < 0 :
					startLoc = 0
				
				endLoc = row[1]+10
				if endLoc > oldSeqLength :
					endLoc = oldSeqLength
					
				fragment = oldSeq[startLoc:endLoc]
				fragmentFront = oldSeq[startLoc:row[1]]
				fragmentBack = oldSeq[row[1]:endLoc]
				print "SEARCHING FOR: " + fragment.upper( )
				if fragment.upper( ) in seq :
					print "RECOVERED BY FULL FRAGMENT COMPARE"
					recoveredPTMs.add( row[3] )
				elif fragmentFront.upper( ) in seq :
					print "RECOVERED BY FRONT FRAGMENT COMPARE"
					recoveredPTMs.add( row[3] )
				elif fragmentBack.upper( ) in seq :
					print "RECOVERED BY BACK FRAGMENT COMPARE"
					recoveredPTMs.add( row[3] )
				else :
					print "NO FRAGMENT MATCH FOUND"
					
				print "--------------------------------"
		
			
	print "Number of Deactivated Sequences: " + str( len(deactivatedSEQs) )
	print "Number of Deactivated PTMs: " + str( len(deactivatedPTMs) )
	print "Number of Deactivated PTMs by Deactivated Sequence: " + str( len(deactivatedSeqPTMs) )
	print "Number of Recovered PTMs: " + str( len(recoveredPTMs) )
	
	print "----------------------------------"
	#print deactivatedSEQs
	
	print "----------------------------------"
	#print deactivatedPTMs
	
	
		

sys.exit( )