
# Parse the Uniprot/Refseq collab file to create
# a mapping table between similar proteins.

import Config
import sys, string
import MySQLdb
import Database

from gzip import open as gopen
from classes import UniprotKB, Refseq

with Database.db as cursor :
	
	uniprotKB = UniprotKB.UniprotKB( Database.db, cursor )
	refseq = Refseq.Refseq( Database.db, cursor )
	
	refseqHash = refseq.buildFullRefseqMappingHash( )
	uniprotHash = uniprotKB.buildAccessionHash( )
	
	cursor.execute( "UPDATE " + Config.DB_NAME + ".protein_mapping SET protein_mapping_status='inactive'" )
	
	with gopen( Config.EG_REFSEQ2UNIPROT ) as file :
		
		insertCount = 0
		for line in file.readlines( ) :
			line = line.strip( )
			
			# Skip Blank Lines and header lines
			if len( line ) <= 0 or "#" == line[0] :
				continue
				
			splitLine = line.split( "\t" )
			refseqAcc = splitLine[0].strip( )
			uniprotAcc = splitLine[1].strip( )
			
			if refseqAcc in refseqHash and uniprotAcc in uniprotHash :
				refseqID = refseqHash[refseqAcc]
				uniprotID = uniprotHash[uniprotAcc]
				
				cursor.execute( "SELECT protein_mapping_id FROM " + Config.DB_NAME + ".protein_mapping WHERE refseq_id=%s AND uniprot_id=%s LIMIT 1", [refseqID, uniprotID] )
				row = cursor.fetchone( )
				
				if None == row : 
					print "INSERTING NEW PROTEIN MAPPING"
					cursor.execute( "INSERT INTO " + Config.DB_NAME + ".protein_mapping VALUES( '0', %s, %s, 'active', NOW( ) )", [refseqID, uniprotID] )
				else :
					print "UPDATING EXISTING PROTEIN MAPPING"
					cursor.execute( "UPDATE " + Config.DB_NAME + ".protein_mapping SET protein_mapping_status='active' WHERE protein_mapping_id=%s", [row[0]] )

				insertCount = insertCount + 1
				
			if 0 == (insertCount % Config.DB_COMMIT_COUNT ) :
				Database.db.commit( )
				
	Database.db.commit( )
	
	cursor.execute( "SELECT uniprot_external_value, uniprot_id FROM " + Config.DB_NAME + ".uniprot_externals WHERE uniprot_external_source='REFSEQ'" )
	
	insertCount = 0
	for row in cursor.fetchall( ) :
		if row[0] in refseqHash :
			refseqID = refseqHash[row[0]]
			
			cursor.execute( "SELECT protein_mapping_id FROM " + Config.DB_NAME + ".protein_mapping WHERE refseq_id=%s AND uniprot_id=%s LIMIT 1", [refseqID, str(row[1])] )
			row = cursor.fetchone( )
			
			if None == row :
				print "INSERTING NEW PROTEIN MAPPING"
				cursor.execute( "INSERT INTO " + Config.DB_NAME + ".protein_mapping VALUES( '0', %s, %s, 'active', NOW( ) )", [refseqID, str(row[1])] )
			else :
				print "UPDATING EXISTING PROTEIN MAPPING"
				cursor.execute( "UPDATE " + Config.DB_NAME + ".protein_mapping SET protein_mapping_status='active' WHERE protein_mapping_id=%s", [row[0]] )
			
			insertCount = insertCount + 1
				
		if 0 == (insertCount % Config.DB_COMMIT_COUNT ) :
			Database.db.commit( )

	Database.db.commit( )
				
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'EG_updateGene2Uniprot', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )