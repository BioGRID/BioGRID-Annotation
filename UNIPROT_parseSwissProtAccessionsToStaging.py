
# Parses UNIPROT_SWISSPROT file and pull out only accessions
# into staging area table

import sys, string
import MySQLdb
import Database
import Config

from classes import UniprotAccessionXMLParser
from xml.sax import parse
from gzip import open as gopen

db = Database.db
cursor = db.cursor( )

cursor.execute( "TRUNCATE TABLE " + Config.DB_STAGING + ".swissprot_ids" )
db.commit( )

with gopen( Config.UP_SWISSPROT ) as swissprot :
	parse( swissprot, UniprotAccessionXMLParser.UniprotAccessionXMLParser( ) )