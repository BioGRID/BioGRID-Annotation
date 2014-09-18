
# Parse UNIPROT XML files and load sequence data
# into the database

import Config
import sys, string
import MySQLdb
import Database
import glob
import os

from gzip import open as gopen
from xml.sax import parse
from classes import UniprotProteinXMLParser, UniprotKB

with Database.db as cursor :

	uniprotKB = UniprotKB.UniprotKB( Database.db, cursor )

	# Simply inactivate these two tables because we want to maintain ids
	# when possible.
	cursor.execute( "UPDATE " + Config.DB_NAME + ".uniprot SET uniprot_status='inactive'" )
	cursor.execute( "UPDATE " + Config.DB_NAME + ".uniprot_features SET uniprot_feature_status='inactive'" )
	
	cursor.execute( "TRUNCATE TABLE " + Config.DB_NAME + ".uniprot_aliases" )
	cursor.execute( "TRUNCATE TABLE " + Config.DB_NAME + ".uniprot_definitions" )
	cursor.execute( "TRUNCATE TABLE " + Config.DB_NAME + ".uniprot_externals" )
	#cursor.execute( "TRUNCATE TABLE " + Config.DB_NAME + ".uniprot_go" )
	
	Database.db.commit( )

	files = [ Config.UP_PROTEINS_DIR + "uniprot_proteins_83333.xml.gz" ]
	for filename in files :
	#for filename in glob.glob( Config.UP_PROTEINS_DIR + "*.gz" ) :

		organismID = filename[filename.rfind( "_" )+1:filename.rfind( ".xml" )]

		with gopen( filename ) as uniprotFile :
			parse( uniprotFile, UniprotProteinXMLParser.UniprotProteinXMLParser( uniprotKB, organismID ) )
		
		Database.db.commit( )
		

	# cursor.execute( "UPDATE " + Config.DB_NAME + ".refseq SET refseq_status='inactive'" )
	# cursor.execute( "TRUNCATE TABLE " + Config.DB_NAME + ".refseq_identifiers" )
	# Database.db.commit( )
	
	# refseq = Refseq.Refseq( Database.db, cursor )
	# accessionHash = refseq.buildAccessionMappingHash( )
	# organismHash = refseq.buildOrganismMappingHash( )
	
	# for filename in glob.glob( Config.PROTEIN_DIR + "*.fasta" ) :
	
		# print "Working on File: " + filename
		
		# sequences = { }
		
		# with open( filename, "r" ) as file : 
			
			# currentInfo = { }
			
			# for line in file.readlines( ) :
				# line = line.strip( )
				
				# Skip Blank Lines
				# if len( line ) <= 0 :
					# continue
				
				# if ">" == line[0] :
					# if len( currentInfo ) > 0 :
						# sequences[currentInfo['ACCESSION']] = currentInfo
						# currentInfo = { }
						
					# splitHeader = line.split( "|" )
					# currentInfo["GI"] = splitHeader[1].strip( )
					# currentInfo["DESC"] = splitHeader[4].strip( )
					# currentInfo["DESC"] = currentInfo["DESC"][:currentInfo["DESC"].rfind( "[" )].strip( )
					# accessionFull = splitHeader[3].strip( ).split( "." )
					# currentInfo["ACCESSION"] = accessionFull[0]
					# currentInfo["VERSION"] = accessionFull[1]
					# currentInfo["SEQUENCE"] = []
					
				# else :
					# currentInfo["SEQUENCE"].append( line.upper( ).strip( ) )
			
			# Load the last sequence from the file
			# if len( currentInfo ) > 0 :
				# sequences[currentInfo['ACCESSION']] = currentInfo
				# currentInfo = { }
					
		# for accession,sequenceInfo in sequences.items( ) :
		
			# sequence = "".join( sequenceInfo["SEQUENCE"] )
			# sequenceLength = len( sequence )
			
			# taxID = organismHash[sequenceInfo["GI"]]
		
			# if accession in accessionHash :
				# cursor.execute( "UPDATE " + Config.DB_NAME + ".refseq SET refseq_gi=%s, refseq_sequence=%s, refseq_length=%s, refseq_description=%s, refseq_version=%s, refseq_modified=NOW( ), refseq_status='active', organism_id=%s WHERE refseq_id=%s", [sequenceInfo['GI'], sequence, sequenceLength, sequenceInfo["DESC"], sequenceInfo["VERSION"], taxID, accessionHash[accession]] )
			# else :
				# cursor.execute( "INSERT INTO " + Config.DB_NAME + ".refseq VALUES( '0', %s, %s, %s, %s, %s, %s, %s, NOW( ), 'active' )", [accession, sequenceInfo["GI"], sequence, sequenceLength, sequenceInfo["DESC"], sequenceInfo["VERSION"], taxID] )
				# accessionHash[accession] = cursor.lastrowid
			
		# Database.db.commit( )
	
	# cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'REFSEQ_parseProteins', NOW( ) )" )
	# Database.db.commit( )
	
sys.exit( )
			