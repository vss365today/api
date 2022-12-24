CREATE DATABASE IF NOT EXISTS `vss365today` /*!40100 COLLATE 'utf8mb4_unicode_ci' */;
USE vss365today;

-- Create the tables
CREATE TABLE IF NOT EXISTS users (
  _id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT UNIQUE,
  username VARCHAR(20) NOT NULL UNIQUE,
  password VARCHAR(128) NOT NULL,
  date_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_signin DATETIME NULL
)
COLLATE='utf8mb4_unicode_ci'
ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS emails (
  email VARCHAR(150) NOT NULL UNIQUE,
  date_added DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
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
    ON DELETE CASCADE
)
COLLATE='utf8mb4_unicode_ci'
ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS prompts (
  tweet_id VARCHAR(25) NOT NULL UNIQUE,
  date DATE NOT NULL,
  uid VARCHAR(30) NOT NULL,
  content VARCHAR(2048) NOT NULL,
  word VARCHAR(30) NOT NULL,
  media VARCHAR(512),
  media_alt_text VARCHAR(1000),
  date_added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY(tweet_id),
  CONSTRAINT `writer_uid-prompts_uid`
    FOREIGN KEY (uid) REFERENCES writers (uid)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
)
COLLATE='utf8mb4_unicode_ci'
ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS api_keys (
  _id TINYINT(3) UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT UNIQUE,
  token VARCHAR(64) NOT NULL UNIQUE COLLATE 'utf8mb4_unicode_ci',
  date_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `desc` VARCHAR(256) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
  has_api_key TINYINT(1) UNSIGNED NOT NULL DEFAULT '0',
  has_archive TINYINT(1) UNSIGNED NOT NULL DEFAULT '0',
  has_broadcast TINYINT(1) UNSIGNED NOT NULL DEFAULT '0',
  has_host TINYINT(1) UNSIGNED NOT NULL DEFAULT '0',
  has_prompt TINYINT(1) UNSIGNED NOT NULL DEFAULT '0',
  has_settings TINYINT(1) UNSIGNED NOT NULL DEFAULT '0',
  has_subscription TINYINT(1) UNSIGNED NOT NULL DEFAULT '0'
)
COMMENT='API keys for accessing protected API endpoints. By default, keys can only access public, unprotected endpoints and actions. Authorization can be granted on a granular level for complete control over key permissions.',
COLLATE='utf8mb4_unicode_ci'
ENGINE=InnoDB;

CREATE TABLE audit_api_keys (
  _id TINYINT(3) UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
  key_id TINYINT(3) UNSIGNED NOT NULL,
  date_updated DATETIME NOT NULL DEFAULT current_timestamp(),
  has_api_key TINYINT(1) UNSIGNED NOT NULL DEFAULT '0',
  has_archive TINYINT(1) UNSIGNED NOT NULL DEFAULT '0',
  has_broadcast  TINYINT(1) UNSIGNED NOT NULL DEFAULT '0',
  has_host TINYINT(1) UNSIGNED NOT NULL DEFAULT '0',
  has_prompt TINYINT(1) UNSIGNED NOT NULL DEFAULT '0',
  has_settings TINYINT(1) UNSIGNED NOT NULL DEFAULT '0',
  has_subscription TINYINT(1) UNSIGNED NOT NULL DEFAULT '0',
  CONSTRAINT `audit_api_keys_key_id-api_keys_id`
    FOREIGN KEY (key_id) REFERENCES api_keys (_id)
    ON UPDATE NO ACTION
    ON DELETE CASCADE
)
COMMENT='Audit table to track permission changes to API keys.'
COLLATE='utf8mb4_unicode_ci'
ENGINE=InnoDB;
