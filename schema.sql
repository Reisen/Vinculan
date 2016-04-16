CREATE TABLE IF NOT EXISTS domain (
    host TEXT,
    template TEXT,
    PRIMARY KEY(host)
);

CREATE TABLE IF NOT EXISTS variable (
    name TEXT,
    PRIMARY KEY(name)
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
    PRIMARY KEY(domain, page),
    FOREIGN KEY(domain) REFERENCES domain(id)
);

CREATE TABLE IF NOT EXISTS pagevar (
    name TEXT,
    domain TEXT,
    page TEXT,
    PRIMARY KEY(name, domain, page),
    FOREIGN KEY(domain, page) REFERENCES page(domain, page)
);

CREATE TABLE IF NOT EXISTS pageval (
);