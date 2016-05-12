CREATE TABLE IF NOT EXISTS grouping (
	name TEXT,
	PRIMARY KEY(name)
);

CREATE TABLE IF NOT EXISTS page (
	grouping TEXT,
	path TEXT,
	PRIMARY KEY(grouping, path)
);

CREATE TABLE IF NOT EXISTS variable (
	grouping TEXT,
	path TEXT,
	name TEXT,
	value TEXT,
	PRIMARY KEY(grouping, path, name),
	FOREIGN KEY(grouping, path) REFERENCES page(grouping, path)
);
