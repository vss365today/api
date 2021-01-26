DELIMITER $$
CREATE TRIGGER api_key_permission_changes
AFTER UPDATE
ON api_keys FOR EACH ROW
BEGIN
     INSERT INTO audit_api_keys(key_id, has_api_key, has_archive, has_broadcast, has_host, has_prompt, has_settings, has_subscription)
     VALUES (old._id, old.has_api_key, old.has_archive, old.has_broadcast, old.has_host, old.has_prompt, old.has_settings, old.has_subscription);
END$$
DELIMITER ;
