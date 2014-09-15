
# Parse annotation from POMBASE and use it to
# supplement the data already in place from
# entrez gene.

import Config
import sys, string
import MySQLdb
import Database
import gzip

from classes import ModelOrganisms

with Database.db as cursor :

	pombase = ModelOrganisms.ModelOrganisms( Database.db, cursor )
	pombaseIDHash = pombase.buildPombaseIDHash( )
	
	with open( Config.POMBASE_FEATURES, 'r' ) as file :
		for line in file.readlines( ) :
			
			line = line.strip( )
			
			splitLine = line.split( "\t" )
			pombaseID = splitLine[0].strip( )
			primaryName = splitLine[1].strip( )
			aliases = (splitLine[2].strip( )).split( "," )
			definition = splitLine[3].strip( )
			
			if pombaseID in pombaseIDHash :
				geneID = pombaseIDHash[pombaseID]
				
				pombase.processName( geneID, pombaseID, primaryName, "pombase-official", aliases )
				pombase.processDefinition( geneID, definition, "POMBASE-DESCRIPTION" )
				
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'POMBASE_parseGenes', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )
			