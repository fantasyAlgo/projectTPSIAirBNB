
/*
CREATE TABLE IF NOT EXISTS Appartments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    price TEXT,
    link_img TEXT,
    description TEXT
)
*/

/*
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(255),
    email VARCHAR(255),
    password VARCHAR(255)
);
*/

CREATE TABLE IF NOT EXISTS Renting (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  appartment_id INTEGER NOT NULL,
  checkin DATE NOT NULL,
  checkout DATE NOT NULL,
  NPeople INTEGER NOT NULL,
  FOREIGN KEY(user_id) REFERENCES Users(id),
  FOREIGN KEY(appartment_id) REFERENCES Users(appartment_id)
)
