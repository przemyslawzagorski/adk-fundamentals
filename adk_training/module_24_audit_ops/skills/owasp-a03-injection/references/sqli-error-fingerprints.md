# SQL engine error fingerprints (case-insensitive substrings)

The bundled `expect_no_sql_error` action lower-cases the response and matches
these. Do not invent your own — false positives kill report credibility.

- `you have an error in your sql syntax`         (MySQL / MariaDB)
- `unclosed quotation mark after the character`  (MS SQL Server)
- `quoted string not properly terminated`        (Oracle)
- `pg_query()`                                    (PostgreSQL with PHP)
- `sqlite3.operationalerror`                      (SQLite)
- `odbc sql server driver`                        (ODBC / MSSQL)
- `microsoft odbc oracle driver`                  (ODBC / Oracle)

## When to trust the signal

A match means the SQL engine surfaced an error to the response body. That is
a configuration finding (verbose errors enabled) and an *injection signal*.
It does **not** prove the input is exploitable. Severity: `medium`.

## When to ignore the signal

Plain `error` or `exception` in body — too generic, lots of false positives.
Stick to the list above.
