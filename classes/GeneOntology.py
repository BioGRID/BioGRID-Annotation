
# Tools for managing the processing of gene ontology terms

import MySQLdb
import sys, string
import Config

class GeneOntology( ) :

	def __init__( self, db, cursor ) :
		self.db = db
		self.cursor = cursor
		self.ignoreTerms = [8150,3674,5575] # biological_process, molecular_function, cellular_component
		self.mappingHash = self.buildSubsetMappingHash( )
		self.parentHash = self.buildParentMappingHash( )
		self.evidenceHash = self.buildEvidenceHash( )
		
	def getMappingHash( self ) :
		return self.mappingHash
		
	def findSubsetParents( self, goID, subsetID ) :
		
		subsetParents = []
		if goID in self.mappingHash[subsetID] and not goID in self.ignoreTerms :
			subsetParents.append( goID )
			return subsetParents
		else :
			if goID in self.parentHash :
				parents = self.parentHash[goID]
				for parent in parents :
					subsetParents = subsetParents + self.findSubsetParents( parent, subsetID )
					
		return subsetParents
				
	def buildSubsetMappingHash( self ) :
		
		self.cursor.execute( "SELECT go_id, go_subset_id FROM " + Config.DB_NAME + ".go_subset_mappings WHERE go_subset_mapping_status='active'" )
		
		mappingHash = {}
		for row in self.cursor.fetchall( ) :
			if not row[1] in mappingHash :
				mappingHash[row[1]] = []
			
			mappingHash[row[1]].append( row[0] )
			
		return mappingHash
		
	def buildParentMappingHash( self ) :
		
		self.cursor.execute( "SELECT go_child_id, go_parent_id FROM " + Config.DB_NAME + ".go_relationships WHERE go_relationship_status='active'" )
		
		mappingHash = {}
		for row in self.cursor.fetchall( ) :
			if not row[0] in mappingHash :
				mappingHash[row[0]] = []
			
			mappingHash[row[0]].append( row[1] )
			
		return mappingHash
		
	def buildEvidenceHash( self ) :
		
		self.cursor.execute( "SELECT go_evidence_code_id, go_evidence_code_symbol FROM " + Config.DB_NAME + ".go_evidence_codes" )
		
		mappingHash = {}
		for row in self.cursor.fetchall( ) :
			if not row[1] in mappingHash :
				mappingHash[row[1].upper( )] = row[0]
			
		return mappingHash
		
	def fetchEvidenceIDFromEvidenceSymbol( self, symbol ) :

		symbol = symbol.strip( ).upper( )
	
		if symbol not in self.evidenceHash :

			self.cursor.execute( "INSERT INTO " + Config.DB_NAME + ".go_evidence_codes VALUES ( '0',%s,'',NOW( ),'active' )", [symbol] )
			self.db.commit( )
			
			self.evidenceHash[symbol] = self.cursor.lastrowid
		
		return self.evidenceHash[symbol]
				