
# Combine the UNIPROT and REFSEQ tables into
# a consolidated protein set where the UNIPROT
# protein takes priority over the REFSEQ when
# applicable.

import Config
import sys, string
import MySQLdb
import Database

from classes import Protein

with Database.db as cursor :

	protein = Protein.Protein( Database.db, cursor )

	cursor.execute( "UPDATE " + Config.DB_NAME + ".proteins SET protein_status='inactive'" )
	Database.db.commit( )
	
	# Process UNIPROT first as we want to use that as the base for
	# proteins. REFSEQs that are identical will be ignored or remapped
	# and those that have no mapping will be slotted in at the end.
	
	cursor.execute( "SELECT uniprot_id, organism_id FROM " + Config.DB_NAME + ".uniprot WHERE uniprot_status='active'" )
	
	for row in cursor.fetchall( ) :
	
		# See if Protein is already in table
		proteinID = protein.proteinExists( str(row[0]), "UNIPROT" )
		if proteinID :
			# If it exists, flip to active, be done with it
			cursor.execute( "UPDATE " + Config.DB_NAME + ".proteins SET protein_status='active', organism_id=%s WHERE protein_id=%s", [row[1], proteinID] )
		else :
			# If it does not exist
			# Test to see if it has refseq mappings
			refseqMappings = protein.fetchMappingsByUniprotID( str(row[0]) )
		
			# Test to see if those refseq mappings exist
			if len(refseqMappings) > 0 :
				sqlFormat = ",".join( ['%s'] * len(refseqMappings) )
				cursor.execute( "SELECT protein_id FROM " + Config.DB_NAME + ".proteins WHERE protein_reference_id IN (%s) AND protein_source='REFSEQ' ORDER BY protein_id ASC LIMIT 1" % sqlFormat, tuple(refseqMappings) )
				
				refRow = cursor.fetchone( )
				if None == refRow :
					# If not, just add the uniprot as separate
					cursor.execute( "INSERT INTO " + Config.DB_NAME + ".proteins VALUES ( '0', %s, 'UNIPROT', %s, 'active' )", [str(row[0]), str(row[1])] )
				else :
					# If they do, take the lowest one and change it to uniprot
					# keep the rest inactive
					cursor.execute( "UPDATE " + Config.DB_NAME + ".proteins SET protein_reference_id=%s, protein_source=%s, organism_id=%s, protein_status='active' WHERE protein_id=%s", [str(row[0]), 'UNIPROT', str(row[1]), str(refRow[0])] )
	
			else :
				# Load all UNIPROTs with no mappings into the table as well
				cursor.execute( "INSERT INTO " + Config.DB_NAME + ".proteins VALUES ( '0', %s, 'UNIPROT', %s, 'active' )", [str(row[0]), str(row[1])] )
				
	
		Database.db.commit( )
	
	# Process UNIPROT isoforms
	
	cursor.execute( "SELECT uniprot_isoform_id, organism_id FROM " + Config.DB_NAME + ".uniprot_isoforms WHERE uniprot_isoform_status='active'" )
	
	for row in cursor.fetchall( ) :
	
		# See if Protein is already in table
		proteinID = protein.proteinExists( str(row[0]), "UNIPROT-ISOFORM" )
		if proteinID :
			# If it exists, flip to active, be done with it
			cursor.execute( "UPDATE " + Config.DB_NAME + ".proteins SET protein_status='active', organism_id=%s WHERE protein_id=%s", [row[1], proteinID] )
		else :
			# Else insert it as a new protein
			cursor.execute( "INSERT INTO " + Config.DB_NAME + ".proteins VALUES ( '0', %s, 'UNIPROT-ISOFORM', %s, 'active' )", [str(row[0]), str(row[1])] )
	
		Database.db.commit( )
	
	# Process REFSEQ last. Only load REFSEQ entries that have no mappings to Uniprot
	
	cursor.execute( "SELECT refseq_id, organism_id FROM " + Config.DB_NAME + ".refseq WHERE refseq_status='active'" )
	
	for row in cursor.fetchall( ) :
	
		# See if Protein is already in table
		proteinID = protein.proteinExists( str(row[0]), "REFSEQ" )
		if proteinID :
			# If it exists, flip to active, be done with it
			cursor.execute( "UPDATE " + Config.DB_NAME + ".proteins SET protein_status='active', organism_id=%s WHERE protein_id=%s", [row[1], proteinID] )
		else :
			# If it does not exist
			# Test to see if it has uniprot mappings
			uniprotMappings = protein.fetchMappingsByRefseqID( str(row[0]) )
		
			# Test to see if those uniprot mappings exist
			# If they do not, load the refseq as a separate entry
			if len(uniprotMappings) <= 0 :
				cursor.execute( "INSERT INTO " + Config.DB_NAME + ".proteins VALUES ( '0', %s, 'REFSEQ', %s, 'active' )", [str(row[0]), str(row[1])] )
	
		Database.db.commit( )
	
	cursor.execute( "INSERT INTO " + Config.DB_STATS + ".update_tracker VALUES ( '0', 'PROTEIN_buildConsolidatedSet', NOW( ) )" )
	Database.db.commit( )
	
sys.exit( )