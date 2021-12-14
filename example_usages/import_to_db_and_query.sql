DROP DATABASE IF EXISTS DASEA;
CREATE DATABASE DASEA;

CREATE TABLE IF NOT EXISTS Package (
	ID serial PRIMARY KEY,
	Name VARCHAR UNIQUE NOT NULL,
	PackageManager VARCHAR
);

COPY Package
FROM '/path/to/data/packageManger/packages.csv' DELIMITER ',' CSV HEADER;

CREATE TABLE IF NOT EXISTS Version (
	ID serial PRIMARY KEY,
	PackageID INT,
	Version VARCHAR,
	Description VARCHAR,
	HomepageURL VARCHAR,
	SourcecodeURL VARCHAR,
	Maintainer VARCHAR,
	License VARCHAR,
	Author VARCHAR,
	FOREIGN KEY (PackageID) REFERENCES package (ID)
);

COPY Version FROM '/path/to/data/packageManger/versions.csv' DELIMITER ',' CSV HEADER;

CREATE TABLE IF NOT EXISTS Dependency (
	ID serial PRIMARY KEY,
	SourceID INT,
	TargetID INT,
	Constraints VARCHAR,
	type VARCHAR,
	FOREIGN KEY (SourceID) REFERENCES Version (ID),
	FOREIGN KEY (TargetID) REFERENCES Package (ID)
);

COPY Dependency FROM '/path/to/data/packageManger/dependencies.csv' DELIMITER ',' CSV HEADER;

/* Find the package most packages depend on */
SELECT Package.Name,
COUNT(TargetID) AS dependenciesCount
FROM Dependency
INNER JOIN Package ON Package.ID=Dependency.TargetID
GROUP BY Package.Name ORDER BY dependenciesCount DESC;
