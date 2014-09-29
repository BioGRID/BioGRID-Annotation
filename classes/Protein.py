
# Tools for managing the processing of proteins

import MySQLdb
import sys, string
import Config

class Protein( ) :

	def __init__( self, db, cursor ) :
		self.db = db
		self.cursor = cursor
		
	def proteinExists( self, proteinID, source ) :
		
		self.cursor.execute( "SELECT protein_id FROM " + Config.DB_NAME + ".proteins WHERE protein_reference_id=%s AND protein_source=%s LIMIT 1", [proteinID, source] )
		
		row = self.cursor.fetchone( )
		if None != row :
			return str(row[0])
			
		return False
		
	def fetchMappingsByUniprotID( self, uniprotID ) :
		
		self.cursor.execute( "SELECT refseq_id FROM " + Config.DB_NAME + ".protein_mapping WHERE uniprot_id=%s AND protein_mapping_status='active'", [uniprotID] )
		
		refseqSet = set( )
		for row in self.cursor.fetchall( ) :
			refseqSet.add( str(row[0]) )
			
		return refseqSet
		
	def fetchMappingsByRefseqID( self, refseqID ) :
		
		self.cursor.execute( "SELECT uniprot_id FROM " + Config.DB_NAME + ".protein_mapping WHERE refseq_id=%s AND protein_mapping_status='active'", [refseqID] )
		
		uniprotSet = set( )
		for row in self.cursor.fetchall( ) :
			uniprotSet.add( str(row[0]) )
			
		return uniprotSet