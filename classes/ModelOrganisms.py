
# Tools for managing the processing of SGD files

import MySQLdb
import sys, string
import Config

class ModelOrganisms( ) :

	def __init__( self, db, cursor ) :
		self.db = db
		self.cursor = cursor

	def buildSGDIDHash( self ) :
		
		self.cursor.execute( "SELECT gene_id, gene_external_value FROM " + Config.DB_NAME + ".gene_externals" )
		
		mappingHash = {}
		for row in self.cursor.fetchall( ) :
			mappingHash[str(row[1])] = str(row[0])
			
		return mappingHash
		
	def buildPombaseIDHash( self ) :
		
		self.cursor.execute( "SELECT gene_id, gene_alias_value FROM " + Config.DB_NAME + ".gene_aliases WHERE gene_id IN ( SELECT gene_id FROM " + Config.DB_NAME + ".genes WHERE organism_id='284812' )" )
		
		mappingHash = {}
		for row in self.cursor.fetchall( ) :
			mappingHash[str(row[1])] = str(row[0])
			
		return mappingHash
		
	def buildWormbaseLocusIDHash( self ) :
	
		self.cursor.execute( "SELECT gene_id, gene_alias_value FROM " + Config.DB_NAME + ".gene_aliases WHERE gene_id IN ( SELECT gene_id FROM " + Config.DB_NAME + ".genes WHERE organism_id='6239' ) AND gene_alias_type='ordered locus'" )
		
		mappingHash = {}
		for row in self.cursor.fetchall( ) :
			mappingHash[str(row[1]).replace( "CELE_", "" )] = str(row[0])
			
		return mappingHash
		
	def buildCGDAliasHash( self ) :
		
		self.cursor.execute( "SELECT gene_id, gene_alias_value FROM " + Config.DB_NAME + ".gene_aliases WHERE gene_id IN ( SELECT gene_id FROM " + Config.DB_NAME + ".genes WHERE organism_id='237561' )" )
		
		mappingHash = {}
		for row in self.cursor.fetchall( ) :
			if str(row[1]) not in mappingHash :
				mappingHash[str(row[1])] = []
			mappingHash[str(row[1])].append(str(row[0]))
			
		return mappingHash
		
	def processName( self, geneID, orfName, officialSymbol, officialType, aliases) :
	
		self.cursor.execute( "SELECT gene_name FROM " + Config.DB_NAME + ".genes WHERE gene_id=%s LIMIT 1", [geneID] )
		row = self.cursor.fetchone( )
		
		if "" != officialSymbol and row[0].lower( ) != officialSymbol.lower( ) :
			self.cursor.execute( "UPDATE " + Config.DB_NAME + ".genes SET gene_name=%s, gene_name_type=%s WHERE gene_id=%s", [officialSymbol, officialType, geneID] )
			
		self.cursor.execute( "SELECT gene_alias_value FROM " + Config.DB_NAME +  ".gene_aliases WHERE gene_id=%s AND gene_alias_status='active'", [geneID] )
		
		aliasSet = set( )
		for row in self.cursor.fetchall( ) :
			aliasSet.add( row[0].strip( ).lower( ) )
			
		if "" != orfName and orfName.lower( ) not in aliasSet :
			self.cursor.execute( "UPDATE " + Config.DB_NAME + ".gene_aliases SET gene_alias_type='synonym' WHERE gene_alias_type='ordered locus' AND gene_id=%s", [geneID] )
			self.cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_aliases VALUES( '0',%s, 'active', 'ordered locus', NOW( ), %s )", [orfName, geneID] )
			
		if "" != officialSymbol and officialSymbol.lower( ) not in aliasSet :
			self.cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_aliases VALUES( '0',%s, 'active', %s, NOW( ), %s )", [officialSymbol, officialType, geneID] )
		
		for alias in aliases :
			alias = alias.strip( )
			if "" != alias and alias.lower( ) not in aliasSet :
				self.cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_aliases VALUES( '0',%s, 'active', 'synonym', NOW( ), %s )", [alias, geneID] )
				
		self.db.commit( )
		
	def processAddonSGDIDs( self, geneID, additionalSGDIDs ) :
	
		self.cursor.execute( "SELECT gene_external_value FROM " + Config.DB_NAME +  ".gene_externals WHERE gene_id=%s AND gene_external_status='active'", [geneID] )
		
		externalSet = set( )
		for row in self.cursor.fetchall( ) :
			externalSet.add( row[0].lower( ) )
			
		for external in additionalSGDIDs :
			external = external.strip( )
			if "" != external and external.lower( ) not in externalSet :
				self.cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_aliases VALUES( '0', %s, 'active', 'synonym', NOW( ), %s )", [external, geneID] )
				
		self.db.commit( )
		
	def processDefinition( self, geneID, definition, definitionType ) :
	
		self.cursor.execute( "SELECT gene_definition_text FROM " + Config.DB_NAME +  ".gene_definitions WHERE gene_id=%s AND gene_definition_status='active'", [geneID] )
		
		definitionSet = set( )
		for row in self.cursor.fetchall( ) :
			definitionSet.add( row[0].lower( ) )
			
		definition = definition.strip( )
			
		if "" != definition and definition.lower( ) not in definitionSet :
			self.cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_definitions VALUES( '0', %s, %s, 'active', NOW( ), %s )", [definition, definitionType, geneID] )
				
		self.db.commit( )
		
	def processExternals( self, geneID, externals, externalSource ) :
	
		self.cursor.execute( "SELECT gene_external_value FROM " + Config.DB_NAME +  ".gene_externals WHERE gene_id=%s AND gene_external_source=%s AND gene_external_status='active'", [geneID, externalSource] )
	
		externalSet = set( )
		for row in self.cursor.fetchall( ) :
			externalSet.add( row[0].lower( ) )
		
		for external in externals :
			external = external.strip( )
			if "" != external and external.lower( ) not in externalSet :
				self.cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_externals VALUES( '0',%s,%s,'active',NOW( ),%s )", [external, externalSource.upper( ), geneID] )
				
		self.db.commit( )