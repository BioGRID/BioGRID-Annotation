-- MySQL dump 10.13  Distrib 5.5.43, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: core
-- ------------------------------------------------------
-- Server version	5.5.43-0ubuntu0.14.04.1-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `gene_aliases`
--

DROP TABLE IF EXISTS `gene_aliases`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gene_aliases` (
  `gene_alias_id` bigint(10) unsigned NOT NULL AUTO_INCREMENT,
  `gene_alias_value` varchar(255) NOT NULL,
  `gene_alias_status` enum('active','inactive') NOT NULL DEFAULT 'active',
  `gene_alias_type` enum('primary','synonym','orf','ordered locus','entrez-official','sgd-official','pombase-official','cgd-official','wormbase-official') NOT NULL,
  `gene_alias_modified` datetime NOT NULL,
  `gene_id` bigint(10) NOT NULL DEFAULT '0',
  PRIMARY KEY (`gene_alias_id`),
  KEY `alias_value` (`gene_alias_value`),
  KEY `alias_status` (`gene_alias_status`),
  KEY `alias_type_id` (`gene_alias_type`),
  KEY `alias_modified` (`gene_alias_modified`),
  KEY `gene_id` (`gene_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gene_definitions`
--

DROP TABLE IF EXISTS `gene_definitions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gene_definitions` (
  `gene_definition_id` bigint(10) unsigned NOT NULL AUTO_INCREMENT,
  `gene_definition_text` mediumtext NOT NULL,
  `gene_definition_source` varchar(255) NOT NULL,
  `gene_definition_status` enum('active','inactive') NOT NULL DEFAULT 'active',
  `gene_definition_modified` datetime NOT NULL,
  `gene_id` bigint(10) NOT NULL DEFAULT '0',
  PRIMARY KEY (`gene_definition_id`),
  KEY `definition_status` (`gene_definition_status`),
  KEY `definition_modified` (`gene_definition_modified`),
  KEY `gene_id` (`gene_id`),
  KEY `definition_type` (`gene_definition_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gene_externals`
--

DROP TABLE IF EXISTS `gene_externals`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gene_externals` (
  `gene_external_id` bigint(10) unsigned NOT NULL AUTO_INCREMENT,
  `gene_external_value` varchar(255) NOT NULL,
  `gene_external_source` varchar(255) NOT NULL,
  `gene_external_status` enum('active','inactive') NOT NULL DEFAULT 'active',
  `gene_external_modified` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `gene_id` bigint(10) NOT NULL DEFAULT '0',
  PRIMARY KEY (`gene_external_id`),
  KEY `external_value` (`gene_external_value`),
  KEY `external_status` (`gene_external_status`),
  KEY `external_modified` (`gene_external_modified`),
  KEY `gene_id` (`gene_id`),
  KEY `external_source_id` (`gene_external_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 PACK_KEYS=0;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gene_go`
--

DROP TABLE IF EXISTS `gene_go`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gene_go` (
  `gene_go_id` bigint(10) NOT NULL AUTO_INCREMENT,
  `go_id` bigint(10) NOT NULL DEFAULT '0',
  `go_evidence_code_id` bigint(10) NOT NULL DEFAULT '0',
  `gene_go_status` enum('active','inactive') NOT NULL DEFAULT 'active',
  `gene_go_modified` datetime NOT NULL,
  `gene_id` bigint(10) NOT NULL,
  PRIMARY KEY (`gene_go_id`),
  KEY `go_id` (`go_id`),
  KEY `go_evidence_code_id` (`go_evidence_code_id`),
  KEY `go_mapping_status` (`gene_go_status`),
  KEY `go_mapping_modified` (`gene_go_modified`),
  KEY `gene_id` (`gene_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gene_refseqs`
--

DROP TABLE IF EXISTS `gene_refseqs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gene_refseqs` (
  `gene_refseq_id` bigint(10) unsigned NOT NULL AUTO_INCREMENT,
  `refseq_id` bigint(10) NOT NULL,
  `refseq_status` varchar(255) NOT NULL,
  `gene_refseq_status` enum('active','inactive') NOT NULL DEFAULT 'active',
  `gene_refseq_modified` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `gene_id` bigint(10) NOT NULL,
  PRIMARY KEY (`gene_refseq_id`),
  KEY `external_value` (`refseq_id`),
  KEY `external_status` (`gene_refseq_status`),
  KEY `external_modified` (`gene_refseq_modified`),
  KEY `refseq_status` (`refseq_status`),
  KEY `gene_id` (`gene_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 PACK_KEYS=0;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `genes`
--

DROP TABLE IF EXISTS `genes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `genes` (
  `gene_id` bigint(10) unsigned NOT NULL AUTO_INCREMENT,
  `gene_name` varchar(255) DEFAULT NULL,
  `gene_name_type` varchar(255) DEFAULT NULL,
  `gene_source_id` varchar(255) DEFAULT NULL,
  `gene_type` varchar(30) NOT NULL,
  `organism_id` bigint(10) unsigned NOT NULL DEFAULT '0',
  `gene_status` enum('active','inactive') NOT NULL DEFAULT 'active',
  `gene_added` datetime NOT NULL,
  `gene_updated` datetime NOT NULL,
  `gene_source` varchar(255) DEFAULT NULL,
  `interaction_count` bigint(10) DEFAULT NULL,
  PRIMARY KEY (`gene_id`),
  KEY `gene_entrez_id` (`gene_source_id`),
  KEY `organism_id` (`organism_id`),
  KEY `gene_status` (`gene_status`),
  KEY `gene_modified` (`gene_added`),
  KEY `gene_type` (`gene_type`),
  KEY `interaction_count` (`interaction_count`),
  KEY `gene_source` (`gene_source`),
  KEY `gene_name_type` (`gene_name_type`),
  KEY `gene_updated` (`gene_updated`),
  KEY `gene_name` (`gene_name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `go_definitions`
--

DROP TABLE IF EXISTS `go_definitions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `go_definitions` (
  `go_id` bigint(10) NOT NULL DEFAULT '0',
  `go_full_id` varchar(10) NOT NULL DEFAULT '',
  `go_name` text NOT NULL,
  `go_definition` text NOT NULL,
  `go_type` varchar(50) NOT NULL DEFAULT 'unknown',
  `go_modified` datetime DEFAULT NULL,
  `go_status` enum('active','inactive') NOT NULL DEFAULT 'active',
  PRIMARY KEY (`go_id`),
  KEY `go_full_id` (`go_full_id`),
  KEY `go_type` (`go_type`),
  KEY `go_modified` (`go_modified`),
  KEY `go_status` (`go_status`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `go_evidence_codes`
--

DROP TABLE IF EXISTS `go_evidence_codes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `go_evidence_codes` (
  `go_evidence_code_id` bigint(10) unsigned NOT NULL AUTO_INCREMENT,
  `go_evidence_code_symbol` char(3) NOT NULL DEFAULT '',
  `go_evidence_code_name` varchar(255) NOT NULL DEFAULT '',
  `go_evidence_code_modified` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `go_evidence_code_status` enum('active','inactive') NOT NULL DEFAULT 'active',
  PRIMARY KEY (`go_evidence_code_id`),
  KEY `go_evidence_code_symbol` (`go_evidence_code_symbol`),
  KEY `go_evidence_code_name` (`go_evidence_code_name`),
  KEY `go_evidence_code_modified` (`go_evidence_code_modified`),
  KEY `go_evidence_code_status` (`go_evidence_code_status`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `go_relationships`
--

DROP TABLE IF EXISTS `go_relationships`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `go_relationships` (
  `go_relationship_id` bigint(10) unsigned NOT NULL AUTO_INCREMENT,
  `go_child_id` bigint(10) NOT NULL DEFAULT '0',
  `go_parent_id` bigint(10) NOT NULL DEFAULT '0',
  `go_relationship_status` enum('active','inactive') NOT NULL DEFAULT 'active',
  PRIMARY KEY (`go_relationship_id`),
  KEY `go_child_id` (`go_child_id`),
  KEY `go_parent_id` (`go_parent_id`),
  KEY `go_relationship_status` (`go_relationship_status`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `go_special_mappings`
--

DROP TABLE IF EXISTS `go_special_mappings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `go_special_mappings` (
  `go_special_mapping_id` bigint(10) unsigned NOT NULL AUTO_INCREMENT,
  `go_id` bigint(20) NOT NULL DEFAULT '0',
  `go_special_id` varchar(30) NOT NULL DEFAULT '0',
  `go_special_mapping_status` enum('active','inactive') NOT NULL DEFAULT 'active',
  PRIMARY KEY (`go_special_mapping_id`),
  KEY `go_id` (`go_id`),
  KEY `go_special_id` (`go_special_id`),
  KEY `go_special_mapping_status` (`go_special_mapping_status`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `go_subset_mappings`
--

DROP TABLE IF EXISTS `go_subset_mappings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `go_subset_mappings` (
  `go_subset_mapping_id` bigint(10) unsigned NOT NULL AUTO_INCREMENT,
  `go_id` bigint(10) NOT NULL,
  `go_subset_id` bigint(10) NOT NULL,
  `go_subset_mapping_status` enum('active','inactive') NOT NULL,
  PRIMARY KEY (`go_subset_mapping_id`),
  KEY `go_id` (`go_id`),
  KEY `go_subset_id` (`go_subset_id`),
  KEY `go_subset_mapping_status` (`go_subset_mapping_status`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `go_subset_pairings`
--

DROP TABLE IF EXISTS `go_subset_pairings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `go_subset_pairings` (
  `go_subset_pairing_id` bigint(10) unsigned NOT NULL AUTO_INCREMENT,
  `go_id` bigint(10) NOT NULL,
  `go_subset_id` bigint(10) NOT NULL,
  `go_pairing_id` bigint(10) NOT NULL,
  `go_subset_pairing_status` enum('active','inactive') NOT NULL,
  PRIMARY KEY (`go_subset_pairing_id`),
  KEY `go_id` (`go_id`),
  KEY `go_subset_id` (`go_subset_id`),
  KEY `go_parent_id` (`go_pairing_id`),
  KEY `go_subset_parent_status` (`go_subset_pairing_status`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `go_subsets`
--

DROP TABLE IF EXISTS `go_subsets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `go_subsets` (
  `go_subset_id` bigint(10) unsigned NOT NULL AUTO_INCREMENT,
  `go_subset_name` varchar(255) NOT NULL,
  `go_subset_desc` varchar(255) NOT NULL,
  `go_subset_addeddate` datetime NOT NULL,
  `go_subset_status` enum('active','inactive') NOT NULL,
  PRIMARY KEY (`go_subset_id`),
  KEY `go_subset_name` (`go_subset_name`),
  KEY `go_subset_addeddate` (`go_subset_addeddate`),
  KEY `go_subset_status` (`go_subset_status`),
  KEY `go_subset_desc` (`go_subset_desc`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `organisms`
--

DROP TABLE IF EXISTS `organisms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `organisms` (
  `organism_id` bigint(10) NOT NULL DEFAULT '0',
  `entrez_taxid` bigint(10) NOT NULL,
  `organism_common_name` varchar(255) NOT NULL DEFAULT '',
  `organism_official_name` varchar(255) NOT NULL DEFAULT '',
  `organism_abbreviation` varchar(255) NOT NULL,
  `organism_strain` varchar(255) NOT NULL,
  `organism_status` enum('active','inactive') NOT NULL DEFAULT 'active',
  PRIMARY KEY (`organism_id`),
  KEY `organism_common_name` (`organism_common_name`),
  KEY `organism_official_name` (`organism_official_name`),
  KEY `organism_status` (`organism_status`),
  KEY `organism_display_name` (`organism_abbreviation`),
  KEY `organism_taxid` (`entrez_taxid`),
  KEY `organism_strain` (`organism_strain`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `protein_mapping`
--

DROP TABLE IF EXISTS `protein_mapping`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `protein_mapping` (
  `protein_mapping_id` bigint(10) NOT NULL AUTO_INCREMENT,
  `refseq_id` bigint(10) NOT NULL,
  `uniprot_id` bigint(10) NOT NULL,
  `protein_mapping_status` enum('active','inactive') NOT NULL,
  `protein_mapping_added` datetime NOT NULL,
  PRIMARY KEY (`protein_mapping_id`),
  KEY `refseq_id` (`refseq_id`),
  KEY `uniprot_id` (`uniprot_id`),
  KEY `protein_mapping_status` (`protein_mapping_status`),
  KEY `protein_mapping_added` (`protein_mapping_added`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `refseq`
--

DROP TABLE IF EXISTS `refseq`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `refseq` (
  `refseq_id` bigint(10) unsigned NOT NULL AUTO_INCREMENT,
  `refseq_accession` varchar(255) DEFAULT NULL,
  `refseq_gi` bigint(10) DEFAULT NULL,
  `refseq_sequence` longtext NOT NULL,
  `refseq_length` bigint(10) DEFAULT NULL,
  `refseq_description` text NOT NULL,
  `refseq_version` bigint(10) NOT NULL,
  `organism_id` bigint(10) NOT NULL,
  `refseq_modified` datetime NOT NULL,
  `refseq_status` enum('active','inactive') NOT NULL DEFAULT 'active',
  PRIMARY KEY (`refseq_id`),
  KEY `protein_modified` (`refseq_modified`),
  KEY `protein_status` (`refseq_status`),
  KEY `refseq_protein_sequence` (`refseq_sequence`(40)),
  KEY `refseq_protein_description` (`refseq_description`(50)),
  KEY `refseq_identifier_value` (`refseq_accession`),
  KEY `organism_id` (`organism_id`),
  KEY `refseq_protein_version` (`refseq_version`),
  KEY `refseq_length` (`refseq_length`),
  KEY `refseq_gi` (`refseq_gi`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `refseq_identifiers`
--

DROP TABLE IF EXISTS `refseq_identifiers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `refseq_identifiers` (
  `refseq_identifier_id` bigint(10) unsigned NOT NULL AUTO_INCREMENT,
  `refseq_identifier_value` varchar(255) NOT NULL,
  `refseq_identifier_type` enum('protein-accession','protein-gi','rna-accession','rna-gi') NOT NULL,
  `refseq_identifier_version` bigint(10) NOT NULL,
  `refseq_identifier_status` enum('active','inactive') NOT NULL,
  `refseq_identifier_modified` datetime NOT NULL,
  `refseq_id` bigint(10) NOT NULL DEFAULT '0',
  PRIMARY KEY (`refseq_identifier_id`),
  KEY `alias_value` (`refseq_identifier_value`),
  KEY `alias_type_id` (`refseq_identifier_type`),
  KEY `alias_modified` (`refseq_identifier_modified`),
  KEY `gene_id` (`refseq_id`),
  KEY `refseq_identifier_version` (`refseq_identifier_version`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `uniprot`
--

DROP TABLE IF EXISTS `uniprot`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `uniprot` (
  `uniprot_id` bigint(10) unsigned NOT NULL AUTO_INCREMENT,
  `uniprot_identifier_value` varchar(255) NOT NULL,
  `uniprot_sequence` longtext,
  `uniprot_sequence_length` bigint(10) NOT NULL,
  `uniprot_name` varchar(255) NOT NULL,
  `uniprot_description` text,
  `uniprot_source` varchar(255) DEFAULT NULL,
  `uniprot_version` bigint(10) DEFAULT NULL,
  `uniprot_curation_status` varchar(255) NOT NULL,
  `uniprot_status` enum('active','inactive') DEFAULT NULL,
  `uniprot_added` datetime DEFAULT NULL,
  `organism_id` bigint(10) NOT NULL,
  PRIMARY KEY (`uniprot_id`),
  KEY `sequence_identifier_value` (`uniprot_identifier_value`),
  KEY `sequence_identifier_status` (`uniprot_status`),
  KEY `sequence_identifier_added` (`uniprot_added`),
  KEY `sequence_identifier_source_id` (`uniprot_source`),
  KEY `refseq_identifier_version` (`uniprot_version`),
  KEY `uniprot_name` (`uniprot_name`),
  KEY `protein_curation_status` (`uniprot_curation_status`),
  KEY `organism_id` (`organism_id`),
  KEY `uniprot_sequence_length` (`uniprot_sequence_length`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `uniprot_aliases`
--

DROP TABLE IF EXISTS `uniprot_aliases`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `uniprot_aliases` (
  `uniprot_alias_id` bigint(10) unsigned NOT NULL AUTO_INCREMENT,
  `uniprot_alias_value` varchar(255) NOT NULL,
  `uniprot_alias_type` varchar(255) NOT NULL,
  `uniprot_alias_status` enum('active','inactive') NOT NULL DEFAULT 'active',
  `uniprot_alias_modified` datetime NOT NULL,
  `uniprot_id` bigint(10) NOT NULL DEFAULT '0',
  PRIMARY KEY (`uniprot_alias_id`),
  KEY `alias_value` (`uniprot_alias_value`),
  KEY `alias_status` (`uniprot_alias_status`),
  KEY `alias_modified` (`uniprot_alias_modified`),
  KEY `gene_id` (`uniprot_id`),
  KEY `protein_alias_type` (`uniprot_alias_type`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `uniprot_definitions`
--

DROP TABLE IF EXISTS `uniprot_definitions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `uniprot_definitions` (
  `uniprot_definition_id` bigint(10) unsigned NOT NULL AUTO_INCREMENT,
  `uniprot_definition_text` mediumtext NOT NULL,
  `uniprot_definition_source` varchar(255) NOT NULL,
  `uniprot_definition_status` enum('active','inactive') NOT NULL DEFAULT 'active',
  `uniprot_definition_modified` datetime NOT NULL,
  `uniprot_id` bigint(10) NOT NULL DEFAULT '0',
  PRIMARY KEY (`uniprot_definition_id`),
  KEY `definition_status` (`uniprot_definition_status`),
  KEY `definition_modified` (`uniprot_definition_modified`),
  KEY `gene_id` (`uniprot_id`),
  KEY `definition_type` (`uniprot_definition_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `uniprot_externals`
--

DROP TABLE IF EXISTS `uniprot_externals`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `uniprot_externals` (
  `uniprot_external_id` bigint(10) unsigned NOT NULL AUTO_INCREMENT,
  `uniprot_external_value` varchar(255) NOT NULL,
  `uniprot_external_source` varchar(255) NOT NULL,
  `uniprot_external_status` enum('active','inactive') NOT NULL DEFAULT 'active',
  `uniprot_external_modified` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `uniprot_id` bigint(10) NOT NULL DEFAULT '0',
  PRIMARY KEY (`uniprot_external_id`),
  KEY `external_value` (`uniprot_external_value`),
  KEY `external_status` (`uniprot_external_status`),
  KEY `external_modified` (`uniprot_external_modified`),
  KEY `gene_id` (`uniprot_id`),
  KEY `external_source_id` (`uniprot_external_source`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 PACK_KEYS=0;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `uniprot_features`
--

DROP TABLE IF EXISTS `uniprot_features`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `uniprot_features` (
  `uniprot_feature_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `uniprot_feature_type` varchar(255) NOT NULL,
  `uniprot_feature_description` text NOT NULL,
  `uniprot_feature_external_id` varchar(255) NOT NULL,
  `uniprot_feature_start` bigint(10) NOT NULL,
  `uniprot_feature_end` bigint(10) NOT NULL,
  `uniprot_feature_position` bigint(10) NOT NULL,
  `uniprot_feature_status` enum('active','inactive') NOT NULL,
  `uniprot_feature_added` datetime NOT NULL,
  `uniprot_id` bigint(10) NOT NULL,
  PRIMARY KEY (`uniprot_feature_id`),
  KEY `uniprot_feature_type` (`uniprot_feature_type`),
  KEY `uniprot_feature_external_id` (`uniprot_feature_external_id`),
  KEY `uniprot_feature_start` (`uniprot_feature_start`),
  KEY `uniprot_feature_end` (`uniprot_feature_end`),
  KEY `uniprot_feature_position` (`uniprot_feature_position`),
  KEY `uniprot_feature_status` (`uniprot_feature_status`),
  KEY `uniprot_feature_added` (`uniprot_feature_added`),
  KEY `uniprot_id` (`uniprot_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `uniprot_go`
--

DROP TABLE IF EXISTS `uniprot_go`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `uniprot_go` (
  `uniprot_go_id` bigint(10) NOT NULL AUTO_INCREMENT,
  `go_id` bigint(10) NOT NULL DEFAULT '0',
  `go_evidence_code_id` bigint(10) NOT NULL DEFAULT '0',
  `uniprot_go_status` enum('active','inactive') NOT NULL DEFAULT 'active',
  `uniprot_go_modified` datetime NOT NULL,
  `uniprot_id` bigint(10) NOT NULL,
  PRIMARY KEY (`uniprot_go_id`),
  KEY `go_id` (`go_id`),
  KEY `go_evidence_code_id` (`go_evidence_code_id`),
  KEY `go_mapping_status` (`uniprot_go_status`),
  KEY `go_mapping_modified` (`uniprot_go_modified`),
  KEY `gene_id` (`uniprot_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `uniprot_isoforms`
--

DROP TABLE IF EXISTS `uniprot_isoforms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `uniprot_isoforms` (
  `uniprot_isoform_id` bigint(10) NOT NULL AUTO_INCREMENT,
  `uniprot_isoform_accession` varchar(255) NOT NULL,
  `uniprot_isoform_number` bigint(10) NOT NULL,
  `uniprot_isoform_sequence` longtext NOT NULL,
  `uniprot_isoform_sequence_length` bigint(10) NOT NULL,
  `uniprot_isoform_name` varchar(255) NOT NULL,
  `uniprot_isoform_description` text NOT NULL,
  `uniprot_isoform_status` enum('active','inactive') NOT NULL,
  `uniprot_isoform_added` datetime NOT NULL,
  `organism_id` bigint(10) NOT NULL,
  `uniprot_id` bigint(10) NOT NULL,
  PRIMARY KEY (`uniprot_isoform_id`),
  KEY `uniprot_isoform_accession` (`uniprot_isoform_accession`),
  KEY `uniprot_isoform_number` (`uniprot_isoform_number`),
  KEY `uniprot_isoform_sequence_length` (`uniprot_isoform_sequence_length`),
  KEY `uniprot_isoform_name` (`uniprot_isoform_name`),
  KEY `uniprot_isoform_status` (`uniprot_isoform_status`),
  KEY `uniprot_isoform_added` (`uniprot_isoform_added`),
  KEY `organism_id` (`organism_id`),
  KEY `uniprot_id` (`uniprot_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
