
# Parse annotation from WORMBASE and use it to
# supplement the data already in place from
# entrez gene.

import Config
import sys, string
import MySQLdb
import Database
import gzip

from classes import ModelOrganisms

with Database.db as cursor :

	wormbase = ModelOrganisms.ModelOrganisms( Database.db, cursor )
	wormbaseIDHash = wormbase.buildWormbaseLocusIDHash( )
	
	annotationSet = { }
	
	foundCount = 0
	with gzip.open( Config.WORMBASE_DESC, 'r' ) as file :
		for line in file.readlines( ) :
			
			line = line.strip( )
			
			if "#" == line[0] :
				continue
			
			splitLine = line.split( "\t" )
			
			if len(splitLine) != 7 :
				continue
			
			wormbaseID = splitLine[0].strip( )
			officialSymbol = splitLine[1].strip( )
			systematicName = splitLine[2].strip( )
			definition = splitLine[3].strip( )
			provisionalDesc = splitLine[4].strip( )
			detailedDesc = splitLine[5].strip( )
			classDesc = splitLine[6].strip( )
			
			if systematicName in wormbaseIDHash :
				annotationSet[wormbaseIDHash[systematicName]] = { "WBID" : wormbaseID, "OFFICIAL" : officialSymbol, "SYSTEMATIC" : systematicName, "DEFINITION" : definition, "CLASSDESC" : classDesc, "GENEID" : wormbaseIDHash[systematicName], "ALIASES" : set( ) }
	
	with gzip.open( Config.WORMBASE_OTHER, 'r' ) as file :
		for line in file.readlines( ) :
			
			line = line.strip( )
			splitLine = line.split( "\t" )
			
			wormbaseID = splitLine[0].strip( )
			status = splitLine[1].strip( )
			
			if "LIVE" == status.upper( ) and len(splitLine) > 2 :
				systematicName = splitLine[2].strip( )
				
				if systematicName in wormbaseIDHash :
					geneID = wormbaseIDHash[systematicName]
					if geneID in annotationSet :
						for alias in splitLine[2:] :
							if alias.upper( ) != annotationSet[geneID]["SYSTEMATIC"].upper( ) and alias.upper( ) != annotationSet[geneID]["OFFICIAL"].upper( ) :
								annotationSet[geneID]["ALIASES"].add( alias )
	
	for (geneID,annotationDetails) in annotationSet.items( ) :
	
		systematicName = annotationDetails["SYSTEMATIC"]
		if "" == systematicName or "none available" == systematicName.lower( ) or "not known" == systematicName.lower( ) :
			systematicName = ""
			
		officialSymbol = annotationDetails["OFFICIAL"]
		if "" == officialSymbol or "none available" == officialSymbol.lower( ) or "not known" == officialSymbol.lower( ) :
			officialSymbol = ""
			
		aliases = annotationDetails["ALIASES"]
			
		wormbase.processName( geneID, systematicName, officialSymbol, "wormbase-official", aliases )
		
		if "" != annotationDetails["DEFINITION"] and "none available" != annotationDetails["DEFINITION"].lower( ) and "not known" != annotationDetails["DEFINITION"].lower( ) :
			wormbase.processDefinition( geneID, annotationDetails["DEFINITION"], "WORMBASE-DESCRIPTION" )
		
		if "" != annotationDetails["CLASSDESC"] and "none available" != annotationDetails["CLASSDESC"].lower( ) and "not known" != annotationDetails["CLASSDESC"].lower( ) :
			wormbase.processDefinition( geneID, annotationDetails["CLASSDESC"], "WORMBASE-CLASS" )
			
		if "" != annotationDetails["WBID"] and "none available" != annotationDetails["WBID"].lower( ) and "not known" != annotationDetails["WBID"].lower( ) :
			wormbase.processExternals( geneID, [annotationDetails["WBID"]], "WORMBASE" )
			
	cursor.execute( "SELECT quick_identifier_value, gene_id FROM " + Config.DB_OLDQUICK + ".quick_identifiers WHERE organism_id='6239' AND quick_identifier_type='WORMBASE'" )		
	
	for (idValue, geneID) in cursor.fetchall( ) :
		wormbase.processExternals( geneID, [idValue], "WORMBASE" )
		
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'WORMBASE_parseGenes', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )
			