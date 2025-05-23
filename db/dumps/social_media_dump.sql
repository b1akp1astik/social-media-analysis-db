-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: social_media
-- ------------------------------------------------------
-- Server version	8.0.41

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `social_media`
--

/*!40000 DROP DATABASE IF EXISTS `social_media`*/;

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `social_media` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `social_media`;

--
-- Table structure for table `field`
--

DROP TABLE IF EXISTS `field`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `field` (
  `ProjectName` varchar(100) NOT NULL,
  `FieldName` varchar(50) NOT NULL,
  PRIMARY KEY (`ProjectName`,`FieldName`),
  CONSTRAINT `field_ibfk_1` FOREIGN KEY (`ProjectName`) REFERENCES `project` (`ProjectName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `field`
--

LOCK TABLES `field` WRITE;
/*!40000 ALTER TABLE `field` DISABLE KEYS */;
/*!40000 ALTER TABLE `field` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `institute`
--

DROP TABLE IF EXISTS `institute`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `institute` (
  `InstituteName` varchar(100) NOT NULL,
  PRIMARY KEY (`InstituteName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `institute`
--

LOCK TABLES `institute` WRITE;
/*!40000 ALTER TABLE `institute` DISABLE KEYS */;
/*!40000 ALTER TABLE `institute` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `post`
--

DROP TABLE IF EXISTS `post`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `post` (
  `MediaName` varchar(50) NOT NULL,
  `Username` varchar(40) NOT NULL,
  `TimePosted` datetime NOT NULL,
  `TextContent` text NOT NULL,
  `City` varchar(50) DEFAULT NULL,
  `State` varchar(50) DEFAULT NULL,
  `Country` varchar(50) DEFAULT NULL,
  `Likes` int DEFAULT '0',
  `Dislikes` int DEFAULT '0',
  `HasMultimedia` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`MediaName`,`Username`,`TimePosted`),
  CONSTRAINT `post_ibfk_1` FOREIGN KEY (`MediaName`, `Username`) REFERENCES `user` (`MediaName`, `Username`),
  CONSTRAINT `post_chk_1` CHECK ((`Likes` >= 0)),
  CONSTRAINT `post_chk_2` CHECK ((`Dislikes` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `post`
--

LOCK TABLES `post` WRITE;
/*!40000 ALTER TABLE `post` DISABLE KEYS */;
/*!40000 ALTER TABLE `post` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `postanalysis`
--

DROP TABLE IF EXISTS `postanalysis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `postanalysis` (
  `ProjectName` varchar(100) NOT NULL,
  `FieldName` varchar(50) NOT NULL,
  `MediaName` varchar(50) NOT NULL,
  `Username` varchar(40) NOT NULL,
  `TimePosted` datetime NOT NULL,
  `Value` text,
  PRIMARY KEY (`ProjectName`,`FieldName`,`MediaName`,`Username`,`TimePosted`),
  KEY `MediaName` (`MediaName`,`Username`,`TimePosted`),
  CONSTRAINT `postanalysis_ibfk_1` FOREIGN KEY (`ProjectName`, `FieldName`) REFERENCES `field` (`ProjectName`, `FieldName`),
  CONSTRAINT `postanalysis_ibfk_2` FOREIGN KEY (`MediaName`, `Username`, `TimePosted`) REFERENCES `post` (`MediaName`, `Username`, `TimePosted`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `postanalysis`
--

LOCK TABLES `postanalysis` WRITE;
/*!40000 ALTER TABLE `postanalysis` DISABLE KEYS */;
/*!40000 ALTER TABLE `postanalysis` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project`
--

DROP TABLE IF EXISTS `project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project` (
  `ProjectName` varchar(100) NOT NULL,
  `ManagerFirstName` varchar(50) DEFAULT NULL,
  `ManagerLastName` varchar(50) DEFAULT NULL,
  `InstituteName` varchar(100) DEFAULT NULL,
  `StartDate` date DEFAULT NULL,
  `EndDate` date DEFAULT NULL,
  PRIMARY KEY (`ProjectName`),
  KEY `InstituteName` (`InstituteName`),
  CONSTRAINT `project_ibfk_1` FOREIGN KEY (`InstituteName`) REFERENCES `institute` (`InstituteName`),
  CONSTRAINT `project_chk_1` CHECK ((`EndDate` >= `StartDate`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project`
--

LOCK TABLES `project` WRITE;
/*!40000 ALTER TABLE `project` DISABLE KEYS */;
/*!40000 ALTER TABLE `project` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `projectpost`
--

DROP TABLE IF EXISTS `projectpost`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `projectpost` (
  `ProjectName` varchar(100) NOT NULL,
  `MediaName` varchar(50) NOT NULL,
  `Username` varchar(40) NOT NULL,
  `TimePosted` datetime NOT NULL,
  PRIMARY KEY (`ProjectName`,`MediaName`,`Username`,`TimePosted`),
  KEY `MediaName` (`MediaName`,`Username`,`TimePosted`),
  CONSTRAINT `projectpost_ibfk_1` FOREIGN KEY (`ProjectName`) REFERENCES `project` (`ProjectName`),
  CONSTRAINT `projectpost_ibfk_2` FOREIGN KEY (`MediaName`, `Username`, `TimePosted`) REFERENCES `post` (`MediaName`, `Username`, `TimePosted`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `projectpost`
--

LOCK TABLES `projectpost` WRITE;
/*!40000 ALTER TABLE `projectpost` DISABLE KEYS */;
/*!40000 ALTER TABLE `projectpost` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `repost`
--

DROP TABLE IF EXISTS `repost`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `repost` (
  `OrigMedia` varchar(50) NOT NULL,
  `OrigUser` varchar(40) NOT NULL,
  `OrigTime` datetime NOT NULL,
  `ReposterMedia` varchar(50) NOT NULL,
  `ReposterUser` varchar(40) NOT NULL,
  `RepostTime` datetime NOT NULL,
  PRIMARY KEY (`OrigMedia`,`OrigUser`,`OrigTime`,`ReposterMedia`,`ReposterUser`,`RepostTime`),
  KEY `ReposterMedia` (`ReposterMedia`,`ReposterUser`),
  CONSTRAINT `repost_ibfk_1` FOREIGN KEY (`OrigMedia`, `OrigUser`, `OrigTime`) REFERENCES `post` (`MediaName`, `Username`, `TimePosted`),
  CONSTRAINT `repost_ibfk_2` FOREIGN KEY (`ReposterMedia`, `ReposterUser`) REFERENCES `user` (`MediaName`, `Username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `repost`
--

LOCK TABLES `repost` WRITE;
/*!40000 ALTER TABLE `repost` DISABLE KEYS */;
/*!40000 ALTER TABLE `repost` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `socialmedia`
--

DROP TABLE IF EXISTS `socialmedia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `socialmedia` (
  `MediaName` varchar(50) NOT NULL,
  PRIMARY KEY (`MediaName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `socialmedia`
--

LOCK TABLES `socialmedia` WRITE;
/*!40000 ALTER TABLE `socialmedia` DISABLE KEYS */;
/*!40000 ALTER TABLE `socialmedia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `MediaName` varchar(50) NOT NULL,
  `Username` varchar(40) NOT NULL,
  `FirstName` varchar(50) DEFAULT NULL,
  `LastName` varchar(50) DEFAULT NULL,
  `CountryOfBirth` varchar(50) DEFAULT NULL,
  `CountryOfResidence` varchar(50) DEFAULT NULL,
  `Age` int DEFAULT NULL,
  `Gender` enum('Male','Female','Other') DEFAULT NULL,
  `IsVerified` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`MediaName`,`Username`),
  CONSTRAINT `user_ibfk_1` FOREIGN KEY (`MediaName`) REFERENCES `socialmedia` (`MediaName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'social_media'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-04-18  4:24:49
