import json

with open( "config/config.json", "r" ) as configFile :
	data = configFile.read( )

data = json.loads( data )