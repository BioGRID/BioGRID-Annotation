
# Create the quick lookup gene annotation
# table by combining annotation from other
# resources into a single table.

import Config
import sys, string
import MySQLdb
import Database

with Database.db as cursor :

	cursor.execute( "SELECT refseq_id, uniprot_id FROM " + Config.DB_NAME + ".protein_mapping WHERE protein_mapping_status='active'" )
	refseqIDs = set( )
	uniprotIDs = set( )
	for row in cursor.fetchall( ) :
		refseqIDs.add( str(row[0]) )
		uniprotIDs.add( str(row[1]) )

	cursor.execute( "SELECT organism_id FROM organisms WHERE organism_status='active'" )
	
	for row in cursor.fetchall( ) :
	
		print "Working on : " + str(row[0])
	
		cursor.execute( "SELECT uniprot_id, uniprot_sequence FROM " + Config.DB_NAME + ".uniprot WHERE uniprot_status='active' AND organism_id=%s", [row[0]] )
		
		# Loading existing Uniprot sequences for this organism
		uniprotSequences = { }
		for uniRow in cursor.fetchall( ) :
			uniprotSequences[uniRow[1]] = str(uniRow[0])
			
		cursor.execute( "SELECT refseq_id, refseq_sequence FROM " + Config.DB_NAME + ".refseq WHERE refseq_status='active' AND organism_id=%s", [row[0]] )
		
		# Test each refseq to see if identical match
		# exists in uniprot
		
		matchCount = 0
		for refRow in cursor.fetchall( ) :
		
			# If we find a match, test to see if a mapping already exists
			if refRow[1] in uniprotSequences :
				uniprotID = uniprotSequences[refRow[1]]
				refseqID = str(refRow[0])
				
				cursor.execute( "SELECT protein_mapping_id FROM " + Config.DB_NAME + ".protein_mapping WHERE refseq_id=%s AND uniprot_id=%s AND protein_mapping_status='active' LIMIT 1", [refseqID, uniprotID] )
				existRow = cursor.fetchone( )
				
				if None == existRow :
				
					# If no mapping exists, test to see if either proteins are already
					# mapped to alternatives, if so, ignore them and assume the 
					# mapping from another source is the correct one.
					
					if uniprotID not in uniprotIDs and refseqID not in refseqIDs :
						matchCount = matchCount + 1
						cursor.execute( "INSERT INTO " + Config.DB_NAME + ".protein_mapping VALUES( '0', %s, %s, 'active', NOW( ) )", [refseqID, uniprotID] )
						Database.db.commit( )
					
		print "Missing: " + str(matchCount) + " => " + str(row[0])
		
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'PROTEIN_mapIdenticalProteins', NOW( ) )" )
	Database.db.commit( )
				
sys.exit( )			