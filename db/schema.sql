CREATE DATABASE `vss365today` /*!40100 COLLATE 'utf8mb4_unicode_ci' */;
USE vss365today;

-- Create the tables
CREATE TABLE IF NOT EXISTS users (
  id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT UNIQUE,
  username VARCHAR(20) NOT NULL UNIQUE,
  password VARCHAR(128) NOT NULL,
  date_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_signin DATETIME NULL,
  token VARCHAR(64) NOT NULL UNIQUE
)
COLLATE='utf8mb4_unicode_ci'
ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS emails (
  email VARCHAR(50) NOT NULL UNIQUE,
  PRIMARY KEY(email)
)
COLLATE='utf8mb4_unicode_ci'
ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS writers (
  uid VARCHAR(30) NOT NULL UNIQUE,
  handle VARCHAR(20) NOT NULL,
  PRIMARY KEY(uid)
)
COLLATE='utf8mb4_unicode_ci'
ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS writer_dates (
  uid VARCHAR(30) NOT NULL,
  `date` DATE NOT NULL,
  PRIMARY KEY(uid,date),
  CONSTRAINT `writer_uid-writer_dates_uid`
    FOREIGN KEY (uid) REFERENCES writers (uid)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
)
COLLATE='utf8mb4_unicode_ci'
ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tweets (
  tweet_id VARCHAR(25) NOT NULL UNIQUE,
  date DATE NOT NULL,
  uid VARCHAR(30) NOT NULL,
  content VARCHAR(512) NOT NULL,
  word VARCHAR(30) NOT NULL,
  media VARCHAR(512),
  PRIMARY KEY(tweet_id),
  CONSTRAINT `writer_uid-tweets_uid`
    FOREIGN KEY (uid) REFERENCES writers (uid)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
)
COLLATE='utf8mb4_unicode_ci'
ENGINE=InnoDB;
