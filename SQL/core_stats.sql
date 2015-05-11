-- MySQL dump 10.13  Distrib 5.5.43, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: core_stats
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
-- Table structure for table `gene_history`
--

DROP TABLE IF EXISTS `gene_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gene_history` (
  `gene_history_id` bigint(10) unsigned NOT NULL AUTO_INCREMENT,
  `modification_type` enum('DISCONTINUED','MODIFY_EG','MODIFY_SP','LOADED') NOT NULL,
  `gene_id` bigint(10) NOT NULL,
  `old_id` varchar(255) NOT NULL,
  `new_id` varchar(255) NOT NULL,
  `gene_history_comment` text NOT NULL,
  `gene_history_datetime` datetime NOT NULL,
  PRIMARY KEY (`gene_history_id`),
  KEY `modification_type` (`modification_type`),
  KEY `gene_id` (`gene_id`),
  KEY `gene_history_datetime` (`gene_history_datetime`),
  KEY `new_id` (`new_id`),
  KEY `old_id` (`old_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `refseq_files_processed`
--

DROP TABLE IF EXISTS `refseq_files_processed`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `refseq_files_processed` (
  `refseq_file_id` int(11) NOT NULL AUTO_INCREMENT,
  `refseq_file_name` varchar(255) NOT NULL,
  `refseq_file_processed` datetime NOT NULL,
  PRIMARY KEY (`refseq_file_id`),
  KEY `refseq_file_name` (`refseq_file_name`),
  KEY `refseq_file_processed` (`refseq_file_processed`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `update_tracker`
--

DROP TABLE IF EXISTS `update_tracker`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `update_tracker` (
  `update_tracker_id` bigint(10) NOT NULL AUTO_INCREMENT,
  `update_tracker_name` varchar(255) NOT NULL,
  `update_tracker_processed_date` datetime NOT NULL,
  PRIMARY KEY (`update_tracker_id`),
  KEY `update_tracker_name` (`update_tracker_name`),
  KEY `update_tracker_processed` (`update_tracker_processed_date`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
