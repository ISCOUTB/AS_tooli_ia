CREATE USER IF NOT EXISTS 'sso_user'@'%' IDENTIFIED BY 'Sso123Secure!';
GRANT ALL PRIVILEGES ON glpi_sso.* TO 'sso_user'@'%';
FLUSH PRIVILEGES;
SELECT User, Host FROM mysql.user WHERE User='sso_user';
