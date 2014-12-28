
# Generate Statistics on Genes and whether or
# not they have a new organism in the latest 
# entrez gene release.

import Config
import sys, string, gzip
import MySQLdb
import Database

from classes import EntrezGene

with Database.db as cursor :

	entrezGene = EntrezGene.EntrezGene( Database.db, cursor )
	organismList = entrezGene.fetchEntrezGeneOrganismMapping( )
	orgMapping = entrezGene.fetchEntrezGeneToOrganismMapping( )
	
	missingOrgs = set( )
	fineCount = 0
	changeCount = 0
	missingCount = 0
	with gzip.open( Config.EG_GENEINFO, 'r' ) as file :
		for line in file.readlines( ) :
		
			line = line.strip( )
			
			# Ignore Header Line
			if "#" == line[0] :
				continue
				
			splitLine = line.split( "\t" )
			entrezGeneTaxID = int(splitLine[0].strip( ))
			sourceID = splitLine[1].strip( )
			
			# If it's an Entrez Gene 
			# we have already
			if str(sourceID) in orgMapping :
				(organismID, geneID) = orgMapping[sourceID]
				
				# If organism we want
				if entrezGeneTaxID in organismList :
					taxID = organismList[entrezGeneTaxID]
					
					# Check to see if organism is same
					if str(taxID) == str(organismID) :
						# Same, no changes needed
						fineCount = fineCount + 1
					else :
						# Different, we can safely switch
						# because we already have the new
						# organism defined.
						cursor.execute( "UPDATE " + Config.DB_NAME + ".genes SET organism_id=%s WHERE gene_id=%s", [taxID, geneID] )
						Database.db.commit( )
						changeCount = changeCount + 1
						
				else :
					# Not one we currently want, add to missing list
					missingCount = missingCount + 1
					missingOrgs.add(entrezGeneTaxID)
					
	print "Total Fine: " + str(fineCount)
	print "Total Changed: " + str(changeCount)
	print "Number of Missing Orgs: " + str(missingCount)
	print missingOrgs
					
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'EG_updateOrganisms', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )
					
			
					