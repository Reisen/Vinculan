CREATE TABLE IF NOT EXISTS variable (
    name TEXT,
    PRIMARY KEY(name)
);

CREATE TABLE IF NOT EXISTS domain (
    host TEXT,
    template TEXT,
    PRIMARY KEY(host)
);

CREATE TABLE IF NOT EXISTS value (
    domain TEXT,
    variable TEXT,
    value TEXT,
    PRIMARY KEY(domain, variable),
    FOREIGN KEY(domain) REFERENCES domain(id),
    FOREIGN KEY(variable) REFERENCES variabe(id)
);

CREATE TABLE IF NOT EXISTS page (
    domain TEXT,
    page TEXT,
    variable TEXT,
    value TEXT,
    PRIMARY KEY(domain, page, variable),
    FOREIGN KEY(domain) REFERENCES domain(id)
);