
# Parse annotation from CGD and use it to
# supplement and fix the data already in place from
# entrez gene.

# NOTE: THIS FILE WILL LIKELY NEED HEAVY MODIFICATION
# ON SUBSEQUENT UPDATES. CGD DOES NOT MAINTAIN A CONSISTENT
# FILE DUMP PROCESS.

import Config
import sys, string
import MySQLdb
import Database
import gzip

from classes import ModelOrganisms

with Database.db as cursor :

	# Deactivate Candida Albicans Genes
	cursor.execute( "UPDATE " + Config.DB_NAME + ".genes SET gene_status='inactive' WHERE organism_id='237561'" )
	cursor.execute( "UPDATE " + Config.DB_NAME + ".gene_aliases SET gene_alias_status='inactive' WHERE gene_id IN (SELECT gene_id FROM " + Config.DB_NAME + ".genes WHERE organism_id='237561')" )

	cgd = ModelOrganisms.ModelOrganisms( Database.db, cursor )
	cgdAliasHash = cgd.buildCGDAliasHash( )
	
	cgdFileMapping = { }
	cgdAliasList = { }
	with open( Config.CGD_FEATURES, 'r' ) as file :
		for line in file.readlines( ) :
			
			line = line.strip( )
			
			if line[0] == "!" :
				continue
			
			splitLine = line.split( "\t" )
			featureName = splitLine[0].strip( )
			geneName = splitLine[1].strip( )
			aliases = (splitLine[2].strip( )).split( "|" )
			featureType = (splitLine[3].strip( )).split( "|" )
			description = splitLine[10].strip( )
			cgdID = splitLine[8].strip( )
			alternateCGDID = splitLine[9].strip( )
			
			altFeatureName = featureName
			if featureName[:3].lower( ) == "cao" :
				altFeatureName = "orf" + featureName[3:].lower( )
			elif featureName[:3].lower( ) == "orf" :
				altFeatureName = "cao" + featureName[3:].lower( )
			
			# File contains numerous duplicates, instead, we
			# run through the file and build an array which attempts
			# to distil down to just the core set of references we are
			# interested in and combines the various identifiers into
			# a single entry for later processing.
			
			if featureName.lower( ) not in cgdAliasList and altFeatureName.lower( ) not in cgdAliasList :
				cgdFileMapping[featureName] = { "FEATURE" : featureName, "GENE" : geneName, "DESC" : description, "CGD" : set( ), "ALT_CGD" : set( ), "ALIASES" : aliases, "GENE_ID" : "", "ALT_GENES" : set( ), "TYPE" : featureType[0] }
				cgdFileMapping[featureName]["CGD"] = cgdID
				
				if len( alternateCGDID ) > 0 :
					cgdFileMapping[featureName]["ALT_CGD"].add( alternateCGDID )
				
				cgdAliasList[featureName.lower( )] = featureName
				
				if altFeatureName.lower( ) != featureName.lower( ) :
					cgdAliasList[altFeatureName] = featureName
					cgdFileMapping[featureName]["ALIASES"].append( altFeatureName )
				
				addonAliases = []
				for alias in aliases :
					alias = alias.strip( )
					
					if alias[:3].lower( ) == "cao" :
						addonAliases.append( "orf" + alias[3:] )
					elif alias[:3].lower( ) == "orf" :
						addonAliases.append( "CaO" + alias[3:] )
					
					if len(alias) > 0 and alias.lower( ) not in cgdAliasList :
					
						if alias[:3].lower( ) == "cao" :
							altAlias = "orf" + alias[3:].lower( )
							if altAlias not in cgdAliasList :
								cgdAliasList[altAlias] = featureName
						elif alias[:3].lower( ) == "orf" :
							altAlias = "cao" + alias[3:].lower( )
							if altAlias not in cgdAliasList :
								cgdAliasList["cao" + alias[3:].lower( )] = featureName
							
						cgdAliasList[alias.lower( )] = featureName
					
				cgdFileMapping[cgdAliasList[featureName.lower( )]]["ALIASES"] = cgdFileMapping[cgdAliasList[featureName.lower( )]]["ALIASES"] + addonAliases
			else :
				cgdFileMapping[cgdAliasList[featureName.lower( )]]["ALIASES"] = cgdFileMapping[cgdAliasList[featureName.lower( )]]["ALIASES"] + aliases
				cgdFileMapping[cgdAliasList[featureName.lower( )]]["ALT_CGD"].add( cgdID )
				
				if len( alternateCGDID ) > 0 :
					cgdFileMapping[cgdAliasList[featureName.lower( )]]["ALT_CGD"].add( alternateCGDID )
					
	cursor.execute( "SELECT gene_id, gene_alias_value FROM " + Config.DB_NAME + ".gene_aliases WHERE gene_id IN ( SELECT gene_id FROM " + Config.DB_NAME + ".genes WHERE organism_id='237561' ) and gene_alias_type='ordered locus' ORDER BY gene_id ASC" )
	
	# Map GENE IDs and Secondary GENE IDs
	for row in cursor.fetchall( ) :
		if row[1].lower( ) in cgdAliasList :
			featureName = cgdAliasList[row[1].lower( )]
			if cgdFileMapping[featureName]["GENE_ID"] == "" :
				cgdFileMapping[featureName]["GENE_ID"] = str(row[0])
			else :
				cgdFileMapping[featureName]["ALT_GENES"].add( str(row[0]) )
			
	for featureName, cgdMapping in cgdFileMapping.items( ) :
	
		officialSymbol = cgdMapping["FEATURE"]
		if "" != cgdMapping["GENE"] :
			officialSymbol = cgdMapping["GENE"]
	
		geneID = "none"
		if cgdMapping["GENE_ID"] != "" :
			# Update matching record in genes table
			cursor.execute( "UPDATE " + Config.DB_NAME + ".genes SET gene_status='active' WHERE gene_id=%s", [cgdMapping["GENE_ID"]] )
			geneID = cgdMapping["GENE_ID"]
		else :
			# Add as a separate record
			
			geneType = cgdMapping["TYPE"]
			if "" == geneType :
				geneType = "-"
			elif "orf" == geneType.lower( ) :
				geneType = "protein-coding"
			elif "autocatalytically_spliced_intron" == geneType.lower( ) :
				geneType = "spliced_intron"
			
			cursor.execute( "INSERT INTO " + Config.DB_NAME + ".genes VALUES( '0', %s, 'cgd-official', %s, %s, '237561', 'active', NOW( ), NOW( ), 'CGD', '0' )", [officialSymbol, cgdMapping["CGD"], geneType] )
			geneID = cursor.lastrowid
		
		if geneID != "none" :

			cgd.processName( geneID, cgdMapping["FEATURE"], officialSymbol, "cgd-official", set(cgdMapping["ALIASES"]) )
			cgd.processDefinition( geneID, cgdMapping["DESC"], "CGD-DESCRIPTION" )
			cgd.processExternals( geneID, set([cgdMapping["CGD"]]), "CGD" )
			cgd.processExternals( geneID, cgdMapping["ALT_CGD"], "CGD" )
			
			for altGeneID in cgdMapping["ALT_GENES"] :
				altGeneID = altGeneID.strip( )
				if "" != altGeneID :
					cursor.execute( "SELECT gene_source_id FROM " + Config.DB_NAME + ".genes WHERE gene_id=%s", [altGeneID] )
					
					row = cursor.fetchone( )
					
					if None != row :
						cgd.processExternals( geneID, set([row[0]]), "ENTREZ_GENE" )
						cgd.processExternals( geneID, set([row[0]]), "ENTREZ_GENE_ETG" )
						
		Database.db.commit( )
				
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'CGD_fixAnnotation', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )
			