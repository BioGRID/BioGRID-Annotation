
# Create the quick lookup gene annotation
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
argGroup.add_argument( '-g', dest='geneID', type = int, nargs = 1, help = 'A Gene ID to Update', action='store' )
argGroup.add_argument( '-all', dest='allRecords', help = 'Build from All Records, Starting from Scratch', action='store_true' )
inputArgs = vars( argParser.parse_args( ) )

isOrganism = False
isGene = False
isAll = False

if None != inputArgs['organismID'] :
	isOrganism = True
elif None != inputArgs['geneID'] :
	isGene = True
else :
	isAll = True

with Database.db as cursor :

	quick = Quick.Quick( Database.db, cursor )
	orgHash = quick.fetchOrganismHash( )

	if isOrganism :
		cursor.execute( "SELECT * FROM " + Config.DB_NAME + ".genes WHERE organism_id=%s AND gene_status='active'", [inputArgs['organismID']] )
	
	elif isGene :
		cursor.execute( "SELECT * FROM " + Config.DB_NAME + ".genes WHERE gene_id=%s AND gene_status='active'", [inputArgs['geneID']] )
	
	else :
		cursor.execute( "TRUNCATE TABLE " + Config.DB_QUICK + ".quick_annotation" )
		Database.db.commit( )
		
		cursor.execute( "SELECT * FROM " + Config.DB_NAME + ".genes WHERE gene_status='active' ORDER BY gene_id ASC" )
	
	insertCount = 0
	for row in cursor.fetchall( ) :
	
		geneRecord = []
	
		geneID = str(row[0])
		geneRecord.append( geneID )
		
		officialSymbol = str(row[1]).strip( )
		
		# Build | delimited set of Refseq IDs
		refseqIDs = quick.fetchRefseqIDs( geneID )
		
		refseq = "-"
		if len(refseqIDs) > 0 :
			refseq = "|".join(refseqIDs)
		
		# Build | delimited Set of Uniprot IDs
		uniprotIDs = quick.fetchUniprotIDs( refseqIDs )
		
		uniprot = "-"
		if len(uniprotIDs) > 0 :
			uniprot = "|".join(uniprotIDs)
		
		# Grab all aliases and a systematic name (if applicable)
		systematicName, aliases = quick.fetchAliases( geneID, officialSymbol )
		
		if len( aliases ) <= 0 :
			aliases = "-"
		else :
			aliases = "|".join(aliases)
			
		uniprotAliases, uniprotExternals, uniprotExternalTypes = quick.fetchUniprotNamesForGenes( uniprotIDs )
		
		if len( uniprotAliases ) <= 0 :
			uniprotAliases = "-"
		else :
			uniprotAliases = "|".join(uniprotAliases)
			
		geneRecord.extend( [systematicName, officialSymbol, aliases] )
			
		# Grab the best description if available
		description = quick.fetchDescription( geneID, refseqIDs )
		geneRecord.extend( [description, len(description)] )
		
		# Grab external Info
		externalIDs, externalTypes = quick.fetchExternals( geneID, refseqIDs )
		externalIDs = externalIDs + uniprotExternals
		externalTypes = externalTypes + uniprotExternalTypes

		if len( externalIDs ) <= 0 :
			externalIDs = "-"
			externalTypes = "-"
		else :
			externalIDs = "|".join(externalIDs)
			externalTypes = "|".join(externalTypes)
		
		geneRecord.extend( [externalIDs,externalTypes] )
		
		# Additional Gene Info
		geneRecord.append( str(row[4]) ) # Gene Type
		geneRecord.append( str(row[9]) ) # Gene Source
		
		# GRAB Gene Ontology Details
		goProcess, goComponent, goFunction = quick.fetchGO( geneID, "GENE" )
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
			
		geneRecord.extend( [goCombined["IDS"], goCombined["NAMES"], goCombined["EVIDENCE"]] )
		geneRecord.extend( [goProcess["IDS"], goProcess["NAMES"], goProcess["EVIDENCE"]] )
		geneRecord.extend( [goComponent["IDS"], goComponent["NAMES"], goComponent["EVIDENCE"]] )
		geneRecord.extend( [goFunction["IDS"], goFunction["NAMES"], goFunction["EVIDENCE"]] )
		
		# Get organism info out of the hash
		(orgID, orgTaxID, orgName, orgOfficial, orgAbbr, orgStrain) = orgHash[str(row[5])]
		geneRecord.extend( [str(orgID), orgName, orgOfficial, orgAbbr, orgStrain] )
		
		# Uniprot IDs
		geneRecord.append( uniprot )
		
		# Uniprot Aliases 
		geneRecord.append( uniprotAliases )
		
		# Refseq IDs
		geneRecord.append( refseq )
		
		# Interaction Count
		geneRecord.append( "0" )
		
		sqlFormat = ",".join( ['%s'] * len(geneRecord) )
	
		if isGene or isOrganism :
			cursor.execute( "SELECT gene_id FROM " + Config.DB_QUICK + ".quick_annotation WHERE gene_id=%s LIMIT 1", [geneID] )
			geneExists = cursor.fetchone( )
			
			if None == geneExists :
				cursor.execute( "INSERT INTO " + Config.DB_QUICK + ".quick_annotation VALUES (%s)" % sqlFormat, tuple(geneRecord) )
			else :
				geneRecord.pop(0)
				geneRecord.append( geneID )
				cursor.execute( "UPDATE " + Config.DB_QUICK + ".quick_annotation SET systematic_name=%s, official_symbol=%s, aliases=%s, definition=%s, definition_length=%s, external_ids=%s, external_ids_types=%s, gene_type=%s, gene_source=%s, go_ids_combined=%s, go_names_combined=%s, go_evidence_combined=%s, go_process_ids=%s, go_process_names=%s, go_process_evidence=%s, go_component_ids=%s, go_component_names=%s, go_component_evidence=%s, go_function_ids=%s, go_function_names=%s, go_function_evidence=%s, organism_id=%s, organism_common_name=%s, organism_official_name=%s, organism_abbreviation=%s, organism_strain=%s, uniprot_ids=%s, uniprot_aliases=%s, refseq_ids=%s, interaction_count=%s WHERE gene_id=%s", tuple(geneRecord) )
			
		else :
			cursor.execute( "INSERT INTO " + Config.DB_QUICK + ".quick_annotation VALUES (%s)" % sqlFormat, tuple(geneRecord) )
	
		
		insertCount = insertCount + 1
		
		if 0 == (insertCount % Config.DB_COMMIT_COUNT ) :
			Database.db.commit( )
			
	Database.db.commit( )
	
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'QUICK_buildAnnotation', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )