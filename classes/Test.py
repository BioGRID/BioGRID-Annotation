
# Tools for running the TEST labeled scripts

import MySQLdb
import sys, string
import Config

class Test( ) :

	def __init__( self, db, cursor ) :
		self.db = db
		self.cursor = cursor
		
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
			
				