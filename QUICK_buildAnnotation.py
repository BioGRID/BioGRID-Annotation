
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
	
	cursor.execute( "SELECT * FROM " + Config.DB_NAME + ".genes WHERE gene_status='active' AND organism_id='7227' LIMIT 50" )
	
	for row in cursor.fetchall( ) :
	
		geneRecord = []
	
		geneID = str(row[0])
		geneRecord.append( geneID )
		
		officialSymbol = str(row[1]).strip( )
		refseqIDs = quick.fetchRefseqIDs( geneID )
		
		# Grab all aliases and a systematic name (if applicable)
		systematicName, aliases = quick.fetchAliases( geneID, officialSymbol )
		
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
		
		# Get organism info out of the hash
		(orgID, orgEntrezID, orgUniprotID, orgName, orgOfficial, orgAbbr, orgStrain) = orgHash[str(row[5])]
		geneRecord.extend( [str(orgID), orgName, orgOfficial, orgAbbr, orgStrain] )
		
		print geneRecord
		print "----------------------------"