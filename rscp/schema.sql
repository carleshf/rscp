USE mysql_rscp_main;

DROP TABLE IF EXISTS request;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS datatype;
DROP TABLE IF EXISTS method;
DROP TABLE IF EXISTS strain;
DROP TABLE IF EXISTS subject;
DROP TABLE IF EXISTS cline;
DROP TABLE IF EXISTS datafile;

CREATE TABLE IF NOT EXISTS user (
    id INT(21) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150),
    surname VARCHAR(300),
    institution VARCHAR(500),
    email VARCHAR(500),
    password VARCHAR(50),
    type VARCHAR(25)
) ENGINE=INNODB;


CREATE TABLE IF NOT EXISTS request (
    id INT(21) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    idUser INT(21),
    tag VARCHAR(25),
    validated BOOLEAN,
    registered BOOLEAN,
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    validated_date TIMESTAMP,
    registered_date TIMESTAMP,
    FOREIGN KEY (idUser) REFERENCES user(id) ON DELETE RESTRICT
) ENGINE=INNODB;


CREATE TABLE IF NOT EXISTS datatype (
    id INT(21) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    description VARCHAR(300)
)  ENGINE=INNODB;


CREATE TABLE IF NOT EXISTS method (
    id INT(21) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    description VARCHAR(300)
)  ENGINE=INNODB;


CREATE TABLE IF NOT EXISTS stratin (
    id INT(21) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    description VARCHAR(300)
)  ENGINE=INNODB;


CREATE TABLE IF NOT EXISTS subject (
    id INT(21) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    idStrain INT(21),
    description VARCHAR(300),
    sex VARCHAR(25),
    age INT,
    FOREIGN KEY (idStrain) REFERENCES strain(id) ON DELETE RESTRICT
)  ENGINE=INNODB;


CREATE TABLE IF NOT EXISTS cline (
    id INT(21) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    idMethod INT(21),
    idSubject INT(21),
    description VARCHAR(300),
    bank_status VARCHAR(300),
    growing  VARCHAR(1000),
    FOREIGN KEY (idMethod) REFERENCES method(id) ON DELETE RESTRICT,
    FOREIGN KEY (idSubject) REFERENCES subject(id) ON DELETE RESTRICT
)  ENGINE=INNODB;


CREATE TABLE IF NOT EXISTS datafile (
    id INT(21) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    idLine INT(21),
    idType INT(21),
    filepath VARCHAR(5000),
    displayname VARCHAR(500),
    passage INT,
    instrument VARCHAR(500),
    FOREIGN KEY (idLine) REFERENCES cline(id) ON DELETE RESTRICT,
    FOREIGN KEY (idType) REFERENCES datatype(id) ON DELETE RESTRICT
)  ENGINE=INNODB;  



INSERT INTO user (name, surname, institution, email, password, type) 
    VALUES("Carles", "Hernandez", "BCH", "carles@chip.edu", "[123Abc]", "Administrator");


INSERT INTO strain (description) VALUE("Sprague Dawley (SD)")
INSERT INTO strain (description) VALUE("Lewis (LEW/SsNHsd)")
INSERT INTO strain (description) VALUE("Long-Evans")
INSERT INTO strain (description) VALUE("F322")
INSERT INTO strain (description) VALUE("Immunodeficient athymic nude (Hsd:RH-Foxn1rnu ) rats")

INSERT INTO datatype (description) VALUE("WGS : 10X deep WGS for de novo assembly")
INSERT INTO datatype (description) VALUE("RNA-seq")
INSERT INTO datatype (description) VALUE("BS-seq")
INSERT INTO datatype (description) VALUE("MeDIP-seq")
INSERT INTO datatype (description) VALUE("multiple microscopic images")