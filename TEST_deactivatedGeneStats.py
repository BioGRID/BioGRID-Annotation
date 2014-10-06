
# Generate Statistics on Deactivated Genes when
# comparing to the IMS database.

import Config
import sys, string
import MySQLdb
import Database

from classes import Quick

with Database.db as cursor :

	quick = Quick.Quick( Database.db, cursor )
	geneHash = quick.fetchValidGeneIDHash( )
	
	cursor.execute( "SELECT interaction_id, interactor_A_id, interactor_B_id FROM " + Config.DB_IMS + ".interaction_matrix WHERE modification_type='ACTIVATED'" )
	
	deactivatedInteractions = set( )
	deactivatedGenes = set( )
	
	for (interactionID, interactorA, interactorB) in cursor.fetchall( ) :
	
		disableInt = False
		if str(interactorA) not in geneHash :
			deactivatedGenes.add(interactorA)
			disableInt = True
			
		if str(interactorB) not in geneHash :
			deactivatedGenes.add(interactorB)
			disableInt = True
			
		if disableInt :
			deactivatedInteractions.add( interactionID )
			
	print "Number of Deactivated Interactions: " + str( len(deactivatedInteractions) )
	print "Number of Deactivated Genes: " + str( len(deactivatedGenes) )

	sqlFormat = ",".join( ['%s'] * len(deactivatedGenes) )
	cursor.execute( "SELECT gene_id, organism_id, organism_common_name FROM " + Config.DB_OLDQUICK + ".quick_annotation WHERE gene_id IN (%s)" % sqlFormat, tuple(deactivatedGenes) )

	organisms = { }
	for (geneID, organismID, organismCommonName) in cursor.fetchall( ) :
		if organismCommonName not in organisms :
			organisms[organismCommonName] = set( )
		organisms[organismCommonName].add(geneID)

	print "----------------------------------"
	print deactivatedInteractions
	
	print "----------------------------------"
	print deactivatedGenes
	
	print "----------------------------------"
	for (organismName, geneSet) in organisms.items( ) :
		print organismName + " => " + str(len(geneSet))
		print geneSet

sys.exit( )