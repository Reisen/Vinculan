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
    PRIMARY KEY(name, domain),
    FOREIGN KEY(domain) REFERENCES page(domain)
);

CREATE TABLE IF NOT EXISTS pageval (
    domain TEXT,
    page TEXT,
    variable TEXT,
    value TEXT,
    PRIMARY KEY(domain, page, variable),
    FOREIGN KEY(domain) REFERENCES domain(id),
    FOREIGN KEY(variable) REFERENCES pagevar(id)
);