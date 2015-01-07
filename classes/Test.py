
# Tools for running the TEST labeled scripts

import MySQLdb
import sys, string
import Config

class Test( ) :

	def __init__( self, db, cursor ) :
		self.db = db
		self.cursor = cursor
		self.fragmentLength = 10
		
	def findReplacementCandidateGenes( self, geneID, organismID ) :
		
		self.cursor.execute( "SELECT quick_identifier_value FROM " + Config.DB_OLDQUICK + ".quick_identifiers WHERE gene_id=%s AND quick_identifier_type IN ('SYNONYM','ALIAS','ORDERED LOCUS','SYSTEMATIC NAME','OFFICIAL SYMBOL','ENTREZ_GENE_ETG')", [geneID] )
		
		replacementCandidates = set( )
		for idRow in self.cursor.fetchall( ) :
			
			self.cursor.execute( "SELECT gene_id FROM " + Config.DB_QUICK + ".quick_identifiers WHERE quick_identifier_value=%s AND organism_id=%s GROUP BY gene_id", [idRow[0],organismID] )
			
			for geneRow in self.cursor.fetchall( ) :
				replacementCandidates.add(str(geneRow[0]))
				
		return replacementCandidates
		
	def fetchInteractionCount( self, geneID ) :
	
		self.cursor.execute( "SELECT count(*) FROM " + Config.DB_IMS + ".interaction_matrix WHERE modification_type='ACTIVATED' AND (interactor_A_id=%s OR interactor_B_id=%s)", [geneID,geneID] )
		
		row = self.cursor.fetchone( )
		return row[0]
		
	def fetchEntrezGeneID( self, geneID ) :
		
		self.cursor.execute( "SELECT quick_identifier_value FROM " + Config.DB_OLDQUICK + ".quick_identifiers WHERE gene_id=%s AND quick_identifier_type = 'ENTREZ_GENE' LIMIT 1", [geneID] )
		
		row = self.cursor.fetchone( )
		if None == row :
			return "-"
			
		return row[0]
		
	def testPTMFragment( self, residueLoc, oldSeq, newSeq, newSeqID ) :
	
		ptmDetails = []
	
		# CREATE FRAGMENT BOUNDARIES
		startLoc = (residueLoc-1)-self.fragmentLength
		if startLoc < 0 :
			startLoc = 0
			
		endLoc = residueLoc+self.fragmentLength
		if endLoc > len(oldSeq) :
			endLoc = len(oldSeq)
		
		# CREATE FRAGMENTS
		fragment = oldSeq[startLoc:endLoc]
		fragmentFront = oldSeq[startLoc:residueLoc]
		fragmentBack = oldSeq[residueLoc-1:endLoc]
		
		if fragment.upper( ) in newSeq and len(fragmentFront) >= self.fragmentLength and len(fragmentBack) >= self.fragmentLength :
			ptmSiteLoc = newSeq.index( fragment.upper( ) ) + self.fragmentLength
			ptmDetails.append( str(newSeqID) )
			ptmDetails.append( str(ptmSiteLoc+1) )
			ptmDetails.append( newSeq[ptmSiteLoc] )
			ptmDetails.append( "FULL FRAGMENT RECOVERY" )
		elif fragmentFront.upper( ) in newSeq and len(fragmentFront) >= self.fragmentLength :
			ptmSiteLoc = newSeq.index( fragmentFront.upper( ) ) + self.fragmentLength
			ptmDetails.append( str(newSeqID) )
			ptmDetails.append( str(ptmSiteLoc+1) )
			ptmDetails.append( newSeq[ptmSiteLoc] )
			ptmDetails.append( "HEAD FRAGMENT RECOVERY" )
		elif fragmentBack.upper( ) in newSeq and len(fragmentBack) >= self.fragmentLength :
			ptmSiteLoc = newSeq.index( fragmentBack.upper( ) )
			ptmDetails.append( str(newSeqID) )
			ptmDetails.append( str(ptmSiteLoc+1) )
			ptmDetails.append( newSeq[ptmSiteLoc] )
			ptmDetails.append( "TAIL FRAGMENT RECOVERY" )
		else :
			ptmDetails.append( "dead" )
			ptmDetails.append( "dead" )
			ptmDetails.append( "dead" )
			ptmDetails.append( "NO FRAGMENT MATCH" )
			
		return ptmDetails
		
	def isPTMValid( self, residueLoc, residue, sequence ) :
			
		if residueLoc > len(sequence) :
			return False
		elif sequence[residueLoc-1].upper( ) != residue.upper( ) :
			return False
			
		return True
		
	def processPTMByFragment( self, ptmID, newSeqID ) :
	
		ptmDetails = []
		ptmDetails.append( str(ptmID) )
	
		# GRAB PTM DETAILS
		self.cursor.execute( "SELECT refseq_protein_id, ptm_residue_location, ptm_residue, ptm_id, modification_id, gene_id FROM " + Config.DB_IMS + ".ptms WHERE ptm_id=%s LIMIT 1", [ptmID] )
		(proteinID, residueLoc, residue, ptmID, modID, geneID) = self.cursor.fetchone( )
		
		ptmDetails.append( str(proteinID) )
		ptmDetails.append( str(residueLoc) )
		ptmDetails.append( str(residue) )
		
		# GRAB OLD SEQUENCE
		(oldRefID, oldSeq, oldSeqLength, oldGeneID) = self.fetchOldSequenceDetails( proteinID )
		
		# GRAB NEW SEQUENCE
		(newRefID, newSeq, newSeqLength, newGeneID) = self.fetchNewSequenceDetails( newSeqID )

		fragmentDetails = self.testPTMFragment( residueLoc, oldSeq, newSeq, newSeqID )
		
		ptmDetails.extend( fragmentDetails )
		
		return ptmDetails
		
	def fetchOldSequenceDetails( self, oldSeqID ) :
		self.cursor.execute( "SELECT refseq_protein_id, refseq_protein_sequence, refseq_protein_length, gene_id FROM " + Config.DB_OLDQUICK + ".quick_refseq_proteins WHERE refseq_protein_id=%s LIMIT 1", [oldSeqID] )
		return self.cursor.fetchone( )
		
	def fetchNewSequenceDetails( self, newSeqID ) :
		self.cursor.execute( "SELECT refseq_id, refseq_sequence, refseq_length, gene_id FROM " + Config.DB_QUICK + ".quick_refseq WHERE refseq_id=%s LIMIT 1", [newSeqID] )
		return self.cursor.fetchone( )
		
	def fetchNewSequenceDetailsByGene( self, geneID ) :
		self.cursor.execute( "SELECT refseq_id, refseq_sequence, refseq_length, gene_id FROM " + Config.DB_QUICK + ".quick_refseq WHERE gene_id=%s", [geneID] )
		
		sequenceDetails = []
		for row in self.cursor.fetchall( ) :
			sequenceDetails.append( row )
		
		return sequenceDetails
		
	def fetchNewSequenceDetailsByGeneAndSequence( self, geneID, sequence ) :
		self.cursor.execute( "SELECT refseq_id, refseq_sequence, refseq_length, gene_id FROM " + Config.DB_QUICK + ".quick_refseq WHERE gene_id=%s AND refseq_sequence=%s", [geneID, sequence] )
		
		sequenceDetails = []
		for row in self.cursor.fetchall( ) :
			sequenceDetails.append( row )
		
		return sequenceDetails

	def processPTMByExactMatch( self, ptmID, newSeqID ) :
		
		ptmDetails = []
		ptmDetails.append( str(ptmID) )
	
		# GRAB PTM DETAILS
		self.cursor.execute( "SELECT refseq_protein_id, ptm_residue_location, ptm_residue, ptm_id, modification_id, gene_id FROM " + Config.DB_IMS + ".ptms WHERE ptm_id=%s LIMIT 1", [ptmID] )
		(proteinID, residueLoc, residue, ptmID, modID, geneID) = self.cursor.fetchone( )
		
		ptmDetails.append( str(proteinID) )
		ptmDetails.append( str(residueLoc) )
		ptmDetails.append( str(residue) )
		
		# GRAB NEW SEQUENCE
		(newRefID, newSeq, newSeqLength, newGeneID) = self.fetchNewSequenceDetails( newSeqID )

		if self.isPTMValid( residueLoc, residue, newSeq ) :
			ptmDetails.extend( [str(newRefID), str(residueLoc), str(newSeq[residueLoc-1]), "EXACT SEQUENCE RECOVERY"] )
		else :
			ptmDetails.extend( ["dead", "dead", "dead", "INVALID PTM ON NEW SEQUENCE"] )
		
		return ptmDetails
		
	def processPTMs( self, oldSeqID, newSeqID, useExact = True, returnOnlyDead = False ) :
		
		ptmSet = []
		self.cursor.execute( "SELECT refseq_protein_id, ptm_residue_location, ptm_residue, ptm_id, modification_id, gene_id FROM " + Config.DB_IMS + ".ptms WHERE ptm_status='active' AND refseq_protein_id=%s", [oldSeqID] )
		for (proteinID, residueLoc, residue, ptmID, modID, geneID) in self.cursor.fetchall( ) :
			
			if not returnOnlyDead :
			
				if useExact :
					ptmDetails = self.processPTMByExactMatch( ptmID, newSeqID )
					ptmSet.append( ptmDetails )
				else :
					ptmDetails = self.processPTMByFragment( ptmID, newSeqID )
					ptmSet.append( ptmDetails )
					
			else :
			
				ptmSet.append( [str(ptmID), str(proteinID), str(residueLoc), str(residue), "dead", "dead", "dead", "INVALID PTM ON NEW SEQUENCE"] )
				
		return ptmSet