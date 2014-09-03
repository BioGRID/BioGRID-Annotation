# Parse through UNIPROT XML file and load all 
# accession identifiers into a separate table

import MySQLdb
import sys, string
import Config
import Database

from xml.sax import handler

class UniprotAccessionXMLParser( handler.ContentHandler ) :

	def __init__( self ) :
		self.path = ""
		self.pathList = []
		self.accession = ""
		self.db = Database.db
		self.cursor = self.db.cursor( )
		self.insertCount = 0

	def startElement( self, name, attrs ) :
		self.pathList.append( name )
		self.path = "|".join( self.pathList )

	def characters( self, content ) :
		if "uniprot|entry|accession" == self.path :
			self.accession = self.accession + content
			
	def endElement( self, name ) :
	
		if "uniprot|entry|accession" == self.path :
			self.cursor.execute( "INSERT INTO " + Config.DB_STAGING + ".swissprot_ids (accession) VALUES ( %s )", [self.accession.strip( )] )
			self.accession = ""
			self.insertCount = self.insertCount + 1
			
		if 0 == (self.insertCount % Config.DB_COMMIT_COUNT ) :
			self.db.commit( )
	
		self.pathList.pop( )
		self.path = "|".join( self.pathList )
		
	def endDocument( self ) :
		self.db.commit( )