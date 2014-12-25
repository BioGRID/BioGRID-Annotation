# Change the organism ID of existing genes before running
# the update.

import Config
import sys, string, argparse
import MySQLdb
import Database
import gzip

from classes import EntrezGene

# Process Command Line Input
argParser = argparse.ArgumentParser( description = 'Swap Genes that were changed from one build to the next.' )
argParser.add_argument( '-f', help = 'Input File', dest = 'inputFile', required=True, action='store' )
inputArgs = vars( argParser.parse_args( ) )

disableMsg = "Disabled by script because one or more interactors was deprecated"

with Database.db as cursor :

	disabledInts = set( )
	swappedInts = set( )
	disabledComps = set( )
	swappedComps = set( )
	
	with open( inputArgs['inputFile'], 'r' ) as file :
		for line in file.readlines( ) :
			
			line = line.strip( )
				
			splitLine = line.split( "\t" )
			oldID = splitLine[0].strip( )
			newID = splitLine[1].strip( ).lower( )
			
			# PROCESS INTERACTIONS
			cursor.execute( "SELECT interaction_id, interactor_A_id, interactor_B_id, experimental_system_id, publication_id, modification_id FROM " + Config.DB_IMS + ".interaction_matrix WHERE (interactor_A_id=%s OR interactor_B_id=%s) AND modification_type='ACTIVATED'", [oldID,oldID] )
			
			for (intID, interactorA, interactorB, expSys, pubID, modID) in cursor.fetchall( ) :

				if "dead" == newID :
					# Deprecate Interactions involving this Gene
					print "FOUND DEAD, DEPRECATING"
					cursor.execute( "INSERT INTO " + Config.DB_IMS + ".interaction_history VALUES( '0','DISABLED', %s, '1', %s, NOW( ) )", [intID, disableMsg] )
					disabledInts.add( intID )
					Database.db.commit( )
				else :
					# Test new ID combination to see if it already exists
					interactorA = str(interactorA)
					interactorB = str(interactorB)
					
					if interactorA.lower( ) == oldID.lower( ) :
						interactorA = str(newID)
					
					if interactorB.lower( ) == oldID.lower( ) :
						interactorB = str(newID)
					
					cursor.execute( "SELECT interaction_id FROM " + Config.DB_IMS + ".interaction_matrix WHERE interactor_A_id=%s AND interactor_B_id=%s AND experimental_system_id=%s AND publication_id=%s AND modification_id=%s AND modification_type='ACTIVATED' LIMIT 1", [interactorA, interactorB, expSys, pubID, modID] )
					testRow = cursor.fetchone( )
					
					# If not, make the swap
					if None == testRow :
						print "FOUND SWAPPABLE"
						cursor.execute( "UPDATE " + Config.DB_IMS + ".interactions SET interactor_A_id=%s, interactor_B_id=%s WHERE interaction_id=%s", [interactorA, interactorB, intID] )
						cursor.execute( "UPDATE " + Config.DB_IMS + ".interaction_matrix SET interactor_A_id=%s, interactor_B_id=%s WHERE interaction_id=%s", [interactorA, interactorB, intID] )
						swappedInts.add( intID )
						Database.db.commit( )
					else :
						# if so, deprecate the old
						print "FOUND DUPLICATE AFTER SWAP, DEPRECATING"
						cursor.execute( "INSERT INTO " + Config.DB_IMS + ".interaction_history VALUES( '0','DISABLED', %s, '1', %s, NOW( ) )", [intID, disableMsg] )
						disabledInts.add( intID )
						Database.db.commit( )
			
			# PROCESS COMPLEXES
			cursor.execute( "SELECT complex_id, complex_participants, experimental_system_id, publication_id, modification_id FROM " + Config.DB_IMS + ".complex_matrix WHERE modification_type='ACTIVATED'" )

			for (complexID, participants, expSys, pubID, modID) in cursor.fetchall( ) :
			
				participantList = participants.split( "|" )
				if str(oldID) in participantList :
				
					if "dead" == newID :
						# Deprecate Complexes involving this Gene
						print "FOUND DEAD COMPLEX, DEPRECATING"
						cursor.execute( "INSERT INTO " + Config.DB_IMS + ".complex_history VALUES( '0','DISABLED', %s, '1', %s, NOW( ) )", [complexID, disableMsg] )
						disabledComps.add( complexID )
						Database.db.commit( )
					else :
						# Test new ID combination to see if it already exists
						newParticipants = []
						for participant in participantList :
							if participant.lower( ) == oldID.lower( ) :
								newParticipants.append( str(newID) )
							else :
								newParticipants.append( str(participant) )
						
						newParticipants.sort( )
						participants = "|".join(newParticipants)
						
						cursor.execute( "SELECT complex_id FROM " + Config.DB_IMS + ".complex_matrix WHERE complex_participants=%s AND experimental_system_id=%s AND publication_id=%s AND modification_id=%s AND modification_type='ACTIVATED' LIMIT 1", [participants, expSys, pubID, modID] )
						testRow = cursor.fetchone( )
						
						# If not, make the swap
						if None == testRow :
							print "FOUND SWAPPABLE COMPLEX"
							cursor.execute( "UPDATE " + Config.DB_IMS + ".complexes SET complex_participants=%s WHERE complex_id=%s", [participants, complexID] )
							cursor.execute( "UPDATE " + Config.DB_IMS + ".complex_matrix SET complex_participants=%s WHERE complex_id=%s", [participants, complexID] )
							swappedComps.add( complexID )
							Database.db.commit( )
						else :
							# if so, deprecate the old
							print "FOUND DUPLICATE COMPLEX AFTER SWAP, DEPRECATING"
							cursor.execute( "INSERT INTO " + Config.DB_IMS + ".complex_history VALUES( '0','DISABLED', %s, '1', %s, NOW( ) )", [complexID, disableMsg] )
							disabledComps.add( complexID )
							Database.db.commit( )
	
	print "DISABLED : " + str(len(disabledInts)) + " INTERACTIONS"
	print "SWAPPED  : " + str(len(swappedInts)) +  " INTERACTIONS"
	print "DISABLED : " + str(len(disabledComps)) + " COMPLEXES"
	print "SWAPPED  : " + str(len(swappedComps)) +  " COMPLEXES"
	
	Database.db.commit( )
				
sys.exit( )