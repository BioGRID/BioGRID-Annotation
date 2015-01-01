
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
argGroup.add_argument( '-u', dest='uniprotID', type = int, nargs = 1, help = 'A Uniprot ID to Update', action='store' )
argGroup.add_argument( '-all', dest='allRecords', help = 'Build from All Records, Starting from Scratch', action='store_true' )
inputArgs = vars( argParser.parse_args( ) )

isOrganism = False
isUniprot = False
isAll = False

if None != inputArgs['organismID'] :
	isOrganism = True
elif None != inputArgs['uniprotID'] :
	isUniprot = True
else :
	isAll = True

with Database.db as cursor :

	quick = Quick.Quick( Database.db, cursor )
	orgHash = quick.fetchUniprotOrganismHash( )
	
	if isOrganism :
		cursor.execute( "SELECT * FROM " + Config.DB_NAME + ".uniprot WHERE organism_id=%s AND uniprot_status='active'", [inputArgs['organismID']] )
	
	elif isUniprot :
		cursor.execute( "SELECT * FROM " + Config.DB_NAME + ".uniprot WHERE uniprot_id=%s AND uniprot_status='active'", [inputArgs['proteinID']] )
	
	else :
		cursor.execute( "TRUNCATE TABLE " + Config.DB_QUICK + ".quick_uniprot" )
		Database.db.commit( )
		
		cursor.execute( "SELECT * FROM " + Config.DB_NAME + ".uniprot WHERE uniprot_status='active' ORDER BY uniprot_id ASC" )
	
	proteinCount = 0
	for row in cursor.fetchall( ) :
	
		proteinCount = proteinCount + 1
		print "Working on: " + str(proteinCount)
	
		proteinRecord = []
		proteinID = str(row[0])
		proteinType = "UNIPROT"
		
		proteinRecord.append( proteinID )
		proteinDetails = quick.fetchProtein( proteinID, proteinType )
		
		genes = "-"
		refseqs = "-"
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
		
			organismIndex = 11
			
			officialSymbol = proteinDetails[1]
			
			# Fetch REFSEQ IDs, ENTREZ GENE IDs, and EXTERNAL REFERENCES for the Uniprot Protein
			refseqIDs = quick.fetchRefseqIDsByUniprotID( proteinID )
			externalIDs, externalTypes, entrezGeneIDs = quick.fetchUniprotExternals( proteinID, refseqIDs )
			
			# Get actual GENE IDs for the Entrez Gene IDs
			geneIDs = quick.fetchGeneIDsByEntrezGeneIDs( entrezGeneIDs )
			refGeneIDs = quick.fetchGeneIDByRefseqIDs( refseqIDs )
			
			geneIDs = geneIDs.union(refGeneIDs)
			
			if len(geneIDs) > 0 :
				genes = "|".join(sorted(geneIDs, key=int))
				
			if len(refseqIDs) > 0 :
				refseqs = "|".join(sorted(refseqIDs, key=int))
			
			# Aliases
			aliases = quick.fetchUniprotAliases( proteinID, geneIDs, proteinDetails[1] )
			
			# Sequence, Sequence Length, Name, Description, Source, Version, Curation Status
			proteinMiddle = [proteinDetails[2], proteinDetails[3], proteinDetails[4], proteinDetails[5], proteinDetails[6], proteinDetails[7], proteinDetails[8]]
			
			if quick.hasFeatures( proteinID ) :
				hasFeatures = "true"
				
			# Fetch GENE ONTOLOGY
			goProcess, goComponent, goFunction = quick.fetchGO( proteinID, "UNIPROT" )
			
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
			(orgID, orgTaxID, orgName, orgOfficial, orgAbbr, orgStrain) = orgHash[str(proteinDetails[organismIndex])]
			proteinRecord.extend( [str(orgID), orgName, orgOfficial, orgAbbr, orgStrain] )
			proteinRecord.extend( [proteinOrder, proteinParent,"0",genes,refseqs] )
		
		sqlFormat = ",".join( ['%s'] * len(proteinRecord) )
		
		if isUniprot or isOrganism :
			cursor.execute( "SELECT uniprot_id FROM " + Config.DB_QUICK + ".quick_uniprot WHERE uniprot_id=%s LIMIT 1", [proteinID] )
			proteinExists = cursor.fetchone( )
			
			if None == proteinExists :
				cursor.execute( "INSERT INTO " + Config.DB_QUICK + ".quick_uniprot VALUES( %s )" % sqlFormat, tuple(proteinRecord) )
			else :
				proteinRecord.pop(0)
				proteinRecord.append( proteinID )
				cursor.execute( "UPDATE " + Config.DB_QUICK + ".quick_uniprot SET uniprot_identifier_value=%s, uniprot_isoform=%s, uniprot_aliases=%s, uniprot_externalids=%s, uniprot_externalids_types=%s, uniprot_sequence=%s, uniprot_sequence_length=%s, uniprot_name=%s, uniprot_description=%s, uniprot_source=%s, uniprot_version=%s, uniprot_curation_status=%s, uniprot_hasfeatures=%s, uniprot_hasgenes=%s, go_ids_combined=%s, go_names_combined=%s, go_evidence_combined=%s, go_process_ids=%s, go_process_names=%s, go_process_evidence=%s, go_component_ids=%s, go_component_names=%s, go_component_evidence=%s, go_function_ids=%s, go_function_names=%s, go_function_evidence=%s, organism_id=%s, organism_common_name=%s, organism_official_name=%s, organism_abbreviation=%s, organism_strain=%s, uniprot_ordering=%s, uniprot_parent=%s, interaction_count=%s, gene_ids=%s WHERE uniprot_id=%s", tuple(proteinRecord) )
		else :	
			cursor.execute( "INSERT INTO " + Config.DB_QUICK + ".quick_uniprot VALUES( %s )" % sqlFormat, tuple(proteinRecord) )
		
		if 0 == (proteinCount % Config.DB_COMMIT_COUNT ) :
			Database.db.commit( )
			
		proteinRecord = []
	
	Database.db.commit( )
		
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'QUICK_buildUniprot', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )