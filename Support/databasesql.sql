/* delete database previously */
drop database if exists hospital;
/* create database */
create database if not exists hospital;
/* create table patient : username (login) dossier (password) set by doctor*/
create table hospital.patient (
	id int(11) primary key,
    username varchar(100) unique not null,
    dossier int(11) not null,
    name varchar(100),
    firstname varchar(100),
    description text,
    drug text,
    date date
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/* create table user */
create table hospital.user (
	id int(11) primary key,
    username varchar(100) unique not null,
	name varchar(100),
    firstname varchar(100),
	email varchar(255) NOT NULL,
	phone varchar(100),
	date date,
	actived boolean NOT NULL DEFAULT 1,
	password varchar(100) NOT NULL,
	role varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
