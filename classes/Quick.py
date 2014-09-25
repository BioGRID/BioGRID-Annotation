
# Tools for managing the building of quick lookup tables

import MySQLdb
import sys, string
import Config

class Quick( ) :

	def __init__( self, db, cursor ) :
		self.db = db
		self.cursor = cursor
		
	def fetchOrganismHash( self ) :
		
		self.cursor.execute( "SELECT * FROM " + Config.DB_QUICK + ".quick_organisms" )
		
		organismHash = { }
		for row in self.cursor.fetchall( ) :
			organismHash[str(row[0])] = row
			
		return organismHash
		
	def fetchExternals( self, geneID, refseqIDs ) :
	
		externalIDSet = []
		externalTypeSet = []
		
		if len(geneID) > 0 :
			self.cursor.execute( "SELECT gene_external_value, gene_external_source FROM " + Config.DB_NAME + ".gene_externals WHERE gene_external_status='active' AND gene_id=%s", [geneID] )
			
			for row in self.cursor.fetchall( ) :
				externalIDSet.append( str(row[0]) )
				externalTypeSet.append( row[1] )
				
			if len(refseqIDs) > 0 :
				sqlFormat = ",".join( ['%s'] * len(refseqIDs) )
				self.cursor.execute( "SELECT refseq_accession, refseq_gi FROM " + Config.DB_NAME + ".refseq WHERE refseq_id IN (%s) and refseq_status='active'" % sqlFormat, tuple(refseqIDs) )
	
				for row in self.cursor.fetchall( ) :
					externalIDSet.extend( [str(row[0]), str(row[1])] )
					externalTypeSet.extend( ["REFSEQ-PROTEIN-ACCESSION", "REFSEQ-PROTEIN-GI"] )
					
				self.cursor.execute( "SELECT refseq_identifier_value, refseq_identifier_type FROM " + Config.DB_NAME + ".refseq_identifiers WHERE refseq_id IN (%s) and refseq_identifier_status='active'" % sqlFormat, tuple(refseqIDs) )
	
				for row in self.cursor.fetchall( ) :
					externalIDSet.append( str(row[0]) )
					
					refseqType = "REFSEQ"
					if "rna-accession" == row[1].lower( ) :
						refseqType = "REFSEQ-RNA-ACCESSION"	
					elif "rna-gi" == row[1].lower( ) :
						refseqType = "REFSEQ-RNA-GI"
						
					externalTypeSet.append( refseqType )
	
		return externalIDSet, externalTypeSet
		
	def fetchAliases( self, geneID, officialSymbol ) :
	
		aliases = set( )
		systematicName = "-"
		
		if len(geneID) > 0 :
			
			self.cursor.execute( "SELECT gene_alias_value, gene_alias_type FROM " + Config.DB_NAME + ".gene_aliases WHERE gene_alias_status='active' and gene_id=%s", [geneID] )
			
			for row in self.cursor.fetchall( ) :
				if "ordered locus" == row[1] :
					systematicName = str(row[0])
				else :
					if row[0].upper( ) != officialSymbol.upper( ) :
						aliases.add( str(row[0]) )
						
		return systematicName, aliases
		
	def fetchRefseqIDs( self, geneID ) :
		
		refseqIDs = set( )
		self.cursor.execute( "SELECT refseq_id FROM " + Config.DB_NAME + ".gene_refseqs WHERE gene_id=%s and gene_refseq_status='active'", [geneID] )
		
		for row in self.cursor.fetchall( ) :
			refseqIDs.add( str(row[0]) )
				
		return refseqIDs
		
	def fetchDescription( self, geneID, refseqIDs ) :
		
		if len(geneID) > 0 :
		
			descriptions = { }
			
			self.cursor.execute( "SELECT gene_definition_text, gene_definition_source FROM " + Config.DB_NAME + ".gene_definitions WHERE gene_definition_status='active' AND gene_id=%s", [geneID] )
			
			for row in self.cursor.fetchall( ) :
				if row[1] not in descriptions :
					descriptions[row[1]] = set( )
				descriptions[row[1]].add( row[0] )
				
			if 'CGD-DESCRIPTION' in descriptions :
				return "; ".join(descriptions['CGD-DESCRIPTION'])
			
			if 'SGD-DESCRIPTION' in descriptions :
				return "; ".join(descriptions['SGD-DESCRIPTION'])
				
			if 'POMBASE-DESCRIPTION' in descriptions :
				return "; ".join(descriptions['POMBASE-DESCRIPTION'])
				
			if len(refseqIDs) > 0 :
				sqlFormat = ",".join( ['%s'] * len(refseqIDs) )
				self.cursor.execute( "SELECT refseq_description FROM " + Config.DB_NAME + ".refseq WHERE refseq_id IN (%s) and refseq_status='active'" % sqlFormat, tuple(refseqIDs) )

				for row in self.cursor.fetchall( ) :
					if 'PROTEIN-DESCRIPTION' not in descriptions :
						descriptions['PROTEIN-DESCRIPTION'] = set( )
					descriptions['PROTEIN-DESCRIPTION'].add( row[0] )
				
			description = "-"
			if 'ENTREZ-DESCRIPTION' in descriptions :
				description = "; ".join(descriptions['ENTREZ-DESCRIPTION'])
						
			elif 'PROTEIN-DESCRIPTION' in definitions :
				
				longestDesc = "-"
				for description in descriptions['PROTEIN-DESCRIPTION'] :
					if len(longestDesc) <= len(description) :
						longestDesc = description
						
				description = longestDesc
				
			elif 'ENTREZ-OTHERDESIGNATION' in defintions :
				description = "; ".join(descriptions['ENTREZ-OTHERDESIGNATION'])
						
			elif 'ENTREZ-NOMENNAME' in defintions :
				description = "; ".join(descriptions['ENTREZ-NOMENNAME'])
				
				
		return description
			