
# Parse annotation from SGD and use it to
# supplement the data already in place from
# entrez gene.

import Config
import sys, string
import MySQLdb
import Database
import gzip

from classes import ModelOrganisms

with Database.db as cursor :

	sgd = ModelOrganisms.ModelOrganisms( Database.db, cursor )
	sgdIDHash = sgd.buildSGDIDHash( )
	
	with open( Config.SGD_FEATURES, 'r' ) as file :
		for line in file.readlines( ) :
			
			line = line.strip( )
			
			splitLine = line.split( "\t" )
			sgdID = splitLine[0].strip( )
			sgdType = splitLine[1].strip( )
			orfName = splitLine[3].strip( )
			
			#if "LTR_RETROTRANSPOSON" == sgdType.upper( ) :
				#print splitLine
			
			geneID = "none"
			if sgdID not in sgdIDHash :
				if "LTR_RETROTRANSPOSON" == sgdType.upper( ) :
					cursor.execute( "INSERT INTO " + Config.DB_NAME + ".genes VALUES( '0', %s, 'ordered locus', %s, 'retrotransposon', '559292', 'active', NOW( ), NOW( ), 'SGD', '0' )", [orfName, sgdID] )
					Database.db.commit( )
					geneID = str(cursor.lastrowid)
					
					cursor.execute( "INSERT INTO " + Config.DB_NAME + ".gene_externals VALUES ('0',%s,'SGD','active',NOW( ), %s)", [sgdID,geneID] )
					Database.db.commit( )
			else :
			
				# Process Addon Annotation
				geneID = sgdIDHash[sgdID]
				
			if geneID != "none" :
			
				if "LTR_RETROTRANSPOSON" == sgdType.upper( ) :
					cursor.execute( "UPDATE " + Config.DB_NAME + ".genes SET gene_updated = NOW( ) WHERE gene_id=%s", [geneID] )
					Database.db.commit( )
			
				officialSymbol = splitLine[4].strip( )
				aliases = (splitLine[5].strip( )).split( "|" )
				additionalSGDIDs = (splitLine[7].strip( )).split( "|" )
				definition = splitLine[15].strip( )
					
				sgd.processName( geneID, orfName, officialSymbol, "sgd-official", aliases )
				sgd.processAddonSGDIDs( geneID, additionalSGDIDs )
				sgd.processDefinition( geneID, definition, "SGD-DESCRIPTION" )
				
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'SGD_parseGenes', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )
			