CREATE TABLE artists (
  id SERIAL PRIMARY KEY,
  artist_name TEXT UNIQUE
);

CREATE TABLE genres (
  id SERIAL PRIMARY KEY,
  genre_name TEXT
);

CREATE TABLE albums (
  id SERIAL PRIMARY KEY,
  album_name TEXT,
  artist_id INTEGER REFERENCES artists ON DELETE CASCADE,
  album_genre_id INTEGER REFERENCES genres ON DELETE CASCADE
);

CREATE TABLE songs (
  id SERIAL PRIMARY KEY,
  album_id INTEGER REFERENCES albums ON DELETE CASCADE,
  song_name TEXT,
  song_length_seconds INTEGER
);

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR (50) UNIQUE,
  user_password TEXT,
  user_role INTEGER
);

CREATE TABLE reviews (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users ON DELETE CASCADE,
  album_id INTEGER REFERENCES albums ON DELETE CASCADE,
  review_date DATE NOT NULL,
  content TEXT
);

CREATE TABLE ratings (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users ON DELETE CASCADE,
  album_id INTEGER REFERENCES albums ON DELETE CASCADE,
  rating INTEGER
);
