# Change the ptm_sequence_ids of existing ptms 
# based on processed swap details.

import Config
import sys, string, argparse
import MySQLdb
import Database
import gzip

from classes import EntrezGene

# Process Command Line Input
argParser = argparse.ArgumentParser( description = 'Swap PTMs that were changed from one build to the next.' )
argParser.add_argument( '-f', help = 'Input File', dest = 'inputFile', required=True, action='store' )
inputArgs = vars( argParser.parse_args( ) )

with Database.db as cursor :

	disabledPTMs = set( )
	swappedPTMs = set( )
	duplicatePTMs = set( )
	
	with open( inputArgs['inputFile'], 'r' ) as file :
		for line in file.readlines( ) :
			
			line = line.strip( )
				
			splitLine = line.split( "\t" )
			ptmID = splitLine[0].strip( )
			oldSeqID = splitLine[1].strip( )
			oldLoc = splitLine[2].strip( )
			oldRes = splitLine[3].strip( )
			newSeqID = splitLine[4].strip( )
			newLoc = splitLine[5].strip( )
			newRes = splitLine[6].strip( )
			
			if "DEAD" == newSeqID.upper( ) :
				cursor.execute( "UPDATE " + Config.DB_IMS + ".ptms SET ptm_status='inactive' WHERE ptm_id=%s", [ptmID] )
				disabledPTMs.add( ptmID )
			else :
			
				# GET PUBLICATION ID FROM OLD PTM
				cursor.execute( "SELECT ptm_id, publication_id FROM " + Config.DB_IMS + ".ptms WHERE ptm_id=%s LIMIT 1", [ptmID] )
				ptmInfo = cursor.fetchone( )
				
				# CHECK TO SEE IF BY SWAPPING WE WOULD CREATE A DUPLICATE
				cursor.execute( "SELECT ptm_id FROM " + Config.DB_IMS + ".ptms WHERE refseq_protein_id=%s AND ptm_residue_location=%s AND publication_id=%s LIMIT 1", [newSeqID, newLoc, ptmInfo[1]] )
				ptmTest = cursor.fetchone( )
				
				# IF NO DUPLICATE UPDATE TO NEW DETAILS
				# IF DUPLICATE, JUST DEPRECATE IT
				if None == ptmTest :
					cursor.execute( "UPDATE " + Config.DB_IMS + ".ptms SET refseq_protein_id=%s, ptm_residue_location=%s, ptm_residue=%s WHERE ptm_id=%s", [newSeqID, newLoc, newRes, ptmID] )
					swappedPTMs.add( ptmID )
				else :
					cursor.execute( "UPDATE " + Config.DB_IMS + ".ptms SET ptm_status='inactive' WHERE ptm_id=%s", [ptmID] )
					duplicatePTMs.add( ptmID )
			
			Database.db.commit( )
	
	print "DISABLED  : " + str(len(disabledPTMs)) + " PTMs"
	print "SWAPPED   : " + str(len(swappedPTMs)) +  " PTMs"
	print "DUPLICATE : " + str(len(duplicatePTMs)) +  " PTMs"
	
	Database.db.commit( )
				
sys.exit( )