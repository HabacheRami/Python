/* delete database previously */
drop database if exists hospital;
/* create database */
create database if not exists hospital;

--
-- Table structure for table `patient`
--

CREATE TABLE hospital.patient (
  `id` int(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `firstname` varchar(100) NOT NULL,
  `date` date NOT NULL,
  `email` varchar(255) NOT NULL,
  `phone` varchar(30) NOT NULL,
  `address` varchar(255) NOT NULL,
  `city` varchar(100) NOT NULL,
  `postal` int(11) NOT NULL,
  `blood` varchar(5) NOT NULL,
  `doctor` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `report`
--

CREATE TABLE hospital.report (
  `id` int(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `description` text NOT NULL,
  `drug` text NOT NULL,
  `date` date NOT NULL,
  `userid` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `user`
--

CREATE TABLE hospital.user (
  `id` int(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `firstname` varchar(100) DEFAULT NULL,
  `email` varchar(255) NOT NULL,
  `phone` varchar(100) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `actived` tinyint(1) NOT NULL DEFAULT '1',
  `password` varchar(100) NOT NULL,
  `role` varchar(100) NOT NULL,
  `expire` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


INSERT INTO hospital.user (`id`, `username`, `name`, `firstname`, `email`, `phone`, `date`, `actived`, `password`, `role`, `expire`) VALUES
(1, 'Sadmin', 'Super', 'Admin', 'testmaileur111@gmail.com', '0662793686', '2003-02-28', 1, '8d9d244845a60033e2290d9a6146fde0', 'Supervisor', '2023-02-27');

