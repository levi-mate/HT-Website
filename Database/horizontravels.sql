-- MySQL dump 10.13  Distrib 8.0.20, for Win64 (x86_64)
--
-- Host: localhost    Database: horizontravels
-- ------------------------------------------------------
-- Server version	8.0.20

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `account`
--

DROP TABLE IF EXISTS `account`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account` (
  `aid` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `firstName` varchar(50) NOT NULL,
  `lastName` varchar(50) NOT NULL,
  `email` varchar(50) NOT NULL,
  `password_hash` varchar(500) NOT NULL,
  `password_salt` varchar(40) NOT NULL,
  `usertype` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL DEFAULT 'basic',
  PRIMARY KEY (`aid`),
  UNIQUE KEY `Email_UNIQUE` (`email`),
  UNIQUE KEY `UserName_UNIQUE` (`username`),
  UNIQUE KEY `Password_UNIQUE` (`password_hash`),
  UNIQUE KEY `AccountID_UNIQUE` (`aid`),
  UNIQUE KEY `password_salt_UNIQUE` (`password_salt`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account`
--

LOCK TABLES `account` WRITE;
/*!40000 ALTER TABLE `account` DISABLE KEYS */;
INSERT INTO `account` VALUES (0,'DEFAULT','DEFAULT','DEFAULT','DEFAULT@DEFAULT.DEFAULT','$5$rounds=535000$ySSEO/HyQqOqzyRu$j7JO2Yjej1ivsWCcEraTd1HJIED3jSnG6eoFtAuGYs7','2023-05-01 14:02:00.700670','DEFAULT'),(1,'admin','Admin','Jones','admin@uwe.co.uk','$5$rounds=535000$Ad7JF/s/qh02wGRC$t8.87FFzPB8myijSsyi/LIuq1f/8xKGhnh1GjcjOuW2','2023-05-01 13:59:15.182029','admin'),(15,'test1','Test','Smith','test1@test.co.uk','$5$rounds=535000$sidTSeaQ9Kvnhw7G$NKzjQ/Pxl7fMMiwIqyd1m/KPBhwmjmNha5FYpb2Om/7','2023-05-01 14:03:22.442504','basic'),(16,'test2','Test','Raynolds','test2@test.co.uk','$5$rounds=535000$MWpe.QHNlLGkMXl/$yIQ4j6b41pHDzvAwvQ89aG/.alBx3fdsWkd6/uzFTa6','2023-05-01 14:04:30.195246','basic'),(17,'test3','Test','Ing','test3@test.co.uk','$5$rounds=535000$uehExGZSbYeCWxqD$GJk2c1CmijzVAc6WXsOSwzd92GwCD/IvKTqnlGHcMG1','2023-05-01 14:05:30.725753','basic');
/*!40000 ALTER TABLE `account` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `basket`
--

DROP TABLE IF EXISTS `basket`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `basket` (
  `basketid` int NOT NULL AUTO_INCREMENT,
  `aid` int NOT NULL,
  `cityD` varchar(50) NOT NULL,
  `cityA` varchar(50) NOT NULL,
  `dateD` datetime NOT NULL,
  `dateRD` datetime NOT NULL,
  `seatS` int NOT NULL,
  `seatB` int NOT NULL,
  PRIMARY KEY (`basketid`),
  UNIQUE KEY `basketid_UNIQUE` (`basketid`),
  UNIQUE KEY `aid_UNIQUE` (`aid`),
  KEY `aid_idx` (`aid`),
  CONSTRAINT `accountid` FOREIGN KEY (`aid`) REFERENCES `account` (`aid`)
) ENGINE=InnoDB AUTO_INCREMENT=63 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `basket`
--

LOCK TABLES `basket` WRITE;
/*!40000 ALTER TABLE `basket` DISABLE KEYS */;
/*!40000 ALTER TABLE `basket` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bookings`
--

DROP TABLE IF EXISTS `bookings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bookings` (
  `bid` int NOT NULL AUTO_INCREMENT,
  `jid` int NOT NULL,
  `jidR` int DEFAULT NULL,
  `aid` int NOT NULL,
  `cityD` varchar(50) NOT NULL,
  `cityA` varchar(50) NOT NULL,
  `dateD` datetime NOT NULL,
  `cityRD` varchar(50) DEFAULT NULL,
  `cityRA` varchar(50) DEFAULT NULL,
  `dateRD` datetime DEFAULT NULL,
  `seatS` int NOT NULL DEFAULT '1',
  `seatB` int NOT NULL DEFAULT '0',
  `pricetotal` double NOT NULL,
  `bookedOn` datetime NOT NULL,
  PRIMARY KEY (`bid`),
  UNIQUE KEY `bid_UNIQUE` (`bid`),
  KEY `jid_idx` (`jid`),
  KEY `aid_idx` (`aid`),
  CONSTRAINT `aid` FOREIGN KEY (`aid`) REFERENCES `account` (`aid`),
  CONSTRAINT `jid` FOREIGN KEY (`jid`) REFERENCES `journeys` (`jid`)
) ENGINE=InnoDB AUTO_INCREMENT=84 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bookings`
--

LOCK TABLES `bookings` WRITE;
/*!40000 ALTER TABLE `bookings` DISABLE KEYS */;
INSERT INTO `bookings` VALUES (77,1003,1011,15,'Bristol','Manchester','2023-05-01 11:30:00','Manchester','Bristol','2023-05-13 18:25:00',2,0,240,'2023-05-01 18:31:11'),(78,1013,0,15,'Portsmouth','Dundee','2023-05-18 12:00:00','NORETURN','NORETURN','1980-01-01 00:00:00',0,1,200,'2023-05-01 18:31:29'),(79,1002,0,15,'Cardiff','Edinburgh','2023-05-25 06:00:00','NORETURN','NORETURN','1980-01-01 00:00:00',1,2,400,'2023-05-01 18:32:00'),(80,1014,0,16,'Dundee','Portsmouth','2023-05-17 10:00:00','NORETURN','NORETURN','1980-01-01 00:00:00',0,3,600,'2023-05-01 18:32:40'),(81,1020,0,16,'Aberdeen','Portsmouth','2023-05-16 07:00:00','NORETURN','NORETURN','1980-01-01 00:00:00',1,0,75,'2023-05-01 18:32:49'),(82,1015,0,17,'Edinburgh','Cardiff','2023-05-19 18:30:00','NORETURN','NORETURN','1980-01-01 00:00:00',1,0,75,'2023-05-01 18:33:14');
/*!40000 ALTER TABLE `bookings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `journeys`
--

DROP TABLE IF EXISTS `journeys`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `journeys` (
  `jid` int NOT NULL AUTO_INCREMENT,
  `cityD` varchar(45) NOT NULL,
  `timeD` varchar(5) NOT NULL,
  `cityA` varchar(45) NOT NULL,
  `timeA` varchar(45) NOT NULL,
  `price` double NOT NULL,
  PRIMARY KEY (`jid`),
  UNIQUE KEY `jid_UNIQUE` (`jid`)
) ENGINE=InnoDB AUTO_INCREMENT=1031 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `journeys`
--

LOCK TABLES `journeys` WRITE;
/*!40000 ALTER TABLE `journeys` DISABLE KEYS */;
INSERT INTO `journeys` VALUES (1000,'Newcastle','16:45','Bristol','18:00',80),(1001,'Bristol','08:00','Newcastle','09:15',80),(1002,'Cardiff','06:00','Edinburgh','07:30',80),(1003,'Bristol','11:30','Manchester','12:30',60),(1004,'Manchester','12:20','Bristol','13:20',60),(1005,'Bristol','07:40','London','08:20',60),(1006,'London','11:00','Manchester','12:20',75),(1007,'Manchester','12:20','Glasgow','13:30',75),(1008,'Bristol','07:40','Glasgow','08:45',90),(1009,'Glasgow','14:30','Newcastle','15:45',75),(1010,'Newcastle','16:15','Manchester','17:05',75),(1011,'Manchester','18:25','Bristol','19:30',60),(1012,'Bristol','06:20','Manchester','07:20',60),(1013,'Portsmouth','12:00','Dundee','14:00',100),(1014,'Dundee','10:00','Portsmouth','12:00',100),(1015,'Edinburgh','18:30','Cardiff','20:00',75),(1016,'Southampton','12:00','Manchester','13:30',75),(1017,'Manchester','19:00','Southhampton','20:30',70),(1018,'Birmingham','16:00','Newcastle','17:30',75),(1019,'Newcastle','06:00','Birmingham','07:30',75),(1020,'Aberdeen','07:00','Portsmouth','09:00',75),(1027,'test1','12:00','test2','14:00',50),(1028,'test2','18:00','test1','20:00',60);
/*!40000 ALTER TABLE `journeys` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-05-01 23:36:28
