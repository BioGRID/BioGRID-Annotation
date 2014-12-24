
# Create the quick lookup protein annotation
# table by combining annotation from other
# resources into a single table.

import Config
import sys, string, argparse
import MySQLdb
import Database

from classes import Quick

# Process Command Line Input
argParser = argparse.ArgumentParser( description = 'Update all Annotation Records' )
argGroup = argParser.add_mutually_exclusive_group( )
argGroup.add_argument( '-o', dest='organismID', type = int, nargs = 1, help = 'An organism id to update annotation for', action='store' )
argGroup.add_argument( '-p', dest='proteinID', type = int, nargs = 1, help = 'A Protein ID to Update', action='store' )
argGroup.add_argument( '-all', dest='allRecords', help = 'Build from All Records, Starting from Scratch', action='store_true' )
inputArgs = vars( argParser.parse_args( ) )

isOrganism = False
isProtein = False
isAll = False

if None != inputArgs['organismID'] :
	isOrganism = True
elif None != inputArgs['proteinID'] :
	isProtein = True
else :
	isAll = True

with Database.db as cursor :

	quick = Quick.Quick( Database.db, cursor )
	orgHash = quick.fetchProteinOrganismHash( )
	
	if isOrganism :
		cursor.execute( "SELECT * FROM " + Config.DB_NAME + ".proteins WHERE organism_id=%s AND protein_status='active'", [inputArgs['organismID']] )
	
	elif isProtein :
		cursor.execute( "SELECT * FROM " + Config.DB_NAME + ".proteins WHERE protein_id=%s AND protein_status='active'", [inputArgs['proteinID']] )
	
	else :
		cursor.execute( "TRUNCATE TABLE " + Config.DB_QUICK + ".quick_proteins" )
		Database.db.commit( )
		
		cursor.execute( "SELECT * FROM " + Config.DB_NAME + ".proteins WHERE protein_status='active' ORDER BY protein_id ASC" )
	
	proteinCount = 0
	for row in cursor.fetchall( ) :
	
		proteinCount = proteinCount + 1
		print "Working on: " + str(proteinCount)
	
		proteinRecord = []
		proteinID = str(row[0])
		proteinReferenceID = str(row[1])
		proteinType = row[2]
		
		proteinRecord.append( proteinID )
		proteinDetails = quick.fetchProtein( proteinReferenceID, proteinType )
		
		genes = "-"
		officialSymbol = "-"
		hasFeatures = "false"
		proteinOrder = 1
		proteinParent = 0
		
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
				
				officialSymbol = proteinDetails[1]
				
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
				
				officialSymbol = proteinDetails[1]
				
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
				
				officialSymbol = proteinDetails[1] + "-" + str(proteinDetails[2])
				proteinParent = quick.fetchUniprotIsoformParent( str(proteinDetails[10]) )
				proteinOrder = proteinDetails[2]
				
				# Fetch REFSEQ IDs, ENTREZ GENE IDs, and EXTERNAL REFERENCES for the Uniprot Protein
				refseqIDs = quick.fetchRefseqIDsByUniprotID( str(proteinDetails[10]) )
				externalIDs, externalTypes, entrezGeneIDs = quick.fetchUniprotExternals( str(proteinDetails[10]), refseqIDs )
				
				# Get actual GENE IDs for the Entrez Gene IDs
				geneIDs = quick.fetchGeneIDsByEntrezGeneIDs( entrezGeneIDs )
				
				if len(geneIDs) > 0 :
					genes = "|".join(geneIDs)
				
				# Aliases
				aliases = quick.fetchUniprotAliases( proteinReferenceID, geneIDs, proteinDetails[1] )
				
				# Sequence, Sequence Length, Name, Description, Source, Version, Curation Status
				proteinMiddle = [proteinDetails[3], proteinDetails[4], proteinDetails[5], proteinDetails[6], 'UNIPROT-ISOFORM', '1', 'Isoform']
				
				if quick.hasFeatures( proteinReferenceID ) :
					hasFeatures = "true"
					
				# Fetch GENE ONTOLOGY
				goProcess, goComponent, goFunction = quick.fetchGO( proteinReferenceID, "UNIPROT" )
			
			# Primary Identifier and Isoform Number
			proteinRecord.extend( [officialSymbol,'1'] )
			
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
			proteinRecord.extend( [proteinOrder, proteinParent,"0",genes] )
		
		sqlFormat = ",".join( ['%s'] * len(proteinRecord) )
		
		if isProtein or isOrganism :
			cursor.execute( "SELECT protein_id FROM " + Config.DB_QUICK + ".quick_proteins WHERE protein_id=%s LIMIT 1", [proteinID] )
			proteinExists = cursor.fetchone( )
			
			if None == proteinExists :
				cursor.execute( "INSERT INTO " + Config.DB_QUICK + ".quick_proteins VALUES( %s )" % sqlFormat, tuple(proteinRecord) )
			else :
				proteinRecord.pop(0)
				proteinRecord.append( proteinID )
				cursor.execute( "UPDATE " + Config.DB_QUICK + ".quick_proteins SET protein_identifier_value=%s, protein_isoform=%s, protein_aliases=%s, protein_externalids=%s, protein_externalids_types=%s, protein_sequence=%s, protein_sequence_length=%s, protein_name=%s, protein_description=%s, protein_source=%s, protein_version=%s, protein_curation_status=%s, protein_hasfeatures=%s, protein_hasgenes=%s, go_ids_combined=%s, go_names_combined=%s, go_evidence_combined=%s, go_process_ids=%s, go_process_names=%s, go_process_evidence=%s, go_component_ids=%s, go_component_names=%s, go_component_evidence=%s, go_function_ids=%s, go_function_names=%s, go_function_evidence=%s, organism_id=%s, organism_common_name=%s, organism_official_name=%s, organism_abbreviation=%s, organism_strain=%s, protein_ordering=%s, protein_parent=%s, interaction_count=%s, gene_ids=%s WHERE protein_id=%s", tuple(proteinRecord) )
		else :	
			cursor.execute( "INSERT INTO " + Config.DB_QUICK + ".quick_proteins VALUES( %s )" % sqlFormat, tuple(proteinRecord) )
		
		if 0 == (proteinCount % Config.DB_COMMIT_COUNT ) :
			Database.db.commit( )
			
		proteinRecord = []
	
	Database.db.commit( )
		
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'QUICK_buildProteins', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )