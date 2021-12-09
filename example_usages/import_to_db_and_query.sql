DROP DATABASE IF EXISTS DASEA;
CREATE DATABASE DASEA;

CREATE TABLE IF NOT EXISTS package (
	id serial PRIMARY KEY,
	name VARCHAR(50) UNIQUE NOT NULL
);

COPY packages FROM '/path/to/csv/packages.csv' DELIMITER ',' CSV HEADER;

CREATE TABLE IF NOT EXISTS version (
	id serial PRIMARY KEY,
	package_id INT,
	version VARCHAR,
	package_manager VARCHAR,
	description VARCHAR,
	homepage_url VARCHAR,
	source_code_url VARCHAR,
	maintainer VARCHAR,
	license VARCHAR,
	author VARCHAR,
	FOREIGN KEY (package_id) REFERENCES package (id)
);

COPY packages FROM '/path/to/csv/versions.csv' DELIMITER ',' CSV HEADER;

CREATE TABLE IF NOT EXISTS dependency (
	id serial PRIMARY KEY,
	source_id INT,
	target_id INT,
	constraints VARCHAR,
	FOREIGN KEY (source_id) REFERENCES version (id),
	FOREIGN KEY (target_id) REFERENCES package (id)
);

COPY packages FROM '/path/to/csv/dependencies.csv' DELIMITER ',' CSV HEADER;


/* Find the package most packages depend on */

SELECT package.name,
COUNT(target_id) AS dependencies_count
FROM dependency
INNER JOIN package ON package.id=dependency.target_id
GROUP BY package.name ORDER BY dependencies_count DESC;
