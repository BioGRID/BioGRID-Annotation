
# Create the quick lookup gene annotation
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

	cursor.execute( "TRUNCATE TABLE " + Config.DB_QUICK + ".quick_annotation" )
	Database.db.commit( )
	
	cursor.execute( "SELECT * FROM " + Config.DB_NAME + ".genes WHERE gene_status='active'" )
	
	insertCount = 0
	for row in cursor.fetchall( ) :
	
		geneRecord = []
	
		geneID = str(row[0])
		geneRecord.append( geneID )
		
		officialSymbol = str(row[1]).strip( )
		refseqIDs = quick.fetchRefseqIDs( geneID )
		uniprotIDs = quick.fetchUniprotIDs( refseqIDs )
		
		# Grab all aliases and a systematic name (if applicable)
		systematicName, aliases = quick.fetchAliases( geneID, officialSymbol )
		uniprotAliases, uniprotExternals, uniprotExternalTypes = quick.fetchUniprotNamesForGenes( uniprotIDs )
		
		aliases = set( aliases + uniprotAliases )
		
		if len( aliases ) <= 0 :
			aliases = "-"
		else :
			aliases = "|".join(aliases)
			
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
		goProcess, goComponent, goFunction = quick.fetchGO( geneID )
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
		(orgID, orgEntrezID, orgUniprotID, orgName, orgOfficial, orgAbbr, orgStrain) = orgHash[str(row[5])]
		geneRecord.extend( [str(orgID), orgName, orgOfficial, orgAbbr, orgStrain] )
		
		# Interaction Count
		geneRecord.append( "0" )
		
		sqlFormat = ",".join( ['%s'] * len(geneRecord) )
		cursor.execute( "INSERT INTO " + Config.DB_QUICK + ".quick_annotation VALUES (%s)" % sqlFormat, tuple(geneRecord) )
		insertCount = insertCount + 1
		
		if 0 == (insertCount % Config.DB_COMMIT_COUNT ) :
			Database.db.commit( )
			
	Database.db.commit( )
	
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'QUICK_buildAnnotation', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )