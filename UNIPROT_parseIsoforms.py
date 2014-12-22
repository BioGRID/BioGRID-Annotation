
# Parse UNIPROT FASTA file and load sequence data
# into the database

import Config
import sys, string
import MySQLdb
import Database
import re

from gzip import open as gopen
from classes import UniprotKB

descRE = re.compile( '^([A-Z0-9]+_{1}[A-Z0-9]+) (.*?) (OS=.*?)? (GN=(.*?))?$', re.VERBOSE )

with Database.db as cursor :

	cursor.execute( "UPDATE " + Config.DB_NAME + ".uniprot_isoforms SET uniprot_isoform_status='inactive'" )
	Database.db.commit( )

	uniprotKB = UniprotKB.UniprotKB( Database.db, cursor )
	accessionHash = uniprotKB.buildAccessionHash( )
	organismHash = uniprotKB.buildOrganismHash( )
	
	with gopen( Config.UP_ISOFORMS ) as file :
			
		currentInfo = { }
			
		for line in file.readlines( ) :
			line = line.strip( )
				
			# Skip Blank Lines
			if len( line ) <= 0 :
				continue
				
			if ">" == line[0] :
				if len( currentInfo ) > 0 :
										
					if currentInfo["ACCESSION"] in accessionHash :
						uniprotID = accessionHash[currentInfo["ACCESSION"]]
						organismID = organismHash[uniprotID]
					
						uniprotKB.processIsoform( uniprotID, organismID, currentInfo )
					
					currentInfo = { }
						
				splitHeader = line.split( "|" )
				splitAccession = splitHeader[1].split( "-" )
				
				currentInfo["ACCESSION"] = splitAccession[0].strip( )
				currentInfo["ISOFORM"] = splitAccession[1].strip( )
				
				descMatches = re.search( descRE, splitHeader[2] )
				currentInfo["NAME"] = (descMatches.group(1)).strip( )
				currentInfo["DESC"] = (descMatches.group(2)).strip( )
				
				if None != descMatches.group(5) :
					currentInfo["GENE"] = (descMatches.group(5)).strip( )
				else :
					currentInfo["GENE"] = ""
				
				currentInfo["SEQUENCE"] = []
					
			else :
				currentInfo["SEQUENCE"].append( line.upper( ).strip( ) )
			
		# Load the last sequence from the file
		if len( currentInfo ) > 0 :
			if currentInfo["ACCESSION"] in accessionHash :
				uniprotID = accessionHash[currentInfo["ACCESSION"]]
				organismID = organismHash[uniprotID]
					
				uniprotKB.processIsoform( uniprotID, organismID, currentInfo )
	
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'UNIPROT_parseIsoforms', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )
			