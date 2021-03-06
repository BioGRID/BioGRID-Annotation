#!/bin/bash
baseDir="../downloads"

cd $baseDir/entrez_gene
wget -m -nd ftp://ftp.ncbi.nih.gov/gene/DATA/gene_info.gz
wget -m -nd ftp://ftp.ncbi.nih.gov/gene/DATA/gene_history.gz
wget -m -nd ftp://ftp.ncbi.nih.gov/gene/DATA/gene_refseq_uniprotkb_collab.gz
wget -m -nd ftp://ftp.ncbi.nih.gov/gene/DATA/gene2refseq.gz
wget -m -nd ftp://ftp.ncbi.nih.gov/gene/DATA/gene2go.gz
wget -m -nd ftp://ftp.ncbi.nih.gov/gene/DATA/gene_group.gz
wget -m -nd ftp://ftp.ncbi.nih.gov/gene/DATA/gene2ensembl.gz
wget -m -nd ftp://ftp.ncbi.nih.gov/gene/DATA/gene2accession.gz

cd ../go
wget -m -nd http://archive.geneontology.org/latest-termdb/go_daily-termdb.obo-xml.gz

cd ../psi
wget -m -nd http://psidev.cvs.sourceforge.net/viewvc/*checkout*/psidev/psi/mi/rel25/data/psi-mi25.obo

cd ../sgd
wget -m -nd http://downloads.yeastgenome.org/curation/chromosomal_feature/SGD_features.tab

cd ../cgd
wget -m -nd http://www.candidagenome.org/download/chromosomal_feature_files/C_albicans_SC5314/C_albicans_SC5314_A22_current_chromosomal_feature.tab

cd ../uniprot
#wget -m -nd ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/idmapping_selected.tab.gz
wget -m -nd ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot_varsplic.fasta.gz

cd ../pombase
wget -m -nd ftp://ftp.ebi.ac.uk/pub/databases/pombase/pombe/Mappings/sysID2product.tsv

cd ../wormbase
wget -m -nd ftp://ftp.wormbase.org/pub/wormbase/releases/WS246/species/c_elegans/PRJNA13758/annotation/c_elegans.PRJNA13758.WS246.functional_descriptions.txt.gz
wget -m -nd ftp://ftp.wormbase.org/pub/wormbase/releases/WS246/species/c_elegans/PRJNA13758/annotation/c_elegans.PRJNA13758.WS246.geneOtherIDs.txt.gz