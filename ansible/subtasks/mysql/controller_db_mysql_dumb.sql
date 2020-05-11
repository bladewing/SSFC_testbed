-- MySQL dump 10.13  Distrib 5.5.49, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: l7sdntest
-- ------------------------------------------------------
-- Server version	5.5.49-0+deb8u1

CREATE DATABASE l7sdntest;
USE l7sdntest;

--
-- Table structure for table `clients`
--

CREATE TABLE `clients` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ip` text NOT NULL,
  `port` int(11) NOT NULL,
  `priority` int(11) NOT NULL,
  `requested_ip` text NOT NULL,
  `requested_port` int(11) NOT NULL,
  `switch_to_ip` text,
  `switch_to_port` int(11) DEFAULT NULL,
  `switch_window` int(11) DEFAULT NULL,
  `first_time` int(11) DEFAULT NULL,
  `last_time` int(11) DEFAULT NULL,
  `first_signal` int(11) DEFAULT NULL,
  `last_signal` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=latin1;

--
-- Table structure for table `ressources`
--

DROP TABLE IF EXISTS `ressources`;
CREATE TABLE `ressources` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` text NOT NULL,
  `name` text,
  `parameter` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

--
-- Table structure for table `client_ressources`
--

DROP TABLE IF EXISTS `client_ressources`;
CREATE TABLE `client_ressources` (
  `client_id` int(11) NOT NULL,
  `ressource_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Table structure for table `servers`
--

DROP TABLE IF EXISTS `servers`;
CREATE TABLE `servers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ip` text NOT NULL,
  `port` int(11) NOT NULL,
  `max_connections` int(11) DEFAULT NULL,
  `current_connections` int(11) DEFAULT NULL,
  `load_type` text,
  `load_parameter` text,
  `load_value` double DEFAULT NULL,
  `first_time` int(11) NOT NULL,
  `last_time` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=latin1;

--
-- Table structure for table `server_ressources`
--

DROP TABLE IF EXISTS `server_ressources`;
CREATE TABLE `server_ressources` (
  `server_id` int(11) NOT NULL,
  `ressource_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

