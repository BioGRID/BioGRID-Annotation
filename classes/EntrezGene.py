
# Tools for managing the processing of genes
# from Entrez Gene

import MySQLdb
import sys, string
import Config

class EntrezGene( ) :

	def __init__( self, db, cursor ) :
		self.db = db
		self.cursor = cursor
		
	def fetchEnsemblHash( self ) :

		self.cursor.execute( "SELECT gene_external_value, gene_id FROM " + Config.DB_NAME + ".gene_externals WHERE gene_external_source='ENSEMBL'" )
		
		ensemblHash = { }
		for row in self.cursor.fetchall( ) :
			ensemblHash[str(row[0]).upper( )] = str(row[1])
			
		return ensemblHash
	
	def fetchLastUpdateDate( self ) :

		self.cursor.execute( "SELECT update_tracker_processed_date FROM " + Config.DB_STATS + ".update_tracker WHERE update_tracker_name='Entrez-Gene History' ORDER BY update_tracker_id DESC LIMIT 1" )

		row = self.cursor.fetchone( )
		if None == row :
			return False
		
		return row[0]

	def geneExists( self, geneID ) :

		self.cursor.execute( "SELECT gene_id FROM " + Config.DB_NAME + ".genes WHERE gene_source_id=%s AND gene_source='ENTREZ' LIMIT 1", [geneID] )

		row = self.cursor.fetchone( )
		if None == row :
			return False

		return row[0]

	def discontinueGene( self, geneID, oldID, newID, reason ) :

		self.cursor.execute( "UPDATE " + Config.DB_NAME + ".genes SET gene_status='inactive' WHERE gene_id=%s", [geneID] )
		self.cursor.execute( "INSERT INTO " + Config.DB_STATS + ".gene_history VALUES ( %s, %s, %s, %s, %s, %s, NOW( ) )", [0, "DISCONTINUED", geneID, oldID, newID, reason] )
					
		self.db.commit( )
		print ( "INSERT INTO " + Config.DB_STATS + ".gene_history VALUES ( %s, %s, %s, %s, %s, %s, NOW( ) )" % (0, "DISCONTINUED", geneID, oldID, newID, reason) )

	def updateGene( self, geneID, oldID, newID ) :

		self.cursor.execute( "UPDATE " + Config.DB_NAME + ".genes SET gene_status='active', gene_source_id=%s WHERE gene_id=%s", [newID, geneID] )
		self.cursor.execute( "INSERT INTO " + Config.DB_STATS + ".gene_history VALUES ( %s, %s, %s, %s, %s, %s, NOW( ) )", [0, "MODIFY_EG", geneID, oldID, newID, "Modified EG ID due to changes in Entrez-Gene Release"] )

		self.db.commit( )
		print ( "INSERT INTO " + Config.DB_STATS + ".gene_history VALUES ( %s, %s, %s, %s, %s, %s, NOW( ) )" % ("0", "MODIFY_EG", geneID, oldID, newID, "Modified EG ID due to changes in Entrez-Gene Release") )
		
	def findReplacementEntrezGeneID( self, entrezGeneID ) :
	
		self.cursor.execute( "SELECT gene_id FROM " + Config.DB_STAGING + ".entrez_gene_history WHERE discontinued_gene_id=%s LIMIT 1", [entrezGeneID] )
		row = self.cursor.fetchone( ) 
		
		if None == row :
			return entrezGeneID
			
		if -1 == row[0] :
			return row[0]
			
		return self.findReplacementEntrezGeneID( row[0] )

	def processGeneHistory( self, geneID, entrezGeneID ) :
	
		replacementID = self.findReplacementEntrezGeneID( entrezGeneID )
		
		if replacementID == entrezGeneID :
			# Do nothing, no replacement ID was found for this record
			return
		elif -1 == replacementID :
			# Deactivate this gene because it is discontinued and has no replacement
			self.discontinueGene( geneID, entrezGeneID, "-", "Discontinued because there is no mapping from this ID to a new ID in the current build" )
		else :
			newGeneID = self.geneExists( replacementID )
			
			if newGeneID :
				# Deactive this gene because its replacement already exists in our database
				self.discontinueGene( geneID, entrezGeneID, replacementID, "Discontinued due to existence of new gene as separate entry" )
			else :
				# otherwise, update record to new entrez gene id
				self.updateGene( geneID, entrezGeneID, replacementID )
				
	def fetchExistingEntrezGeneIDs( self ) :
		
		self.cursor.execute( "SELECT gene_id, gene_source_id FROM " + Config.DB_NAME + ".genes WHERE gene_status='active'" )
		
		idList = { }
		for row in self.cursor.fetchall( ) :
			idList[row[1]] = row[0]
			
		return idList
		
	def fetchEntrezGeneOrganismMapping( self ) :
	
		self.cursor.execute( "SELECT organism_id, organism_entrez_taxid FROM " + Config.DB_NAME + ".organisms WHERE organism_status='active'" )
		
		organismList = {}
		for row in self.cursor.fetchall( ) :
			(organismID, organismEntrezID) = row
			organismList[organismEntrezID] = organismID
			
		return organismList
				