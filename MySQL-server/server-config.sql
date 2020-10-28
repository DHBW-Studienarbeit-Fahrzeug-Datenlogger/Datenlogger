-- MySQL Script generated by MySQL Workbench
-- Sun Nov  4 13:50:41 2018
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema obd/gps-datenlogger
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `obd/gps-datenlogger`;
USE `obd/gps-datenlogger` ;

-- -----------------------------------------------------
-- Table `obd/gps-datenlogger`.`data`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `obd/gps-datenlogger`.`data` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `filename` VARCHAR(180) NULL DEFAULT NULL,
  `date` VARCHAR(45) NULL DEFAULT NULL,
  `starttime` VARCHAR(45) NULL DEFAULT NULL,
  `totalKM` FLOAT NULL DEFAULT NULL,
  `endtime` VARCHAR(45) NULL DEFAULT NULL,
  `VIN` VARCHAR(20) NULL DEFAULT NULL,
  `fuelConsumption` FLOAT NULL DEFAULT NULL,
  `energyConsumption` FLOAT NULL DEFAULT NULL,
  `endLat` FLOAT NULL DEFAULT NULL,
  `endLong` FLOAT NULL DEFAULT NULL,
  `endDate` VARCHAR(45) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `filename_UNIQUE` (`filename` ASC)
);

-- -----------------------------------------------------
-- Table `obd/gps-datenlogger`.`sessions`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `obd/gps-datenlogger`.`sessions` (
  `session_id` VARCHAR(128) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_bin' NOT NULL,
  `expires` INT(11) UNSIGNED NOT NULL,
  `data` TEXT CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_bin' NULL DEFAULT NULL,
  PRIMARY KEY (`session_id`)
);

-- -----------------------------------------------------
-- Table `obd/gps-datenlogger`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `obd/gps-datenlogger`.`users` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(20) NULL DEFAULT NULL,
  `email` VARCHAR(100) NULL DEFAULT NULL,
  `password` BINARY(60) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC)
);

-- -----------------------------------------------------
-- Table `obd/gps-datenlogger`.`cars`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `obd/gps-datenlogger`.`cars` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `type` VARCHAR(20) NULL DEFAULT NULL,
  `consumption` FLOAT NULL DEFAULT NULL,
  `capacity` FLOAT NULL DEFAULT NULL,
  `power` FLOAT NULL DEFAULT NULL,
  `name` VARCHAR(45) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `name_UNIQUE` (`name` ASC)
);

INSERT INTO `cars` VALUES (1,'micro',18.3,17.6,60,'Smart ForTwo Coupe Prime'),(2,'micro',13.7,19,60,'VW E-UP'),(3,'mini',17.3,24.2,85,'VW E-Golf'),(4,'mini',17.4,37.9,125,'BMW i3'),(5,'mini',14.7,28,88,'Hyundai IONIQ Elektro Style'),(6,'mini',19.5,39.2,100,'Hyundai Kona Elektro Small'),(7,'mini',21.3,40,110,'Nissan Leaf Acenta'),(8,'mini',19.7,60,150,'Opel Ampera-E'),(9,'mini',20.3,41,48,'Renault Zoe'),(10,'mini',19.1,27,81,'KIA Soul EV'),(11,'mini',22.6,33.5,107,'Ford Focus Electric'),(12,'mini',19.5,68,150,'Hyundai Kona Elektro Large'),(13,'van',28.1,40,80,'Nissan e-NV200 Evalia'),(14,'van',22.8,40,80,'Nissan e-NV200 Kombi Premium'),(15,'van',23.2,33,44,'Renault Kangoo Z.E.'),(16,'medium',15,75,211,'Tesla Model 3 Long-Range'),(17,'medium',16,75,340,'Tesla Model 3 Long-Range Dual-Motor');