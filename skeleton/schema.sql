CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;
DROP TABLE IF EXISTS Pictures CASCADE;
DROP TABLE IF EXISTS Users CASCADE;

CREATE TABLE Users (
    user_id int4  AUTO_INCREMENT,
    email varchar(255) UNIQUE,
    password varchar(255),
    first_name varchar(255),
    last_name varchar(255),
    hometown varchar(255),
    gender varchar(255),
    score int4 DEFAULT 0,
  CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE Pictures
(
  picture_id int4  AUTO_INCREMENT,
  user_id int4,
  imgdata longblob ,
  caption VARCHAR(255),
  numLike int4 DEFAULT 0,
  album_id int4,
  INDEX upid_idx (user_id),
  FOREIGN KEY (album_id) references Albums(album_id) ON DELETE CASCADE,
  CONSTRAINT pictures_pk PRIMARY KEY (picture_id)
);

CREATE TABLE Albums
(
  album_id int4  AUTO_INCREMENT,
  user_id int4,
  album_name VARCHAR(255),
  album_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT album_pk PRIMARY KEY (album_id),
  FOREIGN KEY (user_id) references Users(user_id)
);

CREATE TABLE comment
(
  comment_id int4 AUTO_INCREMENT primary key,
  u_id int4,
  p_id int4,
  text VARCHAR(255),
  date DATETIME,
  FOREIGN KEY (u_id) REFERENCES Users(user_id),  
  FOREIGN KEY (p_id) REFERENCES Pictures(picture_id)
);

CREATE TABLE Friends
(
   u_id int ,
   f_id int ,
   FOREIGN KEY (u_id) REFERENCES Users(user_id),
   FOREIGN KEY (f_id) REFERENCES Users(user_id)
);

CREATE TABLE Tags(
    tag_id int4 AUTO_INCREMENT PRIMARY Key,
    tag_text VARCHAR(255)
);

CREATE TABLE tagged(
    tag_id int4,
    picture_id int4,
    FOREIGN KEY (tag_id) references Tags(tag_id),
    FOREIGN KEY (picture_id) references Pictures(picture_id)
);

-- SELECT imgdata, picture_id, caption, numLike from pictures where picture_id in(select picture_id as picture_id from (SELECT Tagged.tag_id, Tagged.picture_id, Tags.tag_text FROM Tagged INNER JOIN Tags ON tagged.tag_id = Tags.tag_id) as p where tag_text like '%test%';
-- SELECT tag_text, COUNT(tag_text) as cnt FROM (SELECT Tagged.tag_id , Tagged.picture_id, Tags.tag_text as tag_text FROM Tagged INNER JOIN Tags ON tagged.tag_id = Tags.tag_id) as a
-- GROUP BY tag_text
-- HAVING COUNT(tag_text) > 1;

SELECT Tags.tag_id, Tags.tag_text FROM tagged, Pictures, Tags WHERE
Pictures.user_id = "1" AND tagged.picture_id = Pictures.picture_id
AND tagged.tag_id = Tags.tag_id;


INSERT INTO Users (email, password) VALUES ('test@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test2@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test3@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test4@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test5@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test6@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test7@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test8@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test9@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test10@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test11@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test12@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test13@bu.edu', 'test');
