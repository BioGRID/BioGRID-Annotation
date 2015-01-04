
# Generate Statistics on Deactivated Genes when
# comparing to the IMS database.

import Config
import sys, string
import MySQLdb
import Database

from classes import Quick

with Database.db as cursor :

	quick = Quick.Quick( Database.db, cursor )
	proteinHash = quick.fetchValidRefseqIDHash( )
	
	cursor.execute( "SELECT refseq_protein_id, ptm_residue_location, ptm_residue, ptm_id, modification_id, geneID FROM " + Config.DB_IMS + ".ptms WHERE ptm_status='active'" )
	
	missingSEQs = set( )
	missingPTMs = set( )
	invalidPTMSites = set( )
	lengthProblemPTMSites = set( )
	validPTMSites = set( )
	recoveredPTMSites = set( )
	
	for (proteinID, residueLoc, residue, ptmID, modID, geneID) in cursor.fetchall( ) :
	
		# If protein ID is not in the database any more
		# check to see if an identical protein exists
		# that matches the old protein
		if str(proteinID) not in proteinHash :
		
			# CHECK HERE FOR ANY NEW SEQUENCES 
			# WITH THE EXACT SAME SPOT 
		
			missingSEQs.add(proteinID)
			missingPTMs.add(str(ptmID))
		else :
			# Check to see if PTM is still valid with the current sequence
			cursor.execute( "SELECT refseq_id, refseq_sequence, refseq_length FROM " + Config.DB_QUICK + ".quick_refseq WHERE refseq_id=%s LIMIT 1", [proteinID] )
			(refseqID, sequence, seqLength) = cursor.fetchone( )
			
			if residueLoc > seqLength :
				lengthProblemPTMSites.add( str(ptmID) )
			elif sequence[residueLoc-1].upper( ) != residue.upper( ) :
				
				cursor.execute( "SELECT refseq_protein_sequence, refseq_protein_length FROM " + Config.DB_OLDQUICK + ".quick_refseq_proteins WHERE refseq_protein_id=%s LIMIT 1", [refseqID] )
				(oldSeq, oldSeqLength) = cursor.fetchone( )
				
				startLoc = residueLoc-10
				if startLoc < 0 :
					startLoc = 0
				
				endLoc = residueLoc+10
				if endLoc > oldSeqLength :
					endLoc = oldSeqLength
					
				fragment = oldSeq[startLoc:endLoc]
				fragmentFront = oldSeq[startLoc:residueLoc]
				fragmentBack = oldSeq[residueLoc:endLoc]
				print "SEARCHING FOR: " + fragment.upper( )
				if fragment.upper( ) in sequence :
					print "RECOVERED BY FULL FRAGMENT COMPARE"
					recoveredPTMSites.add( str(ptmID) )
				elif fragmentFront.upper( ) in sequence :
					print "RECOVERED BY FRONT FRAGMENT COMPARE"
					recoveredPTMSites.add( str(ptmID) )
				elif fragmentBack.upper( ) in sequence :
					print "RECOVERED BY BACK FRAGMENT COMPARE"
					recoveredPTMSites.add( str(ptmID) )
				else :
					print "NO FRAGMENT MATCH FOUND"
					invalidPTMSites.add( str(ptmID) )
				
			else :
				validPTMSites.add( str(ptmID) )
				
			
	# for proteinID in missingSEQs :
		
		# cursor.execute( "SELECT refseq_protein_sequence FROM " + Config.DB_OLDQUICK + ".quick_refseq_proteins WHERE refseq_protein_id=%s LIMIT 1", [proteinID] )
		# row = cursor.fetchone( )
			
		# cursor.execute( "SELECT refseq_id FROM " + Config.DB_QUICK + ".quick_refseq WHERE refseq_sequence=%s AND (organism_id='9606' OR organism_id='559292')", [row[0]] )
			
		# if cursor.rowcount <= 0 :
			# print "Found No Match"
		# elif cursor.rowcount == 1 :
			# print "FOUND MATCH!!!!!"
			# row = cursor.fetchone( )
			# print row[0]
		# else :
			# print "FOUND MULTIPLE MATCHES!!!!!"
			# for row in cursor.fetchall( ) :
				# print row[0]	
		
		# else :
			
			# cursor.execute( "SELECT protein_sequence, protein_sequence_length FROM " + Config.DB_QUICK + ".quick_proteins WHERE protein_id=%s LIMIT 1", [row[0]] )
			# (seq, seqLength) = cursor.fetchone( )
			
			# if row[1] > seqLength :
				# deactivatedSeqPTMs.add( row[3] )
			# elif seq[row[1]-1].upper( ) != row[2].upper( ) :
				# deactivatedPTMs.add( row[3] )
				
				# if row[1] > seqLength :
					# print "SEQ IS TOO SHORT"
				# else :
					# print str(row[3])
					# print str(row[0])
					# print seq
					# print "Looking for: " + row[2].upper( ) + " at location: " + str(row[1])
					
					# if row[1]-2 < 0 :
						# print "Found: " + seq[row[1]-1] + " with " + seq[row[1]].upper( ) + " Right." 
					# elif row[1] >= seqLength :
						# print "Found: " + seq[row[1]-1] + " with " + seq[row[1]-2].upper( ) + " Left." 
					# else :
						# print "Found: " + seq[row[1]-1] + " with " + seq[row[1]-2].upper( ) + " Left and " + seq[row[1]].upper( ) + " Right." 
						
				# cursor.execute( "SELECT refseq_protein_sequence, refseq_protein_length FROM " + Config.DB_OLDQUICK + ".quick_refseq_proteins WHERE refseq_protein_id=%s", [row[0]] )
				# (oldSeq, oldSeqLength) = cursor.fetchone( )
				
				# startLoc = row[1]-10
				# if startLoc < 0 :
					# startLoc = 0
				
				# endLoc = row[1]+10
				# if endLoc > oldSeqLength :
					# endLoc = oldSeqLength
					
				# fragment = oldSeq[startLoc:endLoc]
				# fragmentFront = oldSeq[startLoc:row[1]]
				# fragmentBack = oldSeq[row[1]:endLoc]
				# print "SEARCHING FOR: " + fragment.upper( )
				# if fragment.upper( ) in seq :
					# print "RECOVERED BY FULL FRAGMENT COMPARE"
					# recoveredPTMs.add( row[3] )
				# elif fragmentFront.upper( ) in seq :
					# print "RECOVERED BY FRONT FRAGMENT COMPARE"
					# recoveredPTMs.add( row[3] )
				# elif fragmentBack.upper( ) in seq :
					# print "RECOVERED BY BACK FRAGMENT COMPARE"
					# recoveredPTMs.add( row[3] )
				# else :
					# print "NO FRAGMENT MATCH FOUND"
					
				# print "--------------------------------"
		
			
	print "Number of Missing Sequences: " + str( len(missingSEQs) )
	print "Number of Missing PTMs: " + str( len(missingPTMs) )
	print "Number of Length Problem PTMs: " + str( len(lengthProblemPTMSites) )
	print "Number of Invalid PTMs: " + str( len(invalidPTMSites) )
	print "Number of Remapped PTMs: " + str( len(recoveredPTMSites) )
	print "Number of Valid PTMs: " + str( len(validPTMSites) )
	
	print "----------------------------------"
	#print deactivatedSEQs
	
	print "----------------------------------"
	#print deactivatedPTMs
	
	
		

sys.exit( )