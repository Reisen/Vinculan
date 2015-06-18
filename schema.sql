CREATE TABLE variable (
    id INTEGER PRIMARY KEY,
    name TEXT
);

CREATE TABLE domain (
    id INTEGER PRIMARY KEY,
    host TEXT
);

CREATE TABLE value (
    id INTEGER PRIMARY KEY,
    domain INTEGER,
    variable INTEGER,
    value TEXT,
    FOREIGN KEY(domain) REFERENCES domain(id),
    FOREIGN KEY(variable) REFERENCES variabe(id)
);
