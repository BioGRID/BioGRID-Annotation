
# Tools for managing the building of quick lookup tables

import MySQLdb
import sys, string
import Config

class Quick( ) :

	def __init__( self, db, cursor ) :
		self.db = db
		self.cursor = cursor
		self.goDefs = self.fetchGODefinitionHash( )
		self.goEvidence = self.fetchGOEvidenceHash( )
		
	def fetchOrganismHash( self ) :
		
		self.cursor.execute( "SELECT * FROM " + Config.DB_QUICK + ".quick_organisms" )
		
		organismHash = { }
		for row in self.cursor.fetchall( ) :
			organismHash[str(row[0])] = row
			
		return organismHash
		
	def fetchGODefinitionHash( self ) :
	
		self.cursor.execute( "SELECT go_id, go_name, go_type FROM " + Config.DB_NAME + ".go_definitions" )
		
		goHash = { }
		for row in self.cursor.fetchall( ) :
			goHash[str(row[0])] = row
			
		return goHash
		
	def fetchGOEvidenceHash( self ) :
	
		self.cursor.execute( "SELECT go_evidence_code_id, go_evidence_code_symbol FROM " + Config.DB_NAME + ".go_evidence_codes" )
		
		goHash = { }
		for row in self.cursor.fetchall( ) :
			goHash[str(row[0])] = row[1]
			
		return goHash
		
	def formatGOSet( self, goSet, goCombined ) :
	
		if len(goSet["IDS"]) > 0 :
			goCombined["IDS"] = goCombined["IDS"] + goSet["IDS"]
			goCombined["NAMES"] = goCombined["NAMES"] + goSet["NAMES"]
			goCombined["EVIDENCE"] = goCombined["EVIDENCE"] + goSet["EVIDENCE"]
			
			goSet["IDS"] = "|".join( goSet["IDS"] )
			goSet["NAMES"] = "|".join( goSet["NAMES"] )
			goSet["EVIDENCE"] = "|".join( goSet["EVIDENCE"] )
			
		else :
			
			goSet["IDS"] = "-"
			goSet["NAMES"] = "-"
			goSet["EVIDENCE"] = "-"
			
		return goSet, goCombined
		
	def fetchGO( self, geneID ) :
	
		goProcess = { "IDS" : [], "NAMES" : [], "EVIDENCE" : [] }
		goComponent = { "IDS" : [], "NAMES" : [], "EVIDENCE" : [] }
		goFunction = { "IDS" : [], "NAMES" : [], "EVIDENCE" : [] }
		
		if len(geneID) > 0 :
			self.cursor.execute( "SELECT go_id, go_evidence_code_id FROM " + Config.DB_NAME + ".gene_go WHERE gene_id=%s AND gene_go_status='active'", [geneID] )
		
			for row in self.cursor.fetchall( ) :
				(goID, goName, goType) = self.goDefs[str(row[0])]
				goEvidence = self.goEvidence[str(row[1])]
				
				goCompare = goName.upper( )
				if "BIOLOGICAL_PROCESS" != goCompare and "CELLULAR_COMPONENT" != goCompare and "MOLECULAR_FUNCTION" != goCompare :
					
					goCompare = goType.upper( )
					if "BIOLOGICAL_PROCESS" == goCompare :
						goProcess["IDS"].append( str(goID) )
						goProcess["EVIDENCE"].append( goEvidence )
						goProcess["NAMES"].append( goName )
					
					elif "CELLULAR_COMPONENT" == goCompare :
						goComponent["IDS"].append( str(goID) )
						goComponent["EVIDENCE"].append( goEvidence )
						goComponent["NAMES"].append( goName )
						
					elif "MOLECULAR_FUNCTION" == goCompare :
						goFunction["IDS"].append( str(goID) )
						goFunction["EVIDENCE"].append( goEvidence )
						goFunction["NAMES"].append( goName )	
		
		return goProcess, goComponent, goFunction
		
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
				self.cursor.execute( "SELECT refseq_accession, refseq_gi, refseq_version FROM " + Config.DB_NAME + ".refseq WHERE refseq_id IN (%s) and refseq_status='active'" % sqlFormat, tuple(refseqIDs) )
	
				for row in self.cursor.fetchall( ) :
					externalIDSet.extend( [str(row[0]), str(row[1])] )
					externalTypeSet.extend( ["REFSEQ-PROTEIN-ACCESSION", "REFSEQ-PROTEIN-GI"] )
					
					for version in range( 0, row[2] ) :
						externalIDSet.append( str(row[0]) + "." + str(version+1) )
						externalTypeSet.append( "REFSEQ-PROTEIN-ACCESSION-VERSIONED" )
					
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
	
		aliases = []
		systematicName = "-"
		
		if len(geneID) > 0 :
			
			self.cursor.execute( "SELECT gene_alias_value, gene_alias_type FROM " + Config.DB_NAME + ".gene_aliases WHERE gene_alias_status='active' and gene_id=%s", [geneID] )
			
			for row in self.cursor.fetchall( ) :
				if "ordered locus" == row[1] :
					systematicName = str(row[0])
				else :
					if row[0].upper( ) != officialSymbol.upper( ) :
						aliases.append( str(row[0]) )
						
		return systematicName, aliases
		
	def fetchRefseqIDs( self, geneID ) :
		
		refseqIDs = set( )
		
		if len(geneID) > 0 :
			self.cursor.execute( "SELECT refseq_id FROM " + Config.DB_NAME + ".gene_refseqs WHERE gene_id=%s and gene_refseq_status='active'", [geneID] )
		
			for row in self.cursor.fetchall( ) :
				refseqIDs.add( str(row[0]) )
				
		return refseqIDs
		
	def fetchUniprotIDs( self, refseqIDs ) :
	
		uniprotIDs = set( )
		
		if len(refseqIDs) > 0 :
			sqlFormat = ",".join( ['%s'] * len(refseqIDs) )
			self.cursor.execute( "SELECT uniprot_id FROM " + Config.DB_NAME + ".protein_mapping WHERE refseq_id IN (%s) and protein_mapping_status='active'" % sqlFormat, tuple(refseqIDs) )
		
			for row in self.cursor.fetchall( ) :
				uniprotIDs.add( str(row[0]) )
				
		return uniprotIDs
		
	def fetchUniprotNamesForGenes( self, uniprotIDs ) :

		uniprotAliases = []
		uniprotExternals = []
		uniprotExternalTypes = []
		
		if len(uniprotIDs) > 0 :
			sqlFormat = ",".join( ['%s'] * len(uniprotIDs) )
			self.cursor.execute( "SELECT uniprot_identifier_value, uniprot_name, uniprot_source FROM " + Config.DB_NAME + ".uniprot WHERE uniprot_id IN (%s) AND uniprot_status='active'" % sqlFormat, tuple(uniprotIDs) )

			for row in self.cursor.fetchall( ) :
				uniprotAliases.append( row[1] )
				uniprotExternals.append( row[0] )
				uniprotExternalTypes.append( row[2].upper( ) )
				
			self.cursor.execute( "SELECT uniprot_alias_value, uniprot_alias_type FROM " + Config.DB_NAME + ".uniprot_aliases WHERE uniprot_id IN (%s) AND uniprot_alias_type != 'primary-accession' AND uniprot_alias_status='active'" % sqlFormat, tuple(uniprotIDs) )
			
			for row in self.cursor.fetchall( ) :
				if 'ACCESSION' == row[1].upper( ) :
					uniprotExternals.append( row[0] )
					uniprotExternalTypes.append( 'UNIPROT-ACCESSION' )
				else :
					uniprotAliases.append( row[0] )
					
			self.cursor.execute( "SELECT uniprot_isoform_accession, uniprot_isoform_number FROM " + Config.DB_NAME + ".uniprot_isoforms WHERE uniprot_id IN (%s) AND uniprot_isoform_status = 'active'" % sqlFormat, tuple(uniprotIDs) )
					
			for row in self.cursor.fetchall( ) :
				
				isoform = row[0] + "-" + str(row[1])
				
				if isoform not in uniprotExternals :
				
					uniprotExternals.append( isoform )
					uniprotExternalTypes.append( 'UNIPROT-ISOFORM' )
					
		return uniprotAliases, uniprotExternals, uniprotExternalTypes
		
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
			