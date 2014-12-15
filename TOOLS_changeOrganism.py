# Change the organism ID of existing genes before running
# the update.

import Config
import sys, string
import MySQLdb
import Database
import gzip

from classes import EntrezGene

with Database.db as cursor :

	entrezGene = EntrezGene.EntrezGene( Database.db, cursor )
	organismList = entrezGene.fetchEntrezGeneOrganismMapping( )

	cursor.execute( "SELECT gene_id, gene_source_id FROM " + Config.DB_NAME + ".genes WHERE organism_id=%s", ["10368"] )
	
	geneSet = { }
	for (geneID, geneSourceID) in cursor.fetchall( ) :
		geneSet[str(geneSourceID)] = str(geneID)

	with gzip.open( Config.EG_GENEINFO, 'r' ) as file :
		for line in file.readlines( ) :
			
			line = line.strip( )
			
			# Ignore Header Line
			if "#" == line[0] :
				continue
				
			splitLine = line.split( "\t" )
			entrezGeneTaxID = int(splitLine[0].strip( ))
			sourceID = splitLine[1].strip( )
				
			if str(sourceID) in geneSet :
				taxID = organismList[entrezGeneTaxID]
				cursor.execute( "UPDATE " + Config.DB_NAME + ".genes SET organism_id=%s WHERE gene_id=%s", [taxID, geneSet[str(sourceID)]] )
				print "[" + str(taxID) + "," + str(geneSet[str(sourceID)]) + "]"
				
	Database.db.commit( )
				
sys.exit( )