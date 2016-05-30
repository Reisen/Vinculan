CREATE TABLE IF NOT EXISTS grouping (
	name TEXT,
	PRIMARY KEY(name)
);

CREATE TABLE IF NOT EXISTS page (
	path TEXT,
    parent TEXT,
	grouping TEXT,
	PRIMARY KEY(path),
    FOREIGN KEY(parent) REFERENCES page(path),
    FOREIGN KEY(grouping) REFERENCES grouping(name)
);

CREATE TABLE IF NOT EXISTS variable (
	path TEXT,
	name TEXT,
	value TEXT,
	PRIMARY KEY(path, name),
	FOREIGN KEY(path) REFERENCES page(path)
);
