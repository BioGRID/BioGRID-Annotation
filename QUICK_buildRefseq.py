
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
argGroup.add_argument( '-r', dest='refseqID', type = int, nargs = 1, help = 'A Refseq ID to Update', action='store' )
argGroup.add_argument( '-all', dest='allRecords', help = 'Build from All Records, Starting from Scratch', action='store_true' )
inputArgs = vars( argParser.parse_args( ) )

isOrganism = False
isRefseq = False
isAll = False

if None != inputArgs['organismID'] :
	isOrganism = True
elif None != inputArgs['refseqID'] :
	isRefseq = True
else :
	isAll = True

with Database.db as cursor :

	quick = Quick.Quick( Database.db, cursor )
	orgHash = quick.fetchRefseqOrganismHash( )
	
	if isOrganism :
		cursor.execute( "SELECT * FROM " + Config.DB_NAME + ".refseq WHERE organism_id=%s AND refseq_status='active'", [inputArgs['organismID']] )
	
	elif isRefseq :
		cursor.execute( "SELECT * FROM " + Config.DB_NAME + ".refseq WHERE refseq_id=%s AND refseq_status='active'", [inputArgs['refseqID']] )
	
	else :
		cursor.execute( "TRUNCATE TABLE " + Config.DB_QUICK + ".quick_refseq" )
		Database.db.commit( )
		
		cursor.execute( "SELECT * FROM " + Config.DB_NAME + ".refseq WHERE refseq_status='active' ORDER BY refseq_id ASC" )
	
	proteinCount = 0
	for row in cursor.fetchall( ) :
	
		proteinCount = proteinCount + 1
		print "Working on: " + str(proteinCount)
	
		proteinRecord = []
		proteinID = str(row[0])
		proteinType = "REFSEQ"
		
		proteinRecord.append( proteinID )
		proteinDetails = row
		
		genes = "-"
		uniprots = "-"
		officialSymbol = "-"
		proteinOrder = 1
		proteinParent = 0
		
		aliases = []
		externalIDs = []
		externalTypes = []
		
		proteinMiddle = []
		
		if proteinDetails :
		
			organismIndex = 7
			accession = proteinDetails[1]
			gi = proteinDetails[2]
			
			# Get actual GENE IDs for the Entrez Gene IDs
			geneID = str(quick.fetchGeneIDByRefseqID( proteinID ))
			
			# Get Uniprot IDs
			uniprotIDs = quick.fetchUniprotIDs( [proteinID] )
			
			if len(uniprotIDs) > 0 :
				uniprots = "|".join(uniprotIDs)
			
			# Add Sequence Details
			proteinRecord.extend( [accession, gi, proteinDetails[3], proteinDetails[4], proteinDetails[5], proteinDetails[6]] )
			
			# Get curation status
			curationStatus = quick.fetchCurationStatus( geneID, proteinID )
			proteinRecord.append( curationStatus )
			
			# ORDERING
			proteinRecord.append( "1" )
			
			# Get Refseq Aliases
			systematicName, aliases = quick.fetchAliases( geneID, accession )
			
			if systematicName != "-" :
				if systematicName not in aliases :
					aliases.append( systematicName )
			
			if len(aliases) > 0 :
				proteinRecord.append( "|".join(aliases) )
			else :
				proteinRecord.append( "-" )
			
			# Get Uniprot Aliases
			uniprotAliases = []
			for uniprotID in uniprotIDs :
				aliasSet = quick.fetchUniprotAliases( uniprotID, [], accession )
				uniprotAliases.extend(aliasSet)
			
			if len(uniprotAliases) > 0 :
				proteinRecord.append( "|".join(uniprotAliases) )
			else :
				proteinRecord.append( "-" )
			
			# Get External IDs and Types
			geneExternals, geneExternalTypes = quick.fetchExternals( geneID, [proteinID] )
			
			if len(geneExternals) > 0 :
				proteinRecord.append( "|".join( geneExternals ))
				proteinRecord.append( "|".join( geneExternalTypes ))
			else :
				proteinRecord.append( "-" )
				proteinRecord.append( "-" )
			
			# Get organism info out of the hash
			(orgID, orgTaxID, orgName, orgOfficial, orgAbbr, orgStrain) = orgHash[str(proteinDetails[organismIndex])]
			proteinRecord.extend( [str(orgID), orgName, orgOfficial, orgAbbr, orgStrain] )
			
			# Tack on final details
			proteinRecord.extend( [geneID, uniprots, "0", "0"] )
			
			sqlFormat = ",".join( ['%s'] * len(proteinRecord) )
			
			if isRefseq or isOrganism :
				cursor.execute( "SELECT refseq_id FROM " + Config.DB_QUICK + ".quick_refseq WHERE refseq_id=%s LIMIT 1", [proteinID] )
				proteinExists = cursor.fetchone( )
				
				if None == proteinExists :
					cursor.execute( "INSERT INTO " + Config.DB_QUICK + ".quick_refseq VALUES( %s )" % sqlFormat, tuple(proteinRecord) )
				else :
					proteinRecord.pop(0)
					proteinRecord.append( proteinID )
					cursor.execute( "UPDATE " + Config.DB_QUICK + ".quick_refseq SET refseq_accession=%s, refseq_gi=%s, refseq_sequence=%s, refseq_length=%s, refseq_description=%s, refseq_version=%s, refseq_curation_status=%s, refseq_ordering=%s, refseq_aliases=%s, refseq_uniprot_aliases=%s, refseq_externalids=%s, refseq_externalids_types=%s, organism_id=%s, organism_common_name=%s, organism_official_name=%s, organism_abbreviation=%s, organism_strain=%s, gene_id=%s, uniprot_ids=%s, refseq_parent=%s, interaction_count=%s WHERE refseq_id=%s", tuple(proteinRecord) )
			else :	
				cursor.execute( "INSERT INTO " + Config.DB_QUICK + ".quick_refseq VALUES( %s )" % sqlFormat, tuple(proteinRecord) )
			
			if 0 == (proteinCount % Config.DB_COMMIT_COUNT ) :
				Database.db.commit( )
			
		proteinRecord = []
	
	Database.db.commit( )
		
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'QUICK_buildUniprot', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )