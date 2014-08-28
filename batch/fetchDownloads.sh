#!/bin/bash
baseDir="../downloads"

cd $baseDir/entrez_gene
# wget -m -nd ftp://ftp.ncbi.nih.gov/gene/DATA/gene_info.gz
# wget -m -nd ftp://ftp.ncbi.nih.gov/gene/DATA/gene_history.gz
# wget -m -nd ftp://ftp.ncbi.nih.gov/gene/DATA/gene_refseq_uniprotkb_collab.gz
# wget -m -nd ftp://ftp.ncbi.nih.gov/gene/DATA/gene2refseq.gz
# wget -m -nd ftp://ftp.ncbi.nih.gov/gene/DATA/gene2go.gz
# wget -m -nd ftp://ftp.ncbi.nih.gov/gene/DATA/gene_group.gz
# wget -m -nd ftp://ftp.ncbi.nih.gov/gene/DATA/gene2ensembl.gz
# wget -m -nd ftp://ftp.ncbi.nih.gov/gene/DATA/gene2accession.gz

# cd $basedir/go
# wget -m -nd http://archive.geneontology.org/latest-termdb/go_daily-termdb.obo-xml.gz

# cd $basedir/psi
# wget -m -nd http://psidev.cvs.sourceforge.net/viewvc/*checkout*/psidev/psi/mi/rel25/data/psi-mi25.obo

# cd $basedir/sgd
# wget -m -nd http://downloads.yeastgenome.org/curation/chromosomal_feature/SGD_features.tab

# cd $basedir/cgd
# wget -m -nd http://www.candidagenome.org/download/chromosomal_feature_files/C_albicans_SC5314/C_albicans_SC5314_A22_current_chromosomal_feature.tab

# cd $basedir/uniprot
# wget -m -nd ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.xml.gz
# wget -m -nd ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_trembl.xml.gz
# wget -m -nd ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/idmapping_selected.tab.gz
# wget -m -nd ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot_varsplic.fasta.gz

# cd $basedir/refseq/protein
# rm -f *.faa
# wget -m -nd ftp://ftp.ncbi.nih.gov/refseq/release/complete/*.protein.faa.gz

# cd $basedir/refseq/dna
# rm -f *.fna
# wget -m -nd ftp://ftp.ncbi.nih.gov/refseq/release/complete/*.rna.fna.gz