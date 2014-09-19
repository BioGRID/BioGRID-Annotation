# Parse through UNIPROT XML file and load all 
# protein information into separate tables

import sys, string
import Config

from xml.sax import handler
from classes import UniprotKB

class UniprotProteinXMLParser( handler.ContentHandler ) :

	def __init__( self, uniprotKB, organismID ) :
	
		# Tracking Stack
		self.path = ""
		self.pathList = []
		
		# Initialization Variables
		self.uniprotKB = uniprotKB
		self.organismID = organismID
		
		# Storage Strings
		self.characterVal = ""
		self.geneNameType = ""
		
		# Storage Objects
		self.currentRecord = { }
		self.currentGO = {}
		self.currentFeature = {}
		self.currentGene = {}
		self.currentComment = {}
		
		# Detection Booleans
		self.isGO = False
		
		self.ignoreExternal = set( ['GO','PFAM','REFSEQ','INTACT','DIP','GENEID','STRING','MINT','SMART','PROSITE','SUPFAM','INTERPRO','EMBL','GENEVESTIGATOR','GENETREE'] )
	
	def startElement( self, name, attrs ) :
		self.pathList.append( name )
		self.path = "|".join( self.pathList )
	
		if 'uniprot|entry' == self.path :
			self.currentRecord['dataset'] = attrs['dataset'].lower( )
		
		elif 'uniprot|entry|accession' == self.path :
			if 'accessions' not in self.currentRecord :
				self.currentRecord['primary_accession'] = ""
				self.currentRecord['accessions'] = set( )
				
		elif 'uniprot|entry|sequence' == self.path :
			self.currentRecord['sequence_version'] = attrs['version']
			self.currentRecord['sequence'] = ""
			
		elif 'uniprot|entry|gene' == self.path :
			if 'genes' not in self.currentRecord :
				self.currentRecord['genes'] = []
				
		elif 'uniprot|entry|gene|name' == self.path :
			self.geneNameType = attrs['type'].lower( )
			
		elif 'uniprot|entry|proteinExistence' == self.path :
			self.currentRecord['existence'] = attrs['type']
			
		elif 'uniprot|entry|feature' == self.path :
			self.currentFeature['type'] = attrs['type']
			attrsIndexes = vars(attrs)
			
			# Store Description and ID attributes if they exist
			if 'description' in attrsIndexes['_attrs'] :
				self.currentFeature['description'] = attrs['description']
			if 'id' in attrsIndexes['_attrs'] :
				self.currentFeature['id'] = attrs['id']
				
		elif 'uniprot|entry|feature|location|position' == self.path :
			attrsIndexes = vars(attrs)
			if 'position' in attrsIndexes['_attrs'] :
				self.currentFeature['position'] = attrs['position']
				
		elif 'uniprot|entry|feature|location|begin' == self.path :
			attrsIndexes = vars(attrs)
			if 'position' in attrsIndexes['_attrs'] :
				self.currentFeature['begin'] = attrs['position']
				
		elif 'uniprot|entry|feature|location|end' == self.path :
			attrsIndexes = vars(attrs)
			if 'position' in attrsIndexes['_attrs'] :
				self.currentFeature['end'] = attrs['position']
				
		elif 'uniprot|entry|comment' == self.path :
			self.currentComment["TYPE"] = attrs['type'].upper( )
				
		elif 'uniprot|entry|dbReference' == self.path :
		
			# Process dbReference entries and perform separate
			# tasks based on which one we are looking at.
			
			if attrs['type'].upper( ) not in self.ignoreExternal :
			
				if 'externals' not in self.currentRecord :
					self.currentRecord['externals'] = { }
					
				if attrs['type'].upper( ) not in self.currentRecord['externals'] :
					self.currentRecord['externals'][attrs['type'].upper( )] = set( )
				
				self.currentRecord['externals'][attrs['type'].upper( )].add( attrs['id'] )
				
			else :
			
				# These are special cases where more processing
				# is required before storing in current record
			
				if 'GENEID' == attrs['type'].upper( ) :
					if 'GENEID' not in self.currentRecord :
						self.currentRecord['entrez_gene'] = set( )
					self.currentRecord['entrez_gene'].add( attrs['id'] )
					
				elif 'GO' == attrs['type'].upper( )  :
					if 'go' not in self.currentRecord :
						self.currentRecord['go'] = []
					self.currentGO["full_id"] = attrs['id']
					self.currentGO["short_id"] = str(int(attrs['id'][3:]))
					self.isGO = True
					
				elif 'REFSEQ' == attrs['type'].upper( ) :
				
					if 'externals' not in self.currentRecord :
						self.currentRecord['externals'] = { }
						
					if 'REFSEQ' not in self.currentRecord['externals'] :
						self.currentRecord['externals']['REFSEQ'] = set( )
						
					splitID = attrs['id'].split( "." )
					if len( splitID ) > 1 :
						self.currentRecord['externals']['REFSEQ'].add( splitID[0] )
					else :
						self.currentRecord['externals']['REFSEQ'].add( attrs['id'] )
						
		elif 'uniprot|entry|dbReference|property' == self.path and self.isGO :
			if attrs['type'] == 'evidence' :
				evidence = attrs['value'].split( ":" )
				self.currentGO["evidence"] = str(evidence[0])

	def endElement( self, name ) :
	
		if 'uniprot|entry' == self.path :
		
			print self.currentRecord['primary_accession']
			uniprotID = self.uniprotKB.processProtein( self.currentRecord, self.organismID )
			self.uniprotKB.processFeatures( uniprotID, self.currentRecord )
			self.uniprotKB.processAliases( uniprotID, self.currentRecord )
			self.uniprotKB.processExternals( uniprotID, self.currentRecord )
			self.uniprotKB.processDefinitions( uniprotID, self.currentRecord )
			self.uniprotKB.processGO( uniprotID, self.currentRecord )
		
			self.currentRecord = { }
		
		elif 'uniprot|entry|accession' == self.path :
			if self.currentRecord['primary_accession'] == "" :
				self.currentRecord['primary_accession'] = self.characterVal
			else :
				self.currentRecord['accessions'].add( self.characterVal )
				
		elif 'uniprot|entry|sequence' == self.path :
			self.currentRecord['sequence'] = self.characterVal.upper( )
			self.currentRecord['sequence_length'] = len(self.currentRecord['sequence'])
			
		elif 'uniprot|entry|name' == self.path :
			self.currentRecord['name'] = self.characterVal.upper( )
			
		elif 'uniprot|entry|protein|recommendedName|fullName' == self.path :
		
			if 'descriptions' not in self.currentRecord :
				self.currentRecord['descriptions'] = []
				
			self.currentRecord['descriptions'].append( { "TYPE" : "RECOMMENDED_NAME", "DESC" : self.characterVal } )
			
		elif 'uniprot|entry|protein|alternativeName|fullName' == self.path :
		
			if 'descriptions' not in self.currentRecord :
				self.currentRecord['descriptions'] = []
				
			self.currentRecord['descriptions'].append( { "TYPE" : "ALT_NAME", "DESC" : self.characterVal } )
			
		elif 'uniprot|entry|comment|text' == self.path :
			self.currentComment["DESC"] = self.characterVal
			
		elif 'uniprot|entry|comment' == self.path :
			if ("TYPE" in self.currentComment and "DESC" in self.currentComment) and (len(self.currentComment["TYPE"]) > 0 and len(self.currentComment["DESC"]) > 0) :
				if 'descriptions' not in self.currentRecord :
					self.currentRecord['descriptions'] = []
			
				self.currentRecord['descriptions'].append( self.currentComment )
			self.currentComment = { }
			
		elif 'uniprot|entry|gene|name' == self.path and self.geneNameType != "" :
		
			if self.geneNameType not in self.currentGene :
				self.currentGene[self.geneNameType] = set( )
				
			self.currentGene[self.geneNameType].add( self.characterVal )
			self.geneNameType = ""
			
		elif 'uniprot|entry|gene' == self.path :
			self.currentRecord['genes'].append( self.currentGene )
			self.currentGene = { }
			self.geneNameType = ""
			
		elif 'uniprot|entry|dbReference' == self.path and self.isGO :
			self.isGO = False
			self.currentRecord['go'].append( self.currentGO )
			self.currentGO = { }
			
		elif 'uniprot|entry|feature' == self.path :
			if 'features' not in self.currentRecord :
				self.currentRecord['features'] = []
				
			self.currentRecord['features'].append( self.currentFeature )
			self.currentFeature = { }
			
		self.characterVal = ""
		self.pathList.pop( )
		self.path = "|".join( self.pathList )

	def characters( self, content ) :
		self.characterVal = self.characterVal + content.strip( )