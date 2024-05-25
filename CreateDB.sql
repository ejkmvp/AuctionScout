CREATE SCHEMA `auctionscanner` ;

CREATE USER auctionscanner@localhost IDENTIFIED BY 'auctionpassword';

USE auctionscanner;

GRANT DELETE, EXECUTE, INSERT, SELECT, SHOW VIEW, UPDATE ON auctionscanner.* TO auctionscanner@localhost;

CREATE TABLE `auctionscanner`.`auctionitems` (
  `auctionId` VARCHAR(45) NOT NULL,
  `sellPrice` INT NOT NULL,
  `timeSold` DATETIME NOT NULL,
  `itemName` VARCHAR(45) NOT NULL,
  `enchantmentName` VARCHAR(45) NULL,
  `enchantmentLevel` INT NULL,
  `petName` VARCHAR(45) NULL,
  `petRarity` VARCHAR(45) NULL,
  PRIMARY KEY (`auctionId`));
