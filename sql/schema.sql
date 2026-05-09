DROP TABLE IF EXISTS relationships;
DROP TABLE IF EXISTS patents;
DROP TABLE IF EXISTS inventors;
DROP TABLE IF EXISTS companies;

CREATE TABLE patents (
    patent_id TEXT PRIMARY KEY,
    title TEXT,
    abstract TEXT,
    grant_date TEXT,
    grant_year INTEGER,
    filing_date TEXT,
    filing_year INTEGER
);

CREATE TABLE inventors (
    inventor_id TEXT PRIMARY KEY,
    name TEXT,
    country TEXT
);

CREATE TABLE companies (
    company_id TEXT PRIMARY KEY,
    name TEXT
);

CREATE TABLE relationships (
    patent_id TEXT,
    inventor_id TEXT,
    company_id TEXT,
    FOREIGN KEY(patent_id) REFERENCES patents(patent_id),
    FOREIGN KEY(inventor_id) REFERENCES inventors(inventor_id),
    FOREIGN KEY(company_id) REFERENCES companies(company_id)
);
