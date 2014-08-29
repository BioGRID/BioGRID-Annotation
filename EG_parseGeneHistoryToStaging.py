
# Parses Entrez Gene gene_history file format
# into staging area table 

import sys, string
import MySQLdb
import Database
import gzip
import Config

db = Database.db
cursor = db.cursor( )

cursor.execute( "TRUNCATE TABLE " + Config.DB_STAGING + ".entrez_gene_history" ) 

historyFile = gzip.open( Config.EG_GENEHISTORY, 'r' )
insertCount = 0
for line in historyFile.readlines( ) :

	# Ignore Header Line
	if "#" == line[0] :
		continue

	splitLine = line.strip( ).split( "\t" )
	
	if "-" == splitLine[1] :
		splitLine[1] = "-1"
		
	if "-" == splitLine[2] :
		splitLine[2] = "-1"
	
	if "-" == splitLine[3] :
		splitLine[3] = "-1"
	
	formattedEntries = ','.join( ['%s'] * len( splitLine ) )
	query = "INSERT INTO " + Config.DB_STAGING + ".entrez_gene_history VALUES( %s, NOW( ) )"
	query = query % formattedEntries
	cursor.execute( query, tuple( splitLine ) )
	
	insertCount = insertCount + 1
	
	if 0 == (insertCount % Config.DB_COMMIT_COUNT ) :
		db.commit( )
		
db.commit( )
db.close( )
historyFile.close( )