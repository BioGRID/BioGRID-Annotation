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
				cursor.execute( "UPDATE " + Config.DB_IMS + ".ptms SET refseq_protein_id=%s, ptm_residue_location=%s, ptm_residue=%s WHERE ptm_id=%s", [newSeqID, newLoc, newRes, ptmID] )
				swappedPTMs.add( ptmID )
			
			Database.db.commit( )
	
	print "DISABLED : " + str(len(disabledPTMs)) + " PTMs"
	print "SWAPPED  : " + str(len(swappedPTMs)) +  " PTMs"
	
	Database.db.commit( )
				
sys.exit( )