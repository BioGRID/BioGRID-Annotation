
# Tools for managing the processing of refseq proteins

import MySQLdb
import sys, string
import Config

class Refseq( ) :

	def __init__( self, db, cursor ) :
		self.db = db
		self.cursor = cursor

	def buildAccessionMappingHash( self ) :
		
		self.cursor.execute( "SELECT refseq_id, refseq_accession FROM " + Config.DB_NAME + ".refseq" )
		
		mappingHash = {}
		for row in self.cursor.fetchall( ) :
			mappingHash[str(row[1])] = str(row[0])
			
		return mappingHash
		
	def buildOrganismMappingHash( self ) :
	
		self.cursor.execute( "SELECT refseq_protein_uid, refseq_protein_organism_id FROM " + Config.DB_STAGING + ".refseq_protein_ids" )
		
		mappingHash = {}
		for row in self.cursor.fetchall( ) :
			mappingHash[str(row[0])] = str(row[1])
			
		return mappingHash