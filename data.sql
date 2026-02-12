DROP DATABASE IF EXISTS date_night;
CREATE DATABASE date_night;
\connect date_night

DROP TYPE IF EXISTS category_list;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS date_ideas CASCADE;
DROP TABLE IF EXISTS completed_dates CASCADE;

CREATE TYPE category_list AS ENUM ('free', 'cheap', 'affordable', 'expensive');

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);


CREATE TABLE date_ideas (
    id SERIAL PRIMARY KEY,
    author INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category category_list NOT NULL
);

CREATE TABLE completed_dates (
    id SERIAL PRIMARY KEY,
    author INTEGER REFERENCES users(id) ON DELETE CASCADE,
    idea  INTEGER REFERENCES date_ideas(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    date TIMESTAMP,
    image_url TEXT
);

