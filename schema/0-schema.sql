CREATE DATABASE IF NOT EXISTS `vss365today` /*!40100 COLLATE 'utf8mb4_unicode_ci' */;
USE vss365today;

-- Create the tables
CREATE TABLE IF NOT EXISTS emails (
  email VARCHAR(150) NOT NULL UNIQUE,
  date_added DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(email)
)
COLLATE='utf8mb4_unicode_ci'
ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS writers (
  _id INT NOT NULL UNIQUE PRIMARY KEY AUTO_INCREMENT,
  uid VARCHAR(30) NOT NULL UNIQUE,
  handle VARCHAR(20) NOT NULL,
  PRIMARY KEY(uid)
)
COMMENT='Legacy table for storing Host infomation.'
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
COMMENT='Legacy table for storing hosting date infomation.'
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
COMMENT='Legacy table for storing prompts.'
COLLATE='utf8mb4_unicode_ci'
ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS api_keys (
  _id TINYINT(3) UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT UNIQUE,
  token VARCHAR(64) NOT NULL UNIQUE COLLATE 'utf8mb4_unicode_ci',
  date_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `desc` VARCHAR(256) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
  has_keys TINYINT(1) UNSIGNED NOT NULL DEFAULT '0',
  has_archive TINYINT(1) UNSIGNED NOT NULL DEFAULT '0',
  has_host TINYINT(1) UNSIGNED NOT NULL DEFAULT '0',
  has_notifications TINYINT(1) UNSIGNED NOT NULL DEFAULT '0',
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
  has_keys TINYINT(1) UNSIGNED NOT NULL DEFAULT '0',
  has_archive TINYINT(1) UNSIGNED NOT NULL DEFAULT '0',
  has_host TINYINT(1) UNSIGNED NOT NULL DEFAULT '0',
  has_notifications  TINYINT(1) UNSIGNED NOT NULL DEFAULT '0',
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


-- 2023+ tables
CREATE TABLE IF NOT EXISTS `hosts` (
  `_id` BIGINT NOT NULL AUTO_INCREMENT,
  `handle` VARCHAR(30) NOT NULL UNIQUE,
  `twitter_uid` VARCHAR(40) NOT NULL UNIQUE,
  PRIMARY KEY(`_id`)
)
COLLATE='utf8mb4_unicode_ci'
COMMENT='Store the #vss365 Hosts.'
ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `host_dates` (
  `_id` BIGINT NOT NULL AUTO_INCREMENT,
  `host_id` BIGINT NOT NULL,
  `date` DATE NOT NULL,
  PRIMARY KEY (`_id`),
  INDEX `host_id-host_dates_host_id` (`host_id`),
  CONSTRAINT `host_id-host_dates_host_id`
    FOREIGN KEY (`host_id`) REFERENCES `hosts` (`_id`)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
)
COMMENT='Store the hosting dates of #vss365 Hosts.'
COLLATE='utf8mb4_unicode_ci'
ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `prompts_new` (
  `_id` BIGINT NOT NULL AUTO_INCREMENT,
  `twitter_id` VARCHAR(30) NOT NULL UNIQUE,
  `date` DATE NOT NULL,
  `date_added` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `word` VARCHAR(30) NOT NULL,
  `content` VARCHAR(2048) NOT NULL,
  `host_id` BIGINT NOT NULL,
  PRIMARY KEY (`_id`),
  INDEX `host_id-prompts_host_id` (`host_id`),
  CONSTRAINT `host_id-prompts_host_id`
    FOREIGN KEY (`host_id`) REFERENCES `hosts` (`_id`)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
)
COMMENT='Store the #vss365 Prompts.'
COLLATE='utf8mb4_unicode_ci'
ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `prompt_media` (
  `_id` BIGINT NOT NULL AUTO_INCREMENT,
  `media` VARCHAR(512),
  `alt_text` VARCHAR(1000),
  `prompt_id` BIGINT NOT NULL,
  PRIMARY KEY (`_id`),
  INDEX `prompt_media_id-prompts_id` (`prompt_id`),
  CONSTRAINT `prompt_media_id-prompts_id`
    FOREIGN KEY (`prompt_id`) REFERENCES `prompts_new` (`_id`)
    ON UPDATE CASCADE
    ON DELETE CASCADE
)
COMMENT='Store the #vss365 Prompt media.'
COLLATE='utf8mb4_unicode_ci'
ENGINE=InnoDB;
