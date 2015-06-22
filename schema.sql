CREATE TABLE IF NOT EXISTS variable (
    id INTEGER PRIMARY KEY,
    name TEXT
);

CREATE TABLE IF NOT EXISTS domain (
    id INTEGER PRIMARY KEY,
    host TEXT
);

CREATE TABLE IF NOT EXISTS value (
    id INTEGER PRIMARY KEY,
    domain INTEGER,
    variable INTEGER,
    value TEXT,
    UNIQUE(domain, variable),
    FOREIGN KEY(domain) REFERENCES domain(id),
    FOREIGN KEY(variable) REFERENCES variabe(id)
);
