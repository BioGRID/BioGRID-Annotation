# A suite of commonly used routines for application
# in multiple scripts.

import MySQLdb
import sys, string
import Config

class CommonFunctions( ) :

	def __init__( self, db, cursor ) :
		self.db = db
		self.cursor = cursor
		
	def fetchOrganismList( self, isUniprot = False ) :
		
		if isUniprot :
			self.cursor.execute( "SELECT organism_id, entrez_taxid, organism_common_name, organism_official_name, organism_abbreviation, organism_strain, organism_status FROM " + Config.DB_NAME + ".organisms WHERE organism_status='active'" )
		else :
			self.cursor.execute( "SELECT organism_id, entrez_taxid, organism_common_name, organism_official_name, organism_abbreviation, organism_strain, organism_status FROM " + Config.DB_NAME + ".organisms WHERE organism_status='active'" )

		organismInfo = {}

		for row in self.cursor.fetchall( ) :
			(organism_id, organism_taxid, organism_common_name, organism_official_name, organism_abbreviation, organism_strain, organism_status) = row
			organismInfo[organism_id] = row

		return organismInfo