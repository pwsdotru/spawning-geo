
DROP TABLE IF EXISTS `regions`;

CREATE TABLE IF NOT EXISTS `regions` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `title` VARCHAR(255),
    PRIMARY KEY(`id`)
);

DROP TABLE IF EXISTS  `areas`;

CREATE TABLE IF NOT EXISTS `areas` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `region_id` INT(11) NOT NULL,
    `title` VARCHAR(255),
    `original_text` VARCHAR (255),
    PRIMARY KEY(`id`)
);

DROP TABLE IF EXISTS  `points`;

CREATE TABLE IF NOT EXISTS `points` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `area_id` INT(11) NOT NULL,
    `original_text` VARCHAR (255),
    `lat_text` VARCHAR(128),
    `lng_text` VARCHAR(128),
    `lat` DECIMAL (11, 8) NOT NULL,
    `lng` DECIMAL (11, 8) NOT NULL,
    PRIMARY KEY(`id`)
);