
# Parse REFSEQ FASTA files and load sequence data
# into the database

import Config
import sys, string, argparse
import MySQLdb
import Database
import glob

from classes import Refseq

# Process Command Line Input
argParser = argparse.ArgumentParser( description = 'Parse a specific protein file.' )
argParser.add_argument( '-f', help = 'Protein File', dest = 'proteinFile', required=True, action='store' )
inputArgs = vars( argParser.parse_args( ) )

filename = inputArgs['proteinFile']

with Database.db as cursor :
	
	refseq = Refseq.Refseq( Database.db, cursor )
	accessionHash = refseq.buildAccessionMappingHash( )
	organismHash = refseq.buildOrganismMappingHash( )
	
	print "Working on File: " + filename
	
	sequences = { }
	
	with open( filename, "r" ) as file : 
		
		currentInfo = { }
		
		for line in file.readlines( ) :
			line = line.strip( )
			
			# Skip Blank Lines
			if len( line ) <= 0 :
				continue
			
			if ">" == line[0] :
				if len( currentInfo ) > 0 :
					sequences[currentInfo['ACCESSION']] = currentInfo
					currentInfo = { }
					
				splitHeader = line.split( "|" )
				currentInfo["GI"] = splitHeader[1].strip( )
				currentInfo["DESC"] = splitHeader[4].strip( )
				currentInfo["DESC"] = currentInfo["DESC"][:currentInfo["DESC"].rfind( "[" )].strip( )
				accessionFull = splitHeader[3].strip( ).split( "." )
				currentInfo["ACCESSION"] = accessionFull[0]
				currentInfo["VERSION"] = accessionFull[1]
				currentInfo["SEQUENCE"] = []
				
			else :
				currentInfo["SEQUENCE"].append( line.upper( ).strip( ) )
		
		# Load the last sequence from the file
		if len( currentInfo ) > 0 :
			sequences[currentInfo['ACCESSION']] = currentInfo
			currentInfo = { }
				
	for accession,sequenceInfo in sequences.items( ) :
	
		accession = accession.strip( )
	
		sequence = "".join( sequenceInfo["SEQUENCE"] )
		sequenceLength = len( sequence )
		
		taxID = organismHash[sequenceInfo["GI"]]
	
		if accession in accessionHash :
			print "UPDATING SEQUENCE"
			cursor.execute( "UPDATE " + Config.DB_NAME + ".refseq SET refseq_gi=%s, refseq_sequence=%s, refseq_length=%s, refseq_description=%s, refseq_version=%s, refseq_modified=NOW( ), refseq_status='active', organism_id=%s WHERE refseq_id=%s", [sequenceInfo['GI'], sequence, sequenceLength, sequenceInfo["DESC"], sequenceInfo["VERSION"], taxID, accessionHash[accession]] )
		else :
			print "INSERTING NEW SEQUENCE"
			cursor.execute( "INSERT INTO " + Config.DB_NAME + ".refseq VALUES( '0', %s, %s, %s, %s, %s, %s, %s, NOW( ), 'active' )", [accession, sequenceInfo["GI"], sequence, sequenceLength, sequenceInfo["DESC"], sequenceInfo["VERSION"], taxID] )
			accessionHash[accession] = cursor.lastrowid
		
	Database.db.commit( )
	
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'REFSEQ_parseProteins', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )
			