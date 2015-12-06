CREATE TABLE media(
  user_id bigint PRIMARY KEY NOT NULL,
  raw_text TEXT NOT NULL,
  username VARCHAR(50) NOT NULL,
  n_media INT NOT NULL
);

CREATE TABLE liked_media(
  media_id VARCHAR(255) PRIMARY KEY NOT NULL,
  user_id bigint NOT NULL
);
