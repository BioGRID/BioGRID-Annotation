# Change the ptm_sequence_ids of existing ptms 
# based on processed swap details.

import Config
import sys, string, argparse
import MySQLdb
import Database
import gzip

from classes import EntrezGene

# Process Command Line Input
argParser = argparse.ArgumentParser( description = 'Swap PTMs that were changed from one build to the next.' )
argParser.add_argument( '-f', help = 'Input File', dest = 'inputFile', required=True, action='store' )
inputArgs = vars( argParser.parse_args( ) )

with Database.db as cursor :

				
sys.exit( )