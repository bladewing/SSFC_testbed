DROP TABLE IF EXISTS `servers`;
DROP TABLE IF EXISTS `ressources`;
DROP TABLE IF EXISTS `clients`;
DROP TABLE IF EXISTS `server_ressources`;
DROP TABLE IF EXISTS `client_ressources`;

CREATE TABLE servers (
	id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
	ip TEXT NOT NULL,
	port INTEGER NOT NULL,
	max_connections INTEGER,
	current_connections INTEGER,
	load_type TEXT,
	load_parameter TEXT,
	load_value REAL,
	first_time INTEGER NOT NULL,
	last_time INTEGER NOT NULL
);

CREATE TABLE ressources (
	id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
	type TEXT NOT NULL,
	name TEXT,
	parameter INT NOT NULL
);

CREATE TABLE clients (
	id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
	ip TEXT NOT NULL,
	port INTEGER NOT NULL,
	priority INTEGER NOT NULL,
	requested_ip TEXT NOT NULL,
	requested_port INTEGER NOT NULL,
	switch_to_ip TEXT,
	switch_to_port INTEGER,
	switch_window INTEGER,
	first_time INTEGER,
	last_time INTEGER,
	first_signal INTEGER,
	last_signal INTEGER
);

CREATE TABLE server_ressources (
	server_id INTEGER NOT NULL,
	ressource_id INTEGER NOT NULL
);

CREATE TABLE client_ressources (
	client_id INTEGER NOT NULL,
	ressource_id INTEGER NOT NULL
);
