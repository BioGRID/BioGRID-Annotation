BioGRID-Annotation
==================

This resource contains tools for creating and maintaining an annotation database that is specifically used for operation with the the BioGRID suite of web applications and desktop software (http://thebiogrid.org). It builds off major protein databases such as REFSEQ and UNIPROT as well as other resources for Gene annotation such as ENTREZ GENE and other model organism databases. 

## Requirements
To use all of the tools contained within, you require at least the following:

+ Python 2.7+
+ MySQL 5.5+
+ wget
+ Approximately 300 GB of HD Space (shared between database and downloaded files)
+ At least 8 GB of Memory (more is much better)

### Required Python Libraries
+ MySQLdb
+ gzip
+ json
+ xml.sax

### Required Databases (from SQL directory if starting fresh)
+ core_staging - Tables used for staging data before updating.
+ core_stats - Tables for storing statistics on update progress.
+ core - Tables storing the complete annotation dataset.

## Update Process

### Before Getting Started 
Make sure you have a loaded copy of the annotation database tables to use for the new annotation. Load a MySQL dump of the existing CORE tables (in the SQL folder), and load it into a fresh database if starting new. Otherwise, point to a previous version of the database. Once the database is loaded, make sure you add any organisms you want added, or changed, to the organisms table, as that table will be used to fetch your set of annotation.

+ Run the batch/fetchDownloads.sh file to download all the required files for an annotation update. This process will take some time, depending on the speed of your network connection. For example: the Trembl file from Uniprot is currently larger than 55 GB in XML format.

+ Verify that all files are downloaded

+  Go to config/config.json (or create this file modelled on the config.json.example file already in this directory) and adjust the settings in here to point to your setup. Especially modify the paths and the database login credentials to match your current configuration.

#### Prepare Staging Database

+ Run: **python EG_parseGeneHistoryToStaging.py** - This will load the gene history from ENTREZ GENE into a staging table for later use.

+ Run: **python UNIPROT_parseSwissProtAccessionsToStaging.py** - This will load all the SWISSPROT accession ids into a staging table so we can later quickly determine which ids are from SWISSPROT and which are from TREMBL.

#### Process ENTREZ GENE

+ Run: **python EG_updateGeneHistory.py** - This will use _entrez_gene_history_ in the staging database to swap identifiers if they were replaced with an alternative. Also, it will discontinue genes that were merged, so there are no redundancies.

+ Run: **python EG_parseGenes.py** - This will load up all new genes from ENTREZ GENE into the genes table using only the organisms in the _organisms_ table.

+ Run: **python EG_parseAliases.py** - This will load all the aliases from ENTREZ GENE fetching only those we are interested in via previously loaded data stored in the _genes_ table.

+ Run: **python EG_parseExternals.py** - This will load all the external database references from ENTREZ GENE fetching only those we are interested in via previously loaded data stored in the _genes_ table.

+ Run: **python EG_parseDefinitions.py** - This will load all the definition entries from ENTREZ GENE fetching only those we are interested in via previously loaded data stored in the _genes_ table.

#### Process GENE ONTOLOGY