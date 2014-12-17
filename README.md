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
+ xml.etree
+ glob
+ re
+ argparse

### Required Databases (from SQL directory if starting fresh)
+ core_staging - Tables used for staging data before updating.
+ core_stats - Tables for storing statistics on update progress.
+ core - Tables storing the complete annotation dataset.

## Update Process

### Before Getting Started 
Make sure you have a loaded copy of the annotation database tables to use for the new annotation. Load a MySQL dump of the existing CORE tables (in the SQL folder), and load it into a fresh database if starting new. Otherwise, point to a previous version of the database. Once the database is loaded, make sure you add any organisms you want added, or changed, to the organisms table, as that table will be used to fetch your set of annotation.

+ Run the batch/fetchDownloads.sh file to download all the required files for an annotation update. This process will take some time, depending on the speed of your network connection. For example: the Trembl file from Uniprot is currently larger than 55 GB in XML format.

+ Verify that all files are downloaded

+ Go to config/config.json (or create this file modelled on the config.json.example file already in this directory) and adjust the settings in here to point to your setup. Especially modify the paths and the database login credentials to match your current configuration.

#### Prepare STAGING DATABASE

+ Run: **python EG_parseGeneHistoryToStaging.py** - This will load the gene history from ENTREZ GENE into a staging table for later use.

+ Run: **python REFSEQ_fetchProteinIDs.py** - This will load all the protein UIDs for REFSEQ into a staging table based on the organisms we are interested in.

#### Process GENE ONTOLOGY

+ Run: **python GO_parseDefinitions.py** - This will load all the terms and definitions from GO and create a mapping to their GO SLIM subsets.

+ Run: **python GO_parseRelationships.py** - This will load all the is_a relationships between terms from GO.

+ Run: **python GO_buildSubsetPairings.py** - This will build parent child relationship pairings between GO terms and their parent terms based on GO SLIM subsets.

#### Process REFSEQ

+ Run: **python REFSEQ_downloadProteins.py** - This will download protein FASTA files for all the protein IDs downloaded into the staging database. This will take some time as sequences can only be fetched in batches of 10,000 at a time.

+ Run: **python REFSEQ_parseProteins.py** - This will parse the FASTA files downloaded in the step above and load them into the database. If the sequence already exists, its details are updated instead.

#### Process ENTREZ GENE

+ Run: **python EG_updateGeneHistory.py** - This will use _entrez_gene_history_ in the staging database to swap identifiers if they were replaced with an alternative. Also, it will discontinue genes that were merged, so there are no redundancies.

+ Run: **python EG_parseGenes.py** - This will load up all new genes from ENTREZ GENE into the genes table using only the organisms in the _organisms_ table.

+ Run: **python EG_parseAliases.py** - This will load all the aliases from ENTREZ GENE fetching only those we are interested in via previously loaded data stored in the _genes_ table.

+ Run: **python EG_parseExternals.py** - This will load all the external database references from ENTREZ GENE fetching only those we are interested in via previously loaded data stored in the _genes_ table.

+ Run: **python EG_parseDefinitions.py** - This will load all the definition entries from ENTREZ GENE fetching only those we are interested in via previously loaded data stored in the _genes_ table.

+ Run: **python EG_parseGO.py** - This will load the ENTREZ GENE gene2go file for a mapping of GENE ONTOLOGY terms to _genes_.

+ Run: **python EG_parseGene2Ensembl.py** - This will load the ENTREZ GENE gene2ensembl file into the _gene_externals_ table for Ensembl entries.

+ Run: **python EG_parseGene2Refseq.py** - This will parse the Gene2Refseq file from ENTREZ GENE and create a mapping table between _genes_ and _refseq_.

#### Process REFSEQ MISSING

+ Run: **python REFSEQ_downloadMissingProteins.py** - This will download protein FASTA files for any proteins in the _refseq_ table that do not have annotation. These are most likely proteins that were added when running the EG_parseGene2Refseq.py script.

+ Run: **python REFSEQ_parseMissingProteins.py** - This will parse the FASTA files downloaded in the step above and load them into the database.

#### Process MODEL ORGANISM SUPPLEMENTS

+ Run: **python SGD_parseGenes.py** - This will process the SGD Features file and match our _gene_ table with the current official symbol and descriptions for genes. It will also load in "retrotransposon" records which are required by BioGRID but not loaded via ENTREZ_GENE.

+ Run: **python POMBASE_parseGenes.py** - This will process the Pombase file and match our _gene_ table with the current official symbol and descriptions for genes. 

+ Run: **python CGD_fixAnnotation.py** - This will process the CGD file and fix some problems with the ENTREZ GENE version. Specifically, some duplicate entries and non-common place systematic names. This script will likely require modification due to regular changes to file formatting and processes at both CGD and NCBI.

#### Process UNIPROTKB

+ Run: **python UNIPROT_downloadProteins.py** - This will download a file for each organism we are interested in containing both SWISS-PROT and TREMBL proteins. These will be parsed out in the subsequent steps. After completion, go to the directory where you downloaded the files and run **gzip --test --verbose *.gz**. This will test all the files to ensure they are complete (some may fail during transfer). If any show errors, simply run **python UNIPROT_downloadProteins.py -o [ORGANISM ID]** to re-download that specific file. Keep testing and re-downloading until all files pass as valid compressed files.

+ Run: **python UNIPROT_parseProteins.py** - This will process each of the files downloaded in the previous step and load their annotation information into appropriate tables.

+ Run: **python UNIPROT_parseIsoforms.py** - This will read the uniprot isoform datafile and load the isoforms into a separate table.

#### Process PROTEIN MAPPING

+ Run: **python EG_parseGene2Uniprot.py** - This will load the mapping data from the Gene2Uniprot Collab file, into a protein mapping table.

+ Run: **python PROTEIN_mapIdenticalProteins.py** - This will check for identical sequences between the two protein databases and make a mapping if they are the same.

+ Run: **python PROTEIN_buildConsolidatedSet.py** - This will update the _proteins_ table to create a consolidated UNIPROT/REFSEQ protein table. UNIPROT is considered the primary and REFSEQ is only loaded when no valid mapping to a UNIPROT exists in the previously loaded tables.

## Quick Lookup Table Generation
Once the annotation database is completed via the steps list above, we generate several quick lookup tables that facilitate rapid searching without requiring large joins or complicated SQL queries. These tables may take some time to complete, so be prepared for a lengthy process depending on your resources available.

+ Create a database containing a empty set of the quick_annotation tables. A reference SQL file can be found in the SQL folder.

+ Go to config/config.json and be sure to set the "DB_QUICK" entry to point to this new database.

#### Build Quick Gene Annotation

+ Run: **python QUICK_buildOrganisms.py** - This will create the _quick_organisms_ lookup table.

+ Run: **python QUICK_buildAnnotation.py** - This will generate a quick lookup table of gene annotation. The table containing this data is simply named _quick_annotation_ due to legacy purposes.

+ Run: **python QUICK_buildIdentifiers.py** - This will generate a quick lookup table of gene identifiers. The table containing this data is simply named _quick_identifiers_ due to legacy purposes.

+ Run: **python QUICK_buildProteins.py** - This will generate a quick lookup table of proteins.

+ Run: **python QUICK_buildProteinIdentifiers.py** - This will generate a quick lookup table of protein identifiers.

+ Run: **python QUICK_buildProteinFeatures.py** - This will generate a quick lookup table of protein features.

## Testing
These calls are mostly for internal BioGRID based testing to validate the final resulting annotation before rolling it out to various different applications within our ecosystem. Likely not of much use to third parties.

## Maintenance
These calls are mostly for maintaining an existing annotation database such as adding additional organisms or updating annotation on existing records.

### Load a New Organism
Ensure that the organism is loaded into the _organisms_ table prior to starting

+ Run: **python EG_updateGenes.py -o [NCBI ORGANISM ID]** - This will run through the gene_info file and selectively process only the organism you passed in via the -o parameter.

+ Run: **python EG_updateAliases.py -o [NCBI ORGANISM ID]** - This will run through the gene_info file and selectively process only the organism you passed in via the -o parameter and grab only aliases.

+ Run: **python EG_updateExternals.py -o [NCBI ORGANISM ID]** - This will run through the gene_info file and selectively process only the organism you passed in via the -o parameter and grab only external identifiers.

+ Run: **python EG_updateDefinitions.py -o [NCBI ORGANISM ID]** - This will run through the gene_info file and selectively process only the organism you passed in via the -o parameter and grab only definitions.

+ Run: **python EG_updateGO.py -o [NCBI ORGANISM ID]** - This will run through the gene2go file and selectively process only the organism you passed in via the -o parameter and grab only go mappings that match.

+ Run: **python EG_updateGene2Ensembl.py -o [NCBI ORGANISM ID]** - This will run through the gene2ensembl file and selectively process only the organism you passed in via the -o parameter and grab only ensembl ids that match.