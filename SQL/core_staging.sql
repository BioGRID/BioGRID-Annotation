-- MySQL dump 10.13  Distrib 5.5.43, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: core_staging
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
-- Table structure for table `entrez_gene_history`
--

DROP TABLE IF EXISTS `entrez_gene_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `entrez_gene_history` (
  `tax_id` bigint(10) NOT NULL,
  `gene_id` bigint(10) NOT NULL,
  `discontinued_gene_id` bigint(10) NOT NULL,
  `discontinued_symbol` varchar(255) NOT NULL,
  `discontinued_date` date NOT NULL,
  `loaded_date` datetime NOT NULL,
  KEY `tax_id` (`tax_id`),
  KEY `gene_id` (`gene_id`),
  KEY `discontinued_gene_id` (`discontinued_gene_id`),
  KEY `discontinued_symbol` (`discontinued_symbol`),
  KEY `discontinued_date` (`discontinued_date`),
  KEY `loaded_date` (`loaded_date`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `refseq_protein_ids`
--

DROP TABLE IF EXISTS `refseq_protein_ids`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `refseq_protein_ids` (
  `refseq_protein_id` bigint(10) NOT NULL AUTO_INCREMENT,
  `refseq_protein_uid` bigint(10) NOT NULL,
  `refseq_protein_organism_id` bigint(10) NOT NULL,
  `refseq_protein_downloaded` enum('true','false') NOT NULL,
  PRIMARY KEY (`refseq_protein_id`),
  KEY `reseq_protein_uid` (`refseq_protein_uid`),
  KEY `reseq_protein_organism_id` (`refseq_protein_organism_id`),
  KEY `refseq_protein_downloaded` (`refseq_protein_downloaded`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `swissprot_ids`
--

DROP TABLE IF EXISTS `swissprot_ids`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `swissprot_ids` (
  `accession` varchar(25) NOT NULL,
  KEY `accession` (`accession`)
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
