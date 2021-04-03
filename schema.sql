CREATE TABLE albums (
  id SERIAL PRIMARY KEY,
  album_name TEXT,
  artist_id INTEGER,
  album_genre_id INTEGER,
  num_of_songs INTEGER,
);

CREATE TABLE songs (
  id SERIAL PRIMARY KEY,
  album_id INTEGER,
  song_name TEXT,
  song_length_seconds INTEGER
);

CREATE TABLE genres (
  id SERIAL PRIMARY KEY,
  genre_name TEXT
);

CREATE TABLE artists (
  id SERIAL PRIMARY KEY,
  artist_name TEXT
);

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  user_name TEXT,
  user_password TEXT,
  user_role INTEGER
);

CREATE TABLE reviews (
  id SERIAL PRIMARY KEY,
  user_id INTEGER,
  album_id INTEGER,
  content TEXT
);
