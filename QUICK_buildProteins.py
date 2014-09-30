
# Create the quick lookup protein annotation
# table by combining annotation from other
# resources into a single table.

import Config
import sys, string
import MySQLdb
import Database

from classes import Quick

with Database.db as cursor :

	quick = Quick.Quick( Database.db, cursor )
	orgHash = quick.fetchOrganismHash( )

	cursor.execute( "TRUNCATE TABLE " + Config.DB_QUICK + ".quick_proteins" )
	Database.db.commit( )
	
	cursor.execute( "SELECT * FROM " + Config.DB_NAME + ".proteins WHERE protein_status='active' AND protein_source != 'UNIPROT-ISOFORM' ORDER BY protein_id ASC LIMIT 1000" )
	
	for row in cursor.fetchall( ) :
	
		proteinRecord = []
		proteinID = str(row[0])
		proteinReferenceID = str(row[1])
		proteinType = row[2]
		
		proteinRecord.append( proteinID )
		proteinDetails = quick.fetchProtein( proteinReferenceID, proteinType )
		
		genes = "-"
		hasFeatures = "false"
		proteinOrder = 1
		
		goProcess = { "IDS" : [], "NAMES" : [], "EVIDENCE" : [] }
		goComponent = { "IDS" : [], "NAMES" : [], "EVIDENCE" : [] }
		goFunction = { "IDS" : [], "NAMES" : [], "EVIDENCE" : [] }
		
		aliases = []
		externalIDs = []
		externalTypes = []
		
		proteinMiddle = []
		
		if proteinDetails :
		
			if "UNIPROT" == proteinType.upper( ) :
				organismIndex = 11
				
				# Fetch REFSEQ IDs, ENTREZ GENE IDs, and EXTERNAL REFERENCES for the Uniprot Protein
				refseqIDs = quick.fetchRefseqIDsByUniprotID( proteinReferenceID )
				externalIDs, externalTypes, entrezGeneIDs = quick.fetchUniprotExternals( proteinReferenceID, refseqIDs )
				
				# Get actual GENE IDs for the Entrez Gene IDs
				geneIDs = quick.fetchGeneIDsByEntrezGeneIDs( entrezGeneIDs )
				
				if len(geneIDs) > 0 :
					genes = "|".join(geneIDs)
				
				# Aliases
				aliases = quick.fetchUniprotAliases( proteinReferenceID, geneIDs, proteinDetails[1] )
				
				# Sequence, Sequence Length, Name, Description, Source, Version, Curation Status
				proteinMiddle = [proteinDetails[2], proteinDetails[3], proteinDetails[4], proteinDetails[5], proteinDetails[6], proteinDetails[7], proteinDetails[8]]
				
				if quick.hasFeatures( proteinReferenceID ) :
					hasFeatures = "true"
					
				# Fetch GENE ONTOLOGY
				goProcess, goComponent, goFunction = quick.fetchGO( proteinReferenceID, "UNIPROT" )
				
			elif "REFSEQ" == proteinType.upper( ) :
				organismIndex = 7
				
				# Get actual GENE IDs for the Entrez Gene IDs
				geneID = quick.fetchGeneIDByRefseqID( proteinReferenceID )
				
				curationStatus = "-"
				
				if not geneID :
					geneID = "0"
				else :
					genes = geneID
					
				# Get official symbol
				officialSymbol = quick.fetchOfficialSymbol( geneID ) 
				
				# Get curation status
				curationStatus = quick.fetchCurationStatus( geneID, proteinReferenceID )
				
				# Grab external Info
				externalIDs, externalTypes = quick.fetchExternals( geneID, [proteinReferenceID] )
				
				# Aliases
				systematicName, aliases = quick.fetchAliases( geneID, officialSymbol )
				
				if "-" != systematicName :
					aliases.append( systematicName )
					
				aliases = set( aliases )
				
				# Sequence, Sequence Length, Name, Description, Source, Version, Curation Status
				proteinMiddle = [proteinDetails[3], proteinDetails[4], officialSymbol, proteinDetails[5], 'REFSEQ', proteinDetails[6], curationStatus]
				
				if quick.hasFeatures( proteinReferenceID ) :
					hasFeatures = "true"
					
				# Fetch GENE ONTOLOGY
				goProcess, goComponent, goFunction = quick.fetchGO( geneID, "GENE" )

			elif "UNIPROT-ISOFORM" == proteinType.upper( ) :
				organismIndex = 9
			
			# Primary Identifier and Isoform Number
			proteinRecord.extend( [proteinDetails[1],'1'] )
			
			# Aliases
			if len( aliases ) <= 0 :
				aliases = "-"
			else :
				aliases = "|".join(aliases)
			
			proteinRecord.append( aliases )
			
			# Externals
			if len( externalIDs ) <= 0 :
				externalIDs = "-"
				externalTypes = "-"
			else :
				externalIDs = "|".join(externalIDs)
				externalTypes = "|".join(externalTypes)
			
			proteinRecord.append( externalIDs )
			proteinRecord.append( externalTypes )
			
			# Add in Protein Middle Annotation
			proteinRecord.extend( proteinMiddle )
			
			# ADD Flag Columns
			proteinRecord.append(hasFeatures)
			
			hasGenes = "false"
			if "-" != genes :
				hasGenes = "true"
				
			proteinRecord.append(hasGenes)
			
			# Process Gene Ontology
			goCombined = {"IDS" : [], "NAMES" : [], "EVIDENCE" : []}
			
			goProcess, goCombined = quick.formatGOSet( goProcess, goCombined )
			goComponent, goCombined = quick.formatGOSet( goComponent, goCombined )
			goFunction, goCombined = quick.formatGOSet( goFunction, goCombined )
			
			if len(goCombined["IDS"]) > 0 :
				goCombined["IDS"] = "|".join( goCombined["IDS"] )
				goCombined["NAMES"] = "|".join( goCombined["NAMES"] )
				goCombined["EVIDENCE"] = "|".join( goCombined["EVIDENCE"] )
			else :
				goCombined["IDS"] = "-"
				goCombined["NAMES"] = "-"
				goCombined["EVIDENCE"] = "-"
				
			proteinRecord.extend( [goCombined["IDS"], goCombined["NAMES"], goCombined["EVIDENCE"]] )
			proteinRecord.extend( [goProcess["IDS"], goProcess["NAMES"], goProcess["EVIDENCE"]] )
			proteinRecord.extend( [goComponent["IDS"], goComponent["NAMES"], goComponent["EVIDENCE"]] )
			proteinRecord.extend( [goFunction["IDS"], goFunction["NAMES"], goFunction["EVIDENCE"]] )
			
			# Get organism info out of the hash
			(orgID, orgEntrezID, orgUniprotID, orgName, orgOfficial, orgAbbr, orgStrain) = orgHash[str(proteinDetails[organismIndex])]
			proteinRecord.extend( [str(orgID), orgName, orgOfficial, orgAbbr, orgStrain] )
			proteinRecord.extend( [proteinOrder,"0",genes] )
		
		sqlFormat = ",".join( ['%s'] * len(proteinRecord) )
		cursor.execute( "INSERT INTO " + Config.DB_QUICK + ".quick_proteins VALUES( %s )" % sqlFormat, tuple(proteinRecord) )

		proteinRecord = []