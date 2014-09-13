
# Parse REFSEQ FASTA files and load sequence data
# into the database

import Config
import sys, string
import MySQLdb
import Database
import glob

from classes import Refseq

with Database.db as cursor :
	
	refseq = Refseq.Refseq( Database.db, cursor )
	accessionHash = refseq.buildAccessionMappingHash( )
	
	for filename in glob.glob( Config.PROTEIN_MISSING_DIR + "*.fasta" ) :
	
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
		
			sequence = "".join( sequenceInfo["SEQUENCE"] )
			sequenceLength = len( sequence )
		
			if accession in accessionHash :
				cursor.execute( "UPDATE " + Config.DB_NAME + ".refseq SET refseq_gi=%s, refseq_sequence=%s, refseq_length=%s, refseq_description=%s, refseq_version=%s, refseq_modified=NOW( ), refseq_status='active' WHERE refseq_id=%s", [sequenceInfo['GI'], sequence, sequenceLength, sequenceInfo["DESC"], sequenceInfo["VERSION"], accessionHash[accession]] )
			
		Database.db.commit( )
	
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'REFSEQ_parseMissingProteins', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )
			