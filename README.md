BioGRID-Annotation
==================

This resource contains tools for creating and maintaining an annotation database that is specifically used for operation with the the BioGRID suite of web applications and desktop software (http://thebiogrid.org).

### Requirements
To use all of the tools contained within, you require at least the following:

+ Python 2.7+
+ MySQL 5.5+
+ wget
+ Approximately 300 GB of HD Space (shared between database and downloaded files)
+ At least 8 GB of Memory (more is much better)

#### Required Python Libraries
+ MySQLdb
+ gzip
+ json

### Update Process

##### PRELIM 
Make sure you have a loaded copy of the annotation database tables to use for the new annotation. Load a MySQL dump of the existing BioGRID CORE tables (in the SQL folder), and load it into a fresh database if starting new. Otherwise, point to a previous version of the database. Once the database is loaded, make sure you add any organisms you want added, or changed, to the organisms table, as that table will be used to fetch your set of annotation.

##### Step by Step Process

1. Run the batch/fetchDownloads.sh file to download all the required files for an annotation update. This process will take some time, depending on the speed of your network connection. For example: the Trembl file from Uniprot is currently larger than 55 GB in XML format.

2. Verify that all files are downloaded

3. Go to config/config.json and adjust the settings in here to point to your setup. Especially modify the paths and the database login credentials to match your current configuration.

4. Run: python EG_parseGeneHistoryToStaging.py - This will load the gene history from ENTREZ_GENE into a staging table for later use.