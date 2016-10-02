CREATE TABLE tweets(
  user_id bigint PRIMARY KEY NOT NULL,
  raw_text TEXT NOT NULL,
  screen_name VARCHAR(255) NOT NULL,
  lang VARCHAR(50) NOT NULL,
  n_tweets INT NOT NULL
);

CREATE TABLE followers(
  id VARCHAR(255) PRIMARY KEY NOT NULL
);
