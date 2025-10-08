-- Create a database with:
-- sqlite3 my_database.db

CREATE TABLE students (
	name text,
	id text primary key,
	marks int
);

CREATE TABLE grades (
	id text primary key,
	grade char
);

CREATE TABLE grocery (
	id text primary key,
	name text,
	count int
);
