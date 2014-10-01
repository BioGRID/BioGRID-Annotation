
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
		
	def fetchGO( self, itemID, itemType ) :
	
		goProcess = { "IDS" : [], "NAMES" : [], "EVIDENCE" : [] }
		goComponent = { "IDS" : [], "NAMES" : [], "EVIDENCE" : [] }
		goFunction = { "IDS" : [], "NAMES" : [], "EVIDENCE" : [] }
		
		if len(itemID) > 0 :
			
			if "GENE" == itemType.upper( ) :
				self.cursor.execute( "SELECT go_id, go_evidence_code_id FROM " + Config.DB_NAME + ".gene_go WHERE gene_id=%s AND gene_go_status='active'", [itemID] )
			elif "UNIPROT" == itemType.upper( ) :
				self.cursor.execute( "SELECT go_id, go_evidence_code_id FROM " + Config.DB_NAME + ".uniprot_go WHERE uniprot_id=%s AND uniprot_go_status='active'", [itemID] )
		
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
		
	def fetchExternalsForRefseq( self, refseqIDs ) :
	
		externalIDSet = []
		externalTypeSet = []
	
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
		
	def fetchExternals( self, geneID, refseqIDs ) :
	
		externalIDSet = []
		externalTypeSet = []
		
		if len(geneID) > 0 :
			self.cursor.execute( "SELECT gene_external_value, gene_external_source FROM " + Config.DB_NAME + ".gene_externals WHERE gene_external_status='active' AND gene_id=%s", [geneID] )
			
			for row in self.cursor.fetchall( ) :
				externalIDSet.append( str(row[0]) )
				externalTypeSet.append( row[1] )
				
			refseqExternals, refseqExternalTypes = self.fetchExternalsForRefseq( refseqIDs )
			
			if len(refseqExternals) > 0 :
				externalIDSet.extend(refseqExternals)
				externalTypeSet.extend(refseqExternalTypes)
	
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
						
			elif 'PROTEIN-DESCRIPTION' in descriptions :
				
				longestDesc = "-"
				for description in descriptions['PROTEIN-DESCRIPTION'] :
					if len(longestDesc) <= len(description) :
						longestDesc = description
						
				description = longestDesc
				
			elif 'ENTREZ-OTHERDESIGNATION' in descriptions :
				description = "; ".join(descriptions['ENTREZ-OTHERDESIGNATION'])
						
			elif 'ENTREZ-NOMENNAME' in descriptions :
				description = "; ".join(descriptions['ENTREZ-NOMENNAME'])
				
				
		return description
		
	def fetchProtein( self, proteinRefID, proteinType ) :
	
		proteinDetails = []
		if len(proteinRefID) > 0 :
			
			if "UNIPROT" == proteinType.upper( ) :
				proteinDetails = self.fetchUniprotProtein( proteinRefID )
			elif "REFSEQ" == proteinType.upper( ) :
				proteinDetails = self.fetchRefseqProtein( proteinRefID )
			elif "UNIPROT-ISOFORM" == proteinType.upper( ) :
				proteinDetails = self.fetchUniprotIsoformProtein( proteinRefID )
			else :
				proteinDetails = False
			
		return proteinDetails
			
	def fetchUniprotProtein( self, uniprotID ) :
	
		self.cursor.execute( "SELECT * FROM " + Config.DB_NAME + ".uniprot WHERE uniprot_id=%s and uniprot_status='active' LIMIT 1", [uniprotID] )
		
		row = self.cursor.fetchone( )
		return row
		
	def fetchRefseqProtein( self, refseqID ) :
	
		self.cursor.execute( "SELECT * FROM " + Config.DB_NAME + ".refseq WHERE refseq_id=%s and refseq_status='active' LIMIT 1", [refseqID] )
		
		row = self.cursor.fetchone( )
		return row
		
	def fetchUniprotIsoformProtein( self, uniprotIsoformID ) :
	
		self.cursor.execute( "SELECT * FROM " + Config.DB_NAME + ".uniprot_isoforms WHERE uniprot_isoform_id=%s and uniprot_isoform_status='active' LIMIT 1", [uniprotIsoformID] )
		
		row = self.cursor.fetchone( )
		return row
		
	def fetchUniprotExternals( self, uniprotID, refseqIDs ) :
	
		externalIDSet = []
		externalTypeSet = []
		geneIDs = []
		
		self.cursor.execute( "SELECT uniprot_external_value, uniprot_external_source FROM " + Config.DB_NAME + ".uniprot_externals WHERE uniprot_id=%s AND uniprot_external_source != 'REFSEQ' AND uniprot_external_status='active'", [uniprotID] )
		
		for row in self.cursor.fetchall( ) :
		
			value = str(row[0]).upper( ).replace( "HGNC:", "" ).replace( "MGI:", "" ).replace( "RGD:", "" )
		
			externalIDSet.append( value )
			externalTypeSet.append( row[1] )
			
			if "ENTREZ_GENE" == row[1].upper( ) :
				geneIDs.append( str(row[0]) )
			
		if len(refseqIDs) > 0 :
			refseqExternals, refseqExternalTypes = self.fetchExternalsForRefseq( refseqIDs )
				
			if len(refseqExternals) > 0 :
				externalIDSet.extend(refseqExternals)
				externalTypeSet.extend(refseqExternalTypes)
				
		return externalIDSet, externalTypeSet, geneIDs
		
	def fetchRefseqIDsByUniprotID( self, uniprotID ) :
	
		refseqIDs = set( )
		if len(uniprotID) > 0 :
			self.cursor.execute( "SELECT refseq_id FROM " + Config.DB_NAME + ".protein_mapping WHERE uniprot_id=%s AND protein_mapping_status='active'", [uniprotID] )
			
			for row in self.cursor.fetchall( ) :
				refseqIDs.add( str(row[0]) )
				
		return refseqIDs
		
	def fetchGeneIDsByEntrezGeneIDs( self, entrezGeneIDs ) :
	
		geneIDs = set( )
		if len(entrezGeneIDs) > 0 :
			sqlFormat = ",".join( ['%s'] * len(entrezGeneIDs) )
			self.cursor.execute( "SELECT gene_id FROM " + Config.DB_NAME + ".genes WHERE gene_source_id IN (%s) AND gene_source='ENTREZ' AND gene_status='active'" % sqlFormat, tuple(entrezGeneIDs) )
			
			for row in self.cursor.fetchall( ) :
				geneIDs.add( str(row[0]) )
				
		return geneIDs
		
	def fetchGeneIDByRefseqID( self, refseqID ) :
	
		geneIDs = set( )
		if len(refseqID) > 0 :
			self.cursor.execute( "SELECT gene_id FROM " + Config.DB_NAME + ".gene_refseqs WHERE refseq_id=%s AND gene_refseq_status='active' LIMIT 1", [refseqID] )
			
			row = self.cursor.fetchone( )
			if None != row :
				return str(row[0])
				
		return False
		
	def hasFeatures( self, uniprotID ) :
		
		self.cursor.execute( "SELECT uniprot_feature_id FROM " + Config.DB_NAME + ".uniprot_features WHERE uniprot_id=%s AND uniprot_feature_status='active' LIMIT 1", [uniprotID] )
		row = self.cursor.fetchone( )
		
		if None == row :
			return False
			
		return True
		
	def fetchUniprotAliases( self, uniprotID, geneIDs, primaryIdentifier ) :
	
		aliases = []
		
		if len(uniprotID) > 0 :
		
			self.cursor.execute( "SELECT uniprot_alias_value FROM " + Config.DB_NAME + ".uniprot_aliases WHERE uniprot_id=%s AND uniprot_alias_status='active'", [uniprotID] )
						
			for row in self.cursor.fetchall( ) :
				if row[0].upper( ) != primaryIdentifier.upper( ) :
					aliases.append( str(row[0]) )
					
		if len(geneIDs) > 0 :
			for geneID in geneIDs :
				systematicName, geneAliases = self.fetchAliases( geneID, primaryIdentifier )
				
				if "-" != systematicName :
					aliases.append( systematicName )
				
				if len(geneAliases) > 0 :
					aliases.extend( geneAliases )
						
		return set( aliases )
		
	def fetchOfficialSymbol( self, geneID ) :
	
		self.cursor.execute( "SELECT gene_name FROM " + Config.DB_NAME + ".genes WHERE gene_id=%s LIMIT 1", [geneID] )
		row = self.cursor.fetchone( )
		
		if None == row :
			return "-"
			
		return row[0]
		
	def fetchCurationStatus( self, geneID, refseqID ) :
	
		self.cursor.execute( "SELECT refseq_status FROM " + Config.DB_NAME + ".gene_refseqs WHERE gene_id=%s AND refseq_id=%s LIMIT 1", [geneID, refseqID] )
		row = self.cursor.fetchone( )
		
		if None == row :
			return "-"
			
		return row[0]
		
	def fetchUniprotIsoformParent( self, uniprotID ) :
		
		self.cursor.execute( "SELECT protein_id FROM " + Config.DB_NAME + ".proteins WHERE protein_reference_id=%s and protein_source='UNIPROT'", [uniprotID] )
		row = self.cursor.fetchone( )
		
		if None == row :
			return "0"
		
		return row[0]