
# Tools for managing the processing of uniprotkb proteins

import MySQLdb
import sys, string
import Config

from classes import GeneOntology

class UniprotKB( ) :

	def __init__( self, db, cursor ) :
		self.db = db
		self.cursor = cursor
		self.geneOntology = GeneOntology.GeneOntology( db, cursor )
		self.goIDHash = self.geneOntology.buildGOIDHash( )
		self.goEvidenceHash = self.geneOntology.buildEvidenceHash( )
		
	def buildAccessionHash( self ) :
	
		self.cursor.execute( "SELECT uniprot_alias_value, uniprot_id FROM " + Config.DB_NAME + ".uniprot_aliases WHERE uniprot_alias_status='active' AND (uniprot_alias_type = 'primary-accession' OR uniprot_alias_type = 'accession') GROUP BY uniprot_alias_value" )
		
		accessionHash = { }
		for row in self.cursor.fetchall( ) :
			accessionHash[str(row[0])] = str(row[1])
			
		return accessionHash
		
	def buildOrganismHash( self ) :
	
		self.cursor.execute( "SELECT uniprot_id, organism_id FROM " + Config.DB_NAME + ".uniprot" )
		
		organismHash = { }
		for row in self.cursor.fetchall( ) :
			organismHash[str(row[0])] = str(row[1])
			
		return organismHash
		
	def processIsoform( self, uniprotID, organismID, isoEntry ) :
	
		geneVal = isoEntry["GENE"]
		if "" == geneVal :
			geneVal = "-"
			
		sequence = ("".join( isoEntry['SEQUENCE'] )).upper( )
		sequenceLength = str(len(sequence))
			
		self.cursor.execute( "INSERT INTO " + Config.DB_NAME + ".uniprot_isoforms VALUES( '0',%s,%s,%s,%s,%s,%s,'active',NOW( ),%s,%s )", [isoEntry["ACCESSION"], isoEntry["ISOFORM"], sequence, sequenceLength, isoEntry["NAME"], isoEntry["DESC"], organismID, uniprotID] )
		self.db.commit( )
		
	def processProtein( self, uniprotEntry, organismID ) :
		
		self.cursor.execute( "SELECT uniprot_id FROM " + Config.DB_NAME + ".uniprot WHERE uniprot_identifier_value=%s LIMIT 1", [uniprotEntry['primary_accession']] )
		
		descriptionVal = "-"
		descriptionList = []
		if 'descriptions' in uniprotEntry :
			for description in uniprotEntry['descriptions'] :
				if "RECOMMENDED_NAME" == description["TYPE"] :
					descriptionVal = description["DESC"]
					break
				elif "ALT_NAME" == description["TYPE"] :
					descriptionList.append( description["DESC"] )
			
			if len(descriptionList) > 0 and "-" == descriptionVal :
				descriptionVal = descriptionList[0]
		
		row = self.cursor.fetchone( )
		if None == row :
			self.cursor.execute( "INSERT INTO " + Config.DB_NAME + ".uniprot VALUES ( '0',%s,%s,%s,%s,%s,%s,%s,%s,'active',NOW( ),%s )", [uniprotEntry['primary_accession'], uniprotEntry['sequence'], uniprotEntry['sequence_length'], uniprotEntry['name'], descriptionVal, uniprotEntry['dataset'].upper( ), uniprotEntry['sequence_version'], uniprotEntry['existence'], organismID] )
			return self.cursor.lastrowid
		else :
			self.cursor.execute( "UPDATE " + Config.DB_NAME + ".uniprot SET uniprot_sequence=%s, uniprot_sequence_length=%s, uniprot_name=%s, uniprot_description=%s, uniprot_source=%s, uniprot_version=%s, uniprot_curation_status=%s, uniprot_status='active' WHERE uniprot_id=%s", [uniprotEntry['sequence'], uniprotEntry["sequence_length"], uniprotEntry['name'], descriptionVal, uniprotEntry['dataset'].upper( ), uniprotEntry['sequence_version'], uniprotEntry['existence'], row[0]] )
			return row[0]
			
		self.db.commit( )
		
	def processAliases( self, uniprotID, uniprotEntry ) :
	
		if 'primary_accession' in uniprotEntry :
			self.cursor.execute( "INSERT INTO " + Config.DB_NAME + ".uniprot_aliases VALUES( '0', %s, %s, 'active', NOW( ), %s )", [uniprotEntry['primary_accession'], 'primary-accession', uniprotID] )
	
		if 'accessions' in uniprotEntry :
			
			for accession in uniprotEntry['accessions'] :
				self.cursor.execute( "INSERT INTO " + Config.DB_NAME + ".uniprot_aliases VALUES( '0', %s, %s, 'active', NOW( ), %s )", [accession, 'accession', uniprotID] )
			
		if 'genes' in uniprotEntry :
			
			for genes in uniprotEntry['genes'] :
				for geneNameType, geneNameSet in genes.items( ) :
			
					if "primary" == geneNameType.lower( ) :
						geneNameType = "uniprot-official"
			
					for geneName in geneNameSet :
						self.cursor.execute( "INSERT INTO " + Config.DB_NAME + ".uniprot_aliases VALUES( '0', %s, %s, 'active', NOW( ), %s )", [geneName, geneNameType, uniprotID] )
		
		self.db.commit( )
		
	def processExternals( self, uniprotID, uniprotEntry ) :
				
		if 'externals' in uniprotEntry :
			
			for externalType, externalSet in uniprotEntry['externals'].items( ) :
				for external in externalSet :
					self.cursor.execute( "INSERT INTO " + Config.DB_NAME + ".uniprot_externals VALUES( '0', %s, %s, 'active', NOW( ), %s )", [external, externalType.upper( ), uniprotID] )
		
		if 'entrez_gene' in uniprotEntry :
		
			for entrezGeneID in uniprotEntry['entrez_gene'] :
				self.cursor.execute( "INSERT INTO " + Config.DB_NAME + ".uniprot_externals VALUES( '0', %s, %s, 'active', NOW( ), %s )", [entrezGeneID, "ENTREZ_GENE", uniprotID] )
				self.cursor.execute( "INSERT INTO " + Config.DB_NAME + ".uniprot_externals VALUES( '0', %s, %s, 'active', NOW( ), %s )", ["ETG" + entrezGeneID, "ENTREZ_GENE_ETG", uniprotID] )
		
		self.db.commit( )
		
	def processDefinitions( self, uniprotID, uniprotEntry ) :
				
		if 'descriptions' in uniprotEntry :
			
			for description in uniprotEntry['descriptions'] :
				self.cursor.execute( "INSERT INTO " + Config.DB_NAME + ".uniprot_definitions VALUES( '0', %s, %s, 'active', NOW( ), %s )", [description["DESC"], description["TYPE"].upper( ), uniprotID] )
				
		self.db.commit( )
		
	def processGO( self, uniprotID, uniprotEntry ) :
	
		if 'go' in uniprotEntry :
			
			for goMapping in uniprotEntry['go'] :
				if goMapping['full_id'] in self.goIDHash and 'evidence' in goMapping :
					goID = self.goIDHash[goMapping['full_id']]
					if goMapping['evidence'].upper( ) in self.goEvidenceHash :
						self.cursor.execute( "INSERT INTO " + Config.DB_NAME + ".uniprot_go VALUES( '0', %s, %s, 'active', NOW( ), %s )", [goID, self.goEvidenceHash[goMapping['evidence'].upper( )], uniprotID] )

		self.db.commit( )
			
	def processFeatures( self, uniprotID, uniprotEntry ) :
	
		if 'features' in uniprotEntry :
		
			for feature in uniprotEntry['features'] :
				featureType = feature['type']
				
				featureDesc = '-'
				if 'description' in feature :
					featureDesc = feature['description']
				
				featureID = '-'
				if 'id' in feature :
					featureID = feature['id']
				
				featurePos = '0'
				if 'position' in feature :
					featurePos = feature['position']
				
				featureBegin = '0'
				if 'begin' in feature :
					featureBegin = feature['begin']
				
				featureEnd = '0'
				if 'end' in feature :
					featureEnd = feature['end']
				
				self.cursor.execute( "SELECT uniprot_feature_id FROM " + Config.DB_NAME + ".uniprot_features WHERE uniprot_id=%s AND uniprot_feature_type=%s AND uniprot_feature_external_id=%s AND uniprot_feature_start=%s AND uniprot_feature_end=%s AND uniprot_feature_position=%s LIMIT 1", [uniprotID, featureType.upper( ), featureID, featureBegin, featureEnd, featurePos] )
				
				row = self.cursor.fetchone( )
				if None == row :
					self.cursor.execute( "INSERT INTO " + Config.DB_NAME + ".uniprot_features VALUES ( '0',%s,%s,%s,%s,%s,%s,'active',NOW( ),%s )", [featureType.upper( ),featureDesc,featureID,featureBegin,featureEnd,featurePos,uniprotID] )
				else :
					self.cursor.execute( "UPDATE " + Config.DB_NAME + ".uniprot_features SET uniprot_feature_description=%s, uniprot_feature_status='active' WHERE uniprot_feature_id=%s", [featureDesc, row[0]] )
					
			self.db.commit( )